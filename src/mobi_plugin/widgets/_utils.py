class LayerUtils:
    @staticmethod
    def connect_signals(widget):
        """
        Connect signals for layer updates.
        """
        widget.viewer.layers.events.inserted.connect(lambda event: LayerUtils.update_layer_selections(widget, event))
        widget.viewer.layers.events.removed.connect(lambda event: LayerUtils.update_layer_selections(widget, event))
        widget.viewer.layers.events.changed.connect(lambda event: LayerUtils.update_layer_selections(widget, event))
        widget.viewer.layers.events.reordered.connect(lambda event: LayerUtils.update_layer_selections(widget, event))

    @staticmethod
    def update_layer_selections(widget, event=None):
        """
        Update the QComboBox selections with the list of layers.
        """
        layers = [layer.name for layer in widget.viewer.layers]
        for combobox in [widget.reference_selection, widget.sample_selection]:
            combobox.clear()
            combobox.addItems(layers)

        if hasattr(widget, 'darkfield_checkbox') and widget.darkfield_checkbox.isChecked() and widget.darkfield_selection:
            widget.darkfield_selection.clear()
            widget.darkfield_selection.addItems(layers)
        
        if hasattr(widget, 'flatfield_checkbox') and widget.flatfield_checkbox.isChecked() and widget.flatfield_selection:
            widget.flatfield_selection.clear()
            widget.flatfield_selection.addItems(layers)


class Experiment:
    def __init__(self, sample_images, reference_images, nb_of_point, max_shift, pixel, dist_object_detector, dist_source_object, LCS_median_filter):
        self.sample_images = sample_images
        self.reference_images = reference_images
        self.nb_of_point = nb_of_point
        self.max_shift = max_shift
        self.pixel = pixel
        self.dist_object_detector = dist_object_detector
        self.dist_source_object = dist_source_object
        self.LCS_median_filter = LCS_median_filter

    def getk(self):
        # Placeholder for the actual implementation of getk
        return 1.0

class Parameters:
    def __init__(self, method="lcs"):  # Default method to "lcs"
        self.method = method
        self.alpha = None
        self.weak_absorption = None
        self.window_size = None
        self.pixel_shift = None
        self.max_shift = None
        self.pixel = None
        self.dist_object_detector = None
        self.dist_source_object = None
        self.LCS_median_filter = None
        self.phase_parameters = None  # New attribute for phase parameters
        print(f"Initialized Parameters with method: {self.method}")

    def update(self, widget):
        """
        Update the parameters based on the widget values.
        """
        print(f"Updating Parameters for method: {self.method}")
        try:
            if self.method == "lcs" or self.method == "lcs_df":
                self.alpha = float(widget.alpha_input.text())
                self.weak_absorption = widget.weak_absorption_checkbox.isChecked()
            elif self.method == "cst_csvt":
                self.window_size = widget.window_size_input.text()
                self.pixel_shift = widget.pixel_shift_input.text()
            elif self.method == "lcs_dirdf":
                if widget.max_shift_input.text():
                    self.max_shift = int(widget.max_shift_input.text())
                if widget.pixel_input.text():
                    self.pixel = float(widget.pixel_input.text())
                if widget.dist_object_detector_input.text():
                    self.dist_object_detector = float(widget.dist_object_detector_input.text())
                if widget.dist_source_object_input.text():
                    self.dist_source_object = float(widget.dist_source_object_input.text())
                if widget.LCS_median_filter_input.text():
                    self.LCS_median_filter = int(widget.LCS_median_filter_input.text())
            if widget.phase_retrieval_checkbox.isChecked():
                self.phase_parameters = {
                    'method': widget.phase_retrieval_selection.currentText(),
                    'pad': widget.pad_checkbox.isChecked()
                }
            else:
                self.phase_parameters = None
        except ValueError as e:
            print(f"Error updating parameters: {e}")
        print(f"Updated Parameters: {self.__dict__}")
