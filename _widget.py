from typing import TYPE_CHECKING

import numpy as np
import matplotlib.pyplot as plt
from PyQt5.QtCore import Qt
from qtpy.QtWidgets import (
    QLabel, 
    QLineEdit, 
    QPushButton, 
    QVBoxLayout, 
    QHBoxLayout, 
    QWidget,
    QComboBox, 
    QCheckBox,
    QSpacerItem, 
    QSizePolicy,
    QInputDialog
)
from magicgui import magic_factory
from .widgets._processing import processing
from .widgets._utils import LayerUtils

if TYPE_CHECKING:
    import napari

@magic_factory
class StartProcessing(QWidget):
    """
    Custom widget for processing data in Napari.
    """
    def __init__(self, viewer: "napari.viewer.Viewer"):
        super().__init__()
        self.viewer = viewer
        self.parameters = {}

        self.setup_ui()
        LayerUtils.connect_signals(self)

    def setup_ui(self):
        """
        Set up the user interface components.
        """
        self.setLayout(QVBoxLayout())

        self.result_label = QLabel("Results:")
        self.layout().addWidget(self.result_label)

        self.add_layer_selection_section()
        self.add_darkfield_section()
        self.add_flatfield_section()
        self.add_method_selection_section()
        self.add_dynamic_variables_section()
        self.add_phase_retrieval_section()
        self.add_processing_button()
        self.add_test_button()

        # Add spacer to push widgets to the top
        LayerUtils.update_layer_selections(self)
        self.layout().addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

    def add_layer_selection_section(self):
        """
        Add layer selection UI components.
        """
        self.reference_selection = self.create_combobox("Select reference:")
        self.sample_selection = self.create_combobox("Select sample:")

    def create_combobox(self, label_text):
        """
        Create a labeled QComboBox.
        """
        self.layout().addWidget(QLabel(label_text))
        combobox = QComboBox()
        self.layout().addWidget(combobox)
        return combobox
    
    def toggle_field_widgets(self, checked, layout, label_attr, selection_attr, label_text):
        if checked == Qt.Checked:
            if not getattr(self, label_attr):
                setattr(self, label_attr, QLabel(label_text))
                layout.addWidget(getattr(self, label_attr))
            if not getattr(self, selection_attr):
                combobox = QComboBox()
                combobox.addItems([layer.name for layer in self.viewer.layers])
                setattr(self, selection_attr, combobox)
                layout.addWidget(combobox)
        else:
            widget_label = getattr(self, label_attr)
            widget_selection = getattr(self, selection_attr)
            if widget_label:
                layout.removeWidget(widget_label)
                widget_label.deleteLater()
                setattr(self, label_attr, None)
            if widget_selection.isVisible():
                layout.removeWidget(widget_selection)
                widget_selection.deleteLater()
                setattr(self, selection_attr, None)
        self.layout().update()

    def add_darkfield_section(self):
        """
        Add darkfield-related UI components.
        """
        darkfield_layout = QVBoxLayout()

        checkbox_layout = QHBoxLayout()
        checkbox_layout.addWidget(QLabel("Darkfield:"))
        self.darkfield_checkbox = QCheckBox()
        self.darkfield_checkbox.stateChanged.connect(lambda state: self.toggle_field_widgets(state, darkfield_layout, 'darkfield_label', 'darkfield_selection', 'Select darkfield:'))
        checkbox_layout.addWidget(self.darkfield_checkbox)

        darkfield_layout.addLayout(checkbox_layout)
        self.layout().addLayout(darkfield_layout)

        self.darkfield_label = None
        self.darkfield_selection = None

    def add_flatfield_section(self):
        """
        Add flatfield-related UI components.
        """
        flatfield_layout = QVBoxLayout()

        checkbox_layout = QHBoxLayout()
        checkbox_layout.addWidget(QLabel("Flatfield:"))
        self.flatfield_checkbox = QCheckBox()
        self.flatfield_checkbox.stateChanged.connect(lambda state: self.toggle_field_widgets(state, flatfield_layout, 'flatfield_label', 'flatfield_selection', 'Select flatfield:'))
        checkbox_layout.addWidget(self.flatfield_checkbox)

        flatfield_layout.addLayout(checkbox_layout)
        self.layout().addLayout(flatfield_layout)

        self.flatfield_label = None
        self.flatfield_selection = None

    def add_method_selection_section(self):
        """
        Add method selection UI components.
        """
        method_layout = QVBoxLayout()

        method_layout.addWidget(QLabel("Select Method:"))
        self.method_selection = QComboBox()
        self.method_selection.addItems(["lcs", "lcs_df", "cst_csvt", "lcs_dirdf", "MISTI", "MISTII", "Pavlov_2020", "XSVT", "ReverseFlow", "Speckle_matching"])
        self.method_selection.currentIndexChanged.connect(self.update_variables_for_method)
        method_layout.addWidget(self.method_selection)

        self.layout().addLayout(method_layout)

    def add_phase_retrieval_section(self):
        """
        Add phase retrieval section.
        """
        phase_retrieval_layout = QVBoxLayout()

        checkbox_layout = QHBoxLayout()
        checkbox_layout.addWidget(QLabel("Phase Retrieval:"))
        self.phase_retrieval_checkbox = QCheckBox()
        self.phase_retrieval_checkbox.stateChanged.connect(lambda state: self.toggle_field_phase(state, phase_retrieval_layout, 'phase_retrieval_label', 'phase_retrieval_selection', 'Select method:'))
        checkbox_layout.addWidget(self.phase_retrieval_checkbox)

        phase_retrieval_layout.addLayout(checkbox_layout)
        self.pad_checkbox = QCheckBox("Pad")
        self.pad_checkbox.setVisible(False)
        phase_retrieval_layout.addWidget(self.pad_checkbox)
        self.layout().addLayout(phase_retrieval_layout)

        self.phase_retrieval_label = None
        self.phase_retrieval_selection = None

    def add_dynamic_variables_section(self):
        """
        Add dynamic variables section.
        """
        self.variables_layout = QVBoxLayout()
        self.layout().addLayout(self.variables_layout)
        self.update_variables_for_method()

    def add_processing_button(self):
        """
        Add the processing button.
        """
        btn_start_processing = QPushButton("Start processing")
        btn_start_processing.clicked.connect(self.call_processing)
        self.layout().addWidget(btn_start_processing)

    def add_test_button(self):
        """
        Add a test button.
        """
        btn_test = QPushButton("Test")
        btn_test.clicked.connect(self.test_function)
        self.layout().addWidget(btn_test)

    def call_processing(self):
        """
        Call the processing function with selected parameters.
        """
        layer_names = {
            'sample': self.sample_selection.currentText(),
            'reference': self.reference_selection.currentText(),
        }

        darkfield_selected = False
        flatfield_selected = False

        if self.darkfield_selection:
            layer_names['darkfield'] = self.darkfield_selection.currentText()
            darkfield_selected = True

        if self.flatfield_selection:
            layer_names['flatfield'] = self.flatfield_selection.currentText()
            flatfield_selected = True

        params = {
            'layer_names': layer_names,
            'viewer': self.viewer,
            'method': self.method_selection.currentText(),
            'parameters': self.parameters,
            'darkfield_selected': darkfield_selected,
            'flatfield_selected': flatfield_selected,
            'phase_retrieval_method': self.phase_retrieval_selection.currentText() if self.phase_retrieval_selection else None,
            'pad': self.pad_checkbox.isChecked()
        }

        try:
            processing(params)
            self.result_label.setText("Processing completed successfully.")
        except Exception as e:
            self.result_label.setText(f"Error during processing: {e}")

    def test_function(self):
        """
        Display the histogram of the selected layer.
        """
        selected_layer = list(self.viewer.layers.selection)
        if not selected_layer:
            self.result_label.setText("Please select a layer in 'Select sample'.")
            return

        selected_layer = selected_layer[0]
        if not hasattr(selected_layer, "data"):
            self.result_label.setText("The selected layer has no valid data.")
            return

        data = selected_layer.data.ravel()
        data_min, data_max = data.min(), data.max()

        plt.figure(figsize=(8, 6))
        plt.hist(data, bins=50, alpha=0.7)
        plt.title(f"Histogram for layer: {selected_layer.name}\nRange: {data_min:.2f} - {data_max:.2f}")
        plt.xlabel("Pixel values")
        plt.ylabel("Frequency")
        plt.grid(True)
        plt.show()

        self.result_label.setText(f"Value range: Min = {data_min:.2f}, Max = {data_max:.2f}")

    def update_variables_for_method(self):
        """
        Update the dynamic variables based on the selected method.
        """
        while self.variables_layout.count():
            child = self.variables_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        if self.method_selection.currentText() == "lcs":
            self.add_lcs_variables()

        if self.method_selection.currentText() == "lcs_df":
            self.add_lcs_df_variables()

        if self.method_selection.currentText() == "cst_csvt":
            self.add_cst_csvt_variables()

        if self.method_selection.currentText() == "lcs_dirdf":
            self.add_lcs_dirdf_variables()

    def add_lcs_variables(self):
        """
        Add widgets for the 'lcs' method variables.
        """
        self.variables_layout.addWidget(QLabel("Alpha:"))
        self.alpha_input = QLineEdit()
        self.alpha_input.textChanged.connect(self.update_parameters)
        self.variables_layout.addWidget(self.alpha_input)

        self.weak_absorption_checkbox = QCheckBox("Weak Absorption")
        self.weak_absorption_checkbox.stateChanged.connect(self.update_parameters)
        self.variables_layout.addWidget(self.weak_absorption_checkbox)

    def add_lcs_df_variables(self):
        """
        Add widgets for the 'lcs_df' method variables.
        """
        self.variables_layout.addWidget(QLabel("Alpha:"))
        self.alpha_input = QLineEdit()
        self.alpha_input.textChanged.connect(self.update_parameters)
        self.variables_layout.addWidget(self.alpha_input)

        self.weak_absorption_checkbox = QCheckBox("Weak Absorption")
        self.weak_absorption_checkbox.stateChanged.connect(self.update_parameters)
        self.variables_layout.addWidget(self.weak_absorption_checkbox)

    def add_cst_csvt_variables(self):
        """
        Add widgets for the 'cst_csvt' method variables.
        """
        self.variables_layout.addWidget(QLabel("Window Size:"))
        self.window_size_input = QLineEdit()
        self.window_size_input.textChanged.connect(self.update_parameters)
        self.variables_layout.addWidget(self.window_size_input)

        self.variables_layout.addWidget(QLabel("Pixel Shift:"))
        self.pixel_shift_input = QLineEdit()
        self.pixel_shift_input.textChanged.connect(self.update_parameters)
        self.variables_layout.addWidget(self.pixel_shift_input)

    def add_lcs_dirdf_variables(self):
        """
        Add widgets for the 'lcs_dirdf' method variables.
        """
        self.variables_layout.addWidget(QLabel("Max Shift:"))
        self.max_shift_input = QLineEdit()
        self.max_shift_input.textChanged.connect(self.update_parameters)
        self.variables_layout.addWidget(self.max_shift_input)

        self.variables_layout.addWidget(QLabel("Pixel Size:"))
        self.pixel_input = QLineEdit()
        self.pixel_input.textChanged.connect(self.update_parameters)
        self.variables_layout.addWidget(self.pixel_input)

        self.variables_layout.addWidget(QLabel("Distance Object-Detector:"))
        self.dist_object_detector_input = QLineEdit()
        self.dist_object_detector_input.textChanged.connect(self.update_parameters)
        self.variables_layout.addWidget(self.dist_object_detector_input)

        self.variables_layout.addWidget(QLabel("Distance Source-Object:"))
        self.dist_source_object_input = QLineEdit()
        self.dist_source_object_input.textChanged.connect(self.update_parameters)
        self.variables_layout.addWidget(self.dist_source_object_input)

        self.variables_layout.addWidget(QLabel("LCS Median Filter:"))
        self.LCS_median_filter_input = QLineEdit()
        self.LCS_median_filter_input.textChanged.connect(self.update_parameters)
        self.variables_layout.addWidget(self.LCS_median_filter_input)

    def toggle_field_phase(self, checked, layout, label_attr, selection_attr, label_text):
        if checked == Qt.Checked:
            if not getattr(self, label_attr):
                setattr(self, label_attr, QLabel(label_text))
                layout.addWidget(getattr(self, label_attr))
            if not getattr(self, selection_attr):
                combobox = QComboBox()
                combobox.addItems(["Kottler", "Frankot_Chellappa"])
                setattr(self, selection_attr, combobox)
                layout.addWidget(combobox)
            self.pad_checkbox.setVisible(True)
        else:
            widget_label = getattr(self, label_attr)
            widget_selection = getattr(self, selection_attr)
            if widget_label:
                layout.removeWidget(widget_label)
                widget_label.deleteLater()
                setattr(self, label_attr, None)
            if widget_selection:
                layout.removeWidget(widget_selection)
                widget_selection.deleteLater()
                setattr(self, selection_attr, None)
            self.pad_checkbox.setVisible(False)
        self.layout().update()

    def update_parameters(self):
        """
        Update the parameters dictionary based on widget values.
        """
        if self.method_selection.currentText() == "lcs" or self.method_selection.currentText() == "lcs_df":
            self.parameters['alpha'] = self.alpha_input.text()
            self.parameters['weak_absorption'] = self.weak_absorption_checkbox.isChecked()
        
        if self.method_selection.currentText() == "cst_csvt":
            self.parameters['window_size'] = self.window_size_input.text()
            self.parameters['pixel_shift'] = self.pixel_shift_input.text()

        if self.method_selection.currentText() == "lcs_dirdf":
            if self.max_shift_input.text():
                self.parameters['max_shift'] = int(self.max_shift_input.text())
            if self.pixel_input.text():
                self.parameters['pixel'] = float(self.pixel_input.text())
            if self.dist_object_detector_input.text():
            if widget_selection:
                layout.removeWidget(widget_selection)
                widget_selection.deleteLater()
                setattr(self, selection_attr, None)
            self.pad_checkbox.setVisible(False)
        self.layout().update()

    def update_parameters(self):
        """
        Update the parameters dictionary based on widget values.
        """
        if self.method_selection.currentText() == "lcs" or self.method_selection.currentText() == "lcs_df":
            self.parameters['alpha'] = self.alpha_input.text()
            self.parameters['weak_absorption'] = self.weak_absorption_checkbox.isChecked()
        
        if self.method_selection.currentText() == "cst_csvt":
            self.parameters['window_size'] = self.window_size_input.text()
            self.parameters['pixel_shift'] = self.pixel_shift_input.text()

        if self.method_selection.currentText() == "lcs_dirdf":
            if self.max_shift_input.text():
                self.parameters['max_shift'] = int(self.max_shift_input.text())
            if self.pixel_input.text():
                self.parameters['pixel'] = float(self.pixel_input.text())
            if self.dist_object_detector_input.text():
                self.parameters['dist_object_detector'] = float(self.dist_object_detector_input.text())
            if self.dist_source_object_input.text():
                self.parameters['dist_source_object'] = float(self.dist_source_object_input.text())
            if self.LCS_median_filter_input.text():
                self.parameters['LCS_median_filter'] = int(self.LCS_median_filter_input.text())

    """
    Fonction externe appelée par le widget.
    Parameters:
    params (dict): Dictionnaire contenant les paramètres nécessaires.
    """

    images = load_images_from_layers(params['viewer'], params['layer_names'])  # dict

    sample = images[params['layer_names']['sample']]
    ref = images[params['layer_names']['reference']]
    dark = images[params['layer_names']['darkfield']] if params['darkfield_selected'] else None
    flat = images[params['layer_names']['flatfield']] if params['flatfield_selected'] else None

    if params['darkfield_selected'] or params['flatfield_selected']:
        ref, sample = apply_corrections(ref, sample, dark, flat)

    pad = "antisym" if params['pad'] else None
        
    match params['method']:
        case "lcs":
            result_lcs = lcs(ref, sample, alpha=float(params['parameters']['alpha']), weak_absorption=params['parameters']['weak_absorption'])
            name = ["abs", "dx", "dy"]

            if params['phase_retrieval_method'] is not None:
                result_phase = phase_retrieval(result_lcs, params['phase_retrieval_method'], pad)
                name.append("phase")

            for img_idx in range(len(name)):
                if img_idx < 3:
                    params['viewer'].add_image(result_lcs[:, :, img_idx], name=name[img_idx] + "_" + params['method'])
                else:
                    params['viewer'].add_image(result_phase, name=name[img_idx] + "_" + params['method'])

        case "lcs_df":
            result_lcs_df = lcs_df(ref, sample, alpha=float(params['parameters']['alpha']), weak_absorption=params['parameters']['weak_absorption'])
            name = ["abs", "dx", "dy", "df"]

            if params['phase_retrieval_method'] is not None:
                result_phase = phase_retrieval(result_lcs_df, params['phase_retrieval_method'], pad)
                name.append("phase")

            for img_idx in range(len(name)):
                if img_idx < 4:
                    params['viewer'].add_image(result_lcs_df[:, :, img_idx], name=name[img_idx] + "_" + params['method'])
                else:
                    params['viewer'].add_image(result_phase, name=name[img_idx] + "_" + params['method'])

        case "cst_csvt":
            result_cst_csvt = cst_csvt(ref, sample, int(params['parameters']['window_size']), (params['parameters']['pixel_shift']))

            name = ["abs", "dx", "dy"]

            if params['phase_retrieval_method'] is not None:
                result_phase = phase_retrieval(result_cst_csvt, params['phase_retrieval_method'], pad)
                name.append("phase")

            for img_idx in range(len(name)):
                if img_idx < 3:
                    params['viewer'].add_image(result_cst_csvt[:, :, img_idx], name=name[img_idx] + "_" + params['method'])
                else:
                    params['viewer'].add_image(result_phase, name=name[img_idx] + "_" + params['method'])

        case "lcs_dirdf":
            experiment = Experiment(
                sample_images=sample,
                reference_images=ref,
                nb_of_point=sample.shape[0],
                max_shift=params['parameters']['max_shift'],
                pixel=params['parameters']['pixel'],
                dist_object_detector=params['parameters']['dist_object_detector'],
                dist_source_object=params['parameters']['dist_source_object'],
                LCS_median_filter=params['parameters']['LCS_median_filter']
            )

            print("Processing LCS_DirDF") # debug
            result_lcs_dirdf = processProjectionLCS_DDF(experiment)
            print("Processing LCS_DirDF done") # debug
            name = ["dx", "dy", "phiFC", "phiK", "absorption", "Deff_xx", "Deff_yy", "Deff_xy", "excentricity", "area", "oriented_DF_exc", "oriented_DF_area", "oriented_DF_norm", "theta", "local_orientation_strength"]
            print("Adding images to viewer") # debug
            for key in result_lcs_dirdf:
                params['viewer'].add_image(result_lcs_dirdf[key], name=key + "_" + params['method'])
           

    return 

