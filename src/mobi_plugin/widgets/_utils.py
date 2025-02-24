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
    def __init__(self, method): 
        self.method = method
        # Initialize the parameters based on the method

        self.sample_images = None
        self.reference_images = None
        self.darkfield = None
        self.flatfield = None

        if self.method == "lcs":
            self.alpha = None
            self.weak_absorption = False 

        elif self.method == "lcs_df":
            self.nb_of_point = None
            self.max_shift = None
            self.pixel = None
            self.dist_object_detector = None
            self.dist_source_object = None
            self.LCS_median_filter = None

        elif self.method == "lcs_dirdf":
            self.nb_of_point = None
            self.max_shift = None
            self.pixel = None
            self.dist_object_detector = None
            self.dist_source_object = None
            self.LCS_median_filter = None

        elif self.method == "misti":
            self.pixel = None
            self.dist_object_detector = None
            self.beta = None
            self.delta = None
            self.energy = None
            self.MIST_median_filter = None
            self.sigma_regularization = None

        self.phase_parameters = None

        print(f"Initialized Parameters with method: {self.method}")

    def getk(self):
        # Placeholder for the actual implementation of getk
        return 1.0

    def convert_names_to_data(self, widget):
        """
        Convert layer names to actual data.
        """
        

    def update_parameters(self, widget):
        """
        Update the parameters based on the widget values.
        """
        print(f"Updating Parameters for method: {self.method}")
        try:
            self.sample_images = widget.sample_selection.currentText()
            self.reference_images = widget.reference_selection.currentText()

            if widget.darkfield_checkbox.isChecked():
                self.darkfield = widget.darkfield_selection.currentText()
            else:
                self.darkfield = None

            if widget.flatfield_checkbox.isChecked():
                self.flatfield = widget.flatfield_selection.currentText()
            else:
                self.flatfield = None

            if self.method == "lcs":
                self.alpha = float(widget.alpha_input.text())
                self.weak_absorption = widget.weak_absorption_checkbox.isChecked()

            elif self.method == "lcs_df":
                # Récupérer la plage de l'axe 1 du viewer (par exemple, la largeur)
                dim_range = widget.viewer.dims.range[0]
                # Si la plage est fixe (min == max) alors nb_of_point vaut 1, sinon on calcule la taille
                if dim_range[0] == dim_range[1]:
                    self.nb_of_point = 1
                else:
                    self.nb_of_point = int(dim_range[1] - dim_range[0] + 1)
                self.max_shift = float(widget.max_shift_input.text())
                self.pixel = float(widget.pixel_input.text())
                self.dist_object_detector = float(widget.dist_object_detector_input.text())
                self.dist_source_object = float(widget.dist_source_object_input.text())
                self.LCS_median_filter = int(widget.LCS_median_filter_input.text())

            elif self.method == "lcs_dirdf":
                # Même logique pour nb_of_point en utilisant le viewer
                dim_range = widget.viewer.dims.range[0]
                if dim_range[0] == dim_range[1]:
                    self.nb_of_point = 1
                else:
                    self.nb_of_point = int(dim_range[1] - dim_range[0] + 1)
                self.max_shift = float(widget.max_shift_input.text())
                self.pixel = float(widget.pixel_input.text())
                self.dist_object_detector = float(widget.dist_object_detector_input.text())
                self.dist_source_object = float(widget.dist_source_object_input.text())
                self.LCS_median_filter = int(widget.LCS_median_filter_input.text())

            elif self.method == "misti":
                self.pixel = float(widget.pixel_input.text())
                self.dist_object_detector = float(widget.dist_object_detector_input.text())
                self.beta = float(widget.beta_input.text())
                self.delta = float(widget.delta_input.text())
                self.energy = float(widget.energy_input.text())
                self.MIST_median_filter = int(widget.MIST_median_filter_input.text())
                self.sigma_regularization = float(widget.sigma_regularization_input.text())

            if widget.phase_retrieval_checkbox.isChecked():
                self.phase_parameters = {
                    'method': widget.phase_retrieval_selection.currentText(),
                    'pad': "antisym" if widget.pad_checkbox.isChecked() else None
                }
            else:
                self.phase_parameters = None
        except ValueError as e:
            print(f"Error updating parameters: {e}")
