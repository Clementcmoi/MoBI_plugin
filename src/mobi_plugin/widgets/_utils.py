from numpy import pi
from qtpy.QtCore import QSettings

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
        self.settings = QSettings("mobi", "mobiconfig")

        self.sample_images = None
        self.reference_images = None
        self.darkfield = None
        self.flatfield = None

        self._initialize_method_parameters()

        self.load_settings()

        print(f"Initialized Parameters with method: {self.method}")

    def _initialize_method_parameters(self):

        if self.method == "lcs":
            self.alpha = None
            self.weak_absorption = False 

        elif self.method == "lcs_df":
            self.nb_of_point = None
            self.max_shift = None
            self.pixel = None
            self.energy = None
            self.dist_object_detector = None
            self.dist_source_object = None
            self.LCS_median_filter = None

        elif self.method == "lcs_dirdf":
            self.nb_of_point = None
            self.max_shift = None
            self.pixel = None
            self.energy = None
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

        elif self.method == "mistii1":
            self.nb_of_point = None
            self.pixel = None
            self.dist_object_detector = None
            self.beta = None
            self.delta = None
            self.energy = None
            self.MIST_median_filter = None
            self.sigma_regularization = None

        elif self.method == "mistii2":
            self.nb_of_point = None
            self.pixel = None
            self.dist_object_detector = None
            self.beta = None
            self.delta = None
            self.energy = None
            self.MIST_median_filter = None
            self.sigma_regularization = None

        elif self.method == "pavlov2020":
            self.pixel = None
            self.dist_object_detector = None
            self.dist_source_object = None
            self.beta = None
            self.delta = None
            self.energy = None
            self.sigma_regularization = None
            self.source_size = None

        elif self.method == "xsvt":
            self.max_shift = None
            self.pixel = None
            self.dist_object_detector = None
            self.dist_source_object = None
            self.energy = None
            self.XSVT_median_filter = None
            self.XSVT_Nw = None

        elif self.method == "reversflowlcs":
            self.nb_of_point = None
            self.max_shift = None
            self.pixel = None
            self.dist_object_detector = None
            self.dist_source_object = None
            self.energy = None

        elif self.method == "specklematching":
            self.max_shift = None
            self.pixel = None
            self.dist_object_detector = None
            self.dist_source_object = None
            self.UMPA_Nw = None
            self.energy = None
            
        self.phase_parameters = None

    def getk(self):
        """
        Energy in eV
        """
        h=6.626e-34
        c=2.998e8
        e=1.6e-19
        k=2*pi*self.energy*e/(h*c)
        return k     
    
    def load_settings(self):

        method_key_prefix = f"{self.method}/"

        for attr in vars(self):
            if attr not in ["method", "settings"]:
                key = method_key_prefix + attr
                value = self.settings.value(key, getattr(self, attr))
                setattr(self, attr, value)

        print(f"Loaded Parameters for method: {self.method}: {vars(self)}")

    def save_settings(self):

        method_key_prefix = f"{self.method}/"

        for attr in vars(self):
            if attr not in ["method", "settings"]:
                key = method_key_prefix + attr
                self.settings.setValue(key, getattr(self, attr))

        print(f"Saved Parameters for method: {self.method}: {vars(self)}")

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
                dim_range = widget.viewer.dims.range[0]
                if dim_range[0] == dim_range[1]:
                    self.nb_of_point = 1
                else:
                    self.nb_of_point = int(dim_range[1] - dim_range[0] + 1)
                self.max_shift = float(widget.max_shift_input.text())
                self.pixel = float(widget.pixel_input.text())
                self.energy = float(widget.energy_input.text())
                self.dist_object_detector = float(widget.dist_object_detector_input.text())
                self.dist_source_object = float(widget.dist_source_object_input.text())
                self.LCS_median_filter = int(widget.LCS_median_filter_input.text())

            elif self.method == "lcs_dirdf":
                dim_range = widget.viewer.dims.range[0]
                if dim_range[0] == dim_range[1]:
                    self.nb_of_point = 1
                else:
                    self.nb_of_point = int(dim_range[1] - dim_range[0] + 1)
                self.max_shift = float(widget.max_shift_input.text())
                self.pixel = float(widget.pixel_input.text())
                self.energy = float(widget.energy_input.text())
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

            elif self.method == "mistii1":
                dim_range = widget.viewer.dims.range[0]
                if dim_range[0] == dim_range[1]:
                    self.nb_of_point = 1
                else:
                    self.nb_of_point = int(dim_range[1] - dim_range[0] + 1)
                self.pixel = float(widget.pixel_input.text())
                self.dist_object_detector = float(widget.dist_object_detector_input.text())
                self.beta = float(widget.beta_input.text())
                self.delta = float(widget.delta_input.text())
                self.energy = float(widget.energy_input.text())
                self.MIST_median_filter = int(widget.MIST_median_filter_input.text())
                self.sigma_regularization = float(widget.sigma_regularization_input.text())

            elif self.method == "mistii2":
                dim_range = widget.viewer.dims.range[0]
                if dim_range[0] == dim_range[1]:
                    self.nb_of_point = 1
                else:
                    self.nb_of_point = int(dim_range[1] - dim_range[0] + 1)
                self.pixel = float(widget.pixel_input.text())
                self.dist_object_detector = float(widget.dist_object_detector_input.text())
                self.beta = float(widget.beta_input.text())
                self.delta = float(widget.delta_input.text())
                self.energy = float(widget.energy_input.text())
                self.MIST_median_filter = int(widget.MIST_median_filter_input.text())
                self.sigma_regularization = float(widget.sigma_regularization_input.text())

            elif self.method == "pavlov2020":
                self.pixel = float(widget.pixel_input.text())
                self.dist_object_detector = float(widget.dist_object_detector_input.text())
                self.dist_source_object = float(widget.dist_source_object_input.text())
                self.beta = float(widget.beta_input.text())
                self.delta = float(widget.delta_input.text())
                self.energy = float(widget.energy_input.text())
                self.sigma_regularization = float(widget.sigma_regularization_input.text())
                self.source_size = float(widget.source_size_input.text())

            elif self.method == "xsvt":
                self.max_shift = int(widget.max_shift_input.text())
                self.pixel = float(widget.pixel_input.text())
                self.dist_object_detector = float(widget.dist_object_detector_input.text())
                self.dist_source_object = float(widget.dist_source_object_input.text())
                self.energy = float(widget.energy_input.text())
                self.XSVT_median_filter = int(widget.XSVT_median_filter_input.text())
                self.XSVT_Nw = int(widget.XSVT_Nw_input.text())

            elif self.method == "reversflowlcs":
                dim_range = widget.viewer.dims.range[0]
                if dim_range[0] == dim_range[1]:
                    self.nb_of_point = 1
                else:
                    self.nb_of_point = int(dim_range[1] - dim_range[0] + 1)
                self.max_shift = float(widget.max_shift_input.text())
                self.pixel = float(widget.pixel_input.text())
                self.dist_object_detector = float(widget.dist_object_detector_input.text())
                self.dist_source_object = float(widget.dist_source_object_input.text())
                self.energy = float(widget.energy_input.text())
            
            elif self.method == "specklematching":
                self.max_shift = int(widget.max_shift_input.text())
                self.pixel = float(widget.pixel_input.text())
                self.dist_object_detector = float(widget.dist_object_detector_input.text())
                self.dist_source_object = float(widget.dist_source_object_input.text())
                self.UMPA_Nw = int(widget.UMPA_Nw_input.text())
                self.energy = float(widget.energy_input.text())

            if hasattr(widget, 'phase_retrieval_checkbox') and widget.phase_retrieval_checkbox.isChecked():
                self.phase_parameters = {
                    'method': widget.phase_retrieval_selection.currentText(),
                    'pad': "antisym" if widget.pad_checkbox.isChecked() else None
                }
            else:
                self.phase_parameters = None

            self.save_settings()

        except ValueError as e:
            print(f"Error updating parameters: {e}")