def phase_retrieval(result_lcs, phase_retrieval_method, pad):
    gy = result_lcs[:, :, 2]
    gx = result_lcs[:, :, 1]

    match phase_retrieval_method:
        case "Kottler":
            result = kottler(gy, gx, pad=pad)
        case "Frankot_Chellappa":
            result = frankot(gy, gx, pad=pad)

    return result

def load_images_from_layers(viewer, layer_names):
    """
    Charge les images en mémoire à partir des layers sélectionnés dans le viewer Napari.

    Parameters:
    viewer (napari.viewer.Viewer): Instance du viewer Napari.
    layer_names (list, optional): Liste des noms des layers à charger. Si None, charge tous les layers.

    Returns:
    dict: Dictionnaire où les clés sont les noms des layers et les valeurs sont les données des images.
    """
    images = {}

    for layer in viewer.layers:

        # Vérifiez si le layer est dans la liste sélectionnée (si une liste est fournie)
        if layer_names and layer.name not in layer_names.values():
            continue

        # Vérifiez si le layer est une image
        if isinstance(layer, napari.layers.Image):
            images[layer.name] = layer.data
        else:
            print(f"Le layer '{layer.name}' n'est pas de type Image.")

    return images


def apply_corrections(ref, sample, dark, flat):
    """
    Applique les corrections darkfield et flatfield aux images de référence et d'échantillon.

    Parameters:
    ref (numpy.ndarray): Image de référence.
    sample (numpy.ndarray): Image d'échantillon.
    dark (numpy.ndarray): Image darkfield.
    flat (numpy.ndarray): Image flatfield.

    Returns:
    tuple: Tuple contenant les images corrigées dans l'ordre (ref, sample).
    """
    if dark is not None and flat is not None:
        flat_dark = flat - dark

        flat_dark[flat_dark == 0] = 1e-6

        ref = (ref - dark) / (flat_dark)
        sample = (sample - dark) / (flat_dark)

    elif dark is not None:
        ref = ref - dark
        sample = sample - dark

    elif flat is not None:

        flat[flat == 0] = 1e-6

        ref = ref / flat
        sample = sample / flat

    return ref, sample