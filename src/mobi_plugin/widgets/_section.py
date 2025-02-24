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
from ._utils import Experiment, LayerUtils  # Correct import
from ._processing import processing  # Add this import

def add_layer_selection_section(widget):
    """
    Add layer selection UI components.
    """
    widget.reference_selection = create_combobox(widget, "Select reference:")
    widget.sample_selection = create_combobox(widget, "Select sample:")

def create_combobox(widget, label_text):
    """
    Create a labeled QComboBox.
    """
    widget.layout().addWidget(QLabel(label_text))
    combobox = QComboBox()
    widget.layout().addWidget(combobox)
    return combobox

def toggle_field_widgets(widget, checked, layout, label_attr, selection_attr, label_text):
    if checked == Qt.Checked:
        if not getattr(widget, label_attr):
            setattr(widget, label_attr, QLabel(label_text))
            layout.addWidget(getattr(widget, label_attr))
        if not getattr(widget, selection_attr):
            combobox = QComboBox()
            combobox.addItems([layer.name for layer in widget.viewer.layers])
            setattr(widget, selection_attr, combobox)
            layout.addWidget(combobox)
    else:
        widget_label = getattr(widget, label_attr)
        widget_selection = getattr(widget, selection_attr)
        if widget_label:
            layout.removeWidget(widget_label)
            widget_label.deleteLater()
            setattr(widget, label_attr, None)
        if widget_selection.isVisible():
            layout.removeWidget(widget_selection)
            widget_selection.deleteLater()
            setattr(widget, selection_attr, None)
    widget.layout().update()

def add_darkfield_section(widget):
    """
    Add darkfield-related UI components.
    """
    darkfield_layout = QVBoxLayout()

    checkbox_layout = QHBoxLayout()
    checkbox_layout.addWidget(QLabel("Darkfield:"))
    widget.darkfield_checkbox = QCheckBox()
    widget.darkfield_checkbox.stateChanged.connect(lambda state: toggle_field_widgets(widget, state, darkfield_layout, 'darkfield_label', 'darkfield_selection', 'Select darkfield:'))
    checkbox_layout.addWidget(widget.darkfield_checkbox)

    darkfield_layout.addLayout(checkbox_layout)
    widget.layout().addLayout(darkfield_layout)

    widget.darkfield_label = None
    widget.darkfield_selection = None

def add_flatfield_section(widget):
    """
    Add flatfield-related UI components.
    """
    flatfield_layout = QVBoxLayout()

    checkbox_layout = QHBoxLayout()
    checkbox_layout.addWidget(QLabel("Flatfield:"))
    widget.flatfield_checkbox = QCheckBox()
    widget.flatfield_checkbox.stateChanged.connect(lambda state: toggle_field_widgets(widget, state, flatfield_layout, 'flatfield_label', 'flatfield_selection', 'Select flatfield:'))
    checkbox_layout.addWidget(widget.flatfield_checkbox)

    flatfield_layout.addLayout(checkbox_layout)
    widget.layout().addLayout(flatfield_layout)

    widget.flatfield_label = None
    widget.flatfield_selection = None

def add_phase_retrieval_section(widget):
    """
    Add phase retrieval section.
    """
    phase_retrieval_layout = QVBoxLayout()

    checkbox_layout = QHBoxLayout()
    checkbox_layout.addWidget(QLabel("Phase Retrieval:"))
    widget.phase_retrieval_checkbox = QCheckBox()
    widget.phase_retrieval_checkbox.stateChanged.connect(lambda state: toggle_field_phase(widget, state, phase_retrieval_layout, 'phase_retrieval_label', 'phase_retrieval_selection', 'Select method:'))
    checkbox_layout.addWidget(widget.phase_retrieval_checkbox)

    phase_retrieval_layout.addLayout(checkbox_layout)
    widget.pad_checkbox = QCheckBox("Pad")
    widget.pad_checkbox.setVisible(False)
    phase_retrieval_layout.addWidget(widget.pad_checkbox)
    widget.layout().addLayout(phase_retrieval_layout)

    widget.phase_retrieval_label = None
    widget.phase_retrieval_selection = None

def add_dynamic_variables_section(widget):
    """
    Add dynamic variables section.
    """
    widget.variables_layout = QVBoxLayout()
    widget.layout().addLayout(widget.variables_layout)
    widget.update_variables_for_method()

def add_processing_button(widget):
    """
    Add the processing button.
    """
    btn_start_processing = QPushButton("Start processing")
    btn_start_processing.clicked.connect(lambda: call_processing(widget))
    widget.layout().addWidget(btn_start_processing)

def update_layer_selections(widget, event=None):
    """
    Update the QComboBox selections with the list of layers.
    """
    layers = [layer.name for layer in widget.viewer.layers]
    for combobox in [widget.reference_selection, widget.sample_selection]:
        combobox.clear()
        combobox.addItems(layers)

    if widget.darkfield_checkbox.isChecked() and widget.darkfield_selection:
        widget.darkfield_selection.clear()
        widget.darkfield_selection.addItems(layers)
    
    if widget.flatfield_checkbox.isChecked() and widget.flatfield_selection:
        widget.flatfield_selection.clear()
        widget.flatfield_selection.addItems(layers)

def call_processing(widget):
    """
    Met à jour les paramètres de l'expérience à partir des valeurs du widget,
    puis lance le traitement en utilisant l'objet experiment et le viewer.
    """
    widget.experiment.update_parameters(widget)  # Correct method call
    result = processing(widget.experiment, widget.viewer)
    return result

def add_lcs_variables(widget):
    """
    Add widgets for the 'lcs' method variables.
    """
    if not hasattr(widget, 'variables_layout'):
        widget.variables_layout = QVBoxLayout()
        widget.layout().addLayout(widget.variables_layout)
    widget.variables_layout.addWidget(QLabel("Alpha:"))
    
    widget.alpha_input = QLineEdit()
    widget.alpha_input.textChanged.connect(lambda: update_parameters(widget))
    widget.variables_layout.addWidget(widget.alpha_input)

    widget.weak_absorption_checkbox = QCheckBox("Weak Absorption")
    widget.weak_absorption_checkbox.stateChanged.connect(lambda: update_parameters(widget))
    widget.variables_layout.addWidget(widget.weak_absorption_checkbox)

def add_cst_csvt_variables(widget):
    """
    Add widgets for the 'cst_csvt' method variables.
    """
    widget.variables_layout.addWidget(QLabel("Window Size:"))
    widget.window_size_input = QLineEdit()
    widget.window_size_input.textChanged.connect(lambda: update_parameters(widget))
    widget.variables_layout.addWidget(widget.window_size_input)

    widget.variables_layout.addWidget(QLabel("Pixel Shift:"))
    widget.pixel_shift_input = QLineEdit()
    widget.pixel_shift_input.textChanged.connect(lambda: update_parameters(widget))
    widget.variables_layout.addWidget(widget.pixel_shift_input)

def add_lcs_df_variables(widget):
    """
    Add widgets for the 'lcs_dirdf' method variables.
    """
    if not hasattr(widget, 'variables_layout'):
        widget.variables_layout = QVBoxLayout()
        widget.layout().addLayout(widget.variables_layout)

    widget.variables_layout.addWidget(QLabel("Max Shift:"))
    widget.max_shift_input = QLineEdit()
    widget.max_shift_input.textChanged.connect(lambda: update_parameters(widget))
    widget.variables_layout.addWidget(widget.max_shift_input)

    widget.variables_layout.addWidget(QLabel("Pixel Size:"))
    widget.pixel_input = QLineEdit()
    widget.pixel_input.textChanged.connect(lambda: update_parameters(widget))
    widget.variables_layout.addWidget(widget.pixel_input)

    widget.variables_layout.addWidget(QLabel("Distance Object-Detector (en mètres):"))
    widget.dist_object_detector_input = QLineEdit()
    widget.dist_object_detector_input.textChanged.connect(lambda: update_parameters(widget))
    widget.variables_layout.addWidget(widget.dist_object_detector_input)

    widget.variables_layout.addWidget(QLabel("Distance Source-Object:"))
    widget.dist_source_object_input = QLineEdit()
    widget.dist_source_object_input.textChanged.connect(lambda: update_parameters(widget))
    widget.variables_layout.addWidget(widget.dist_source_object_input)

    widget.variables_layout.addWidget(QLabel("LCS Median Filter:"))
    widget.LCS_median_filter_input = QLineEdit()
    widget.LCS_median_filter_input.textChanged.connect(lambda: update_parameters(widget))
    widget.variables_layout.addWidget(widget.LCS_median_filter_input)

def add_misti_variables(widget):
    """
    Add widgets for the 'misti' method variables.
    """
    if not hasattr(widget, 'variables_layout'):
        widget.variables_layout = QVBoxLayout()
        widget.layout().addLayout(widget.variables_layout)

    widget.variables_layout.addWidget(QLabel("Pixel Size:"))
    widget.pixel_input = QLineEdit()
    widget.pixel_input.textChanged.connect(lambda: update_parameters(widget))
    widget.variables_layout.addWidget(widget.pixel_input)

    widget.variables_layout.addWidget(QLabel("Distance Object-Detector (en mètres):"))
    widget.dist_object_detector_input = QLineEdit()
    widget.dist_object_detector_input.textChanged.connect(lambda: update_parameters(widget))
    widget.variables_layout.addWidget(widget.dist_object_detector_input)

    widget.variables_layout.addWidget(QLabel("Beta:"))
    widget.beta_input = QLineEdit()
    widget.beta_input.textChanged.connect(lambda: update_parameters(widget))
    widget.variables_layout.addWidget(widget.beta_input)

    widget.variables_layout.addWidget(QLabel("Delta:"))
    widget.delta_input = QLineEdit()
    widget.delta_input.textChanged.connect(lambda: update_parameters(widget))
    widget.variables_layout.addWidget(widget.delta_input)

    widget.variables_layout.addWidget(QLabel("Energy:"))
    widget.energy_input = QLineEdit()
    widget.energy_input.textChanged.connect(lambda: update_parameters(widget))
    widget.variables_layout.addWidget(widget.energy_input)

    widget.variables_layout.addWidget(QLabel("MIST Median Filter:"))
    widget.MIST_median_filter_input = QLineEdit()
    widget.MIST_median_filter_input.textChanged.connect(lambda: update_parameters(widget))
    widget.variables_layout.addWidget(widget.MIST_median_filter_input)

    widget.variables_layout.addWidget(QLabel("Sigma Regularization:"))
    widget.sigma_regularization_input = QLineEdit()
    widget.sigma_regularization_input.textChanged.connect(lambda: update_parameters(widget))
    widget.variables_layout.addWidget(widget.sigma_regularization_input)

def toggle_field_phase(widget, checked, layout, label_attr, selection_attr, label_text):
    if checked == Qt.Checked:
        if not getattr(widget, label_attr):
            setattr(widget, label_attr, QLabel(label_text))
            layout.addWidget(getattr(widget, label_attr))
        if not getattr(widget, selection_attr):
            combobox = QComboBox()
            combobox.addItems(["Kottler", "Frankot_Chellappa"])
            setattr(widget, selection_attr, combobox)
            layout.addWidget(combobox)
        widget.pad_checkbox.setVisible(True)
    else:
        widget_label = getattr(widget, label_attr)
        widget_selection = getattr(widget, selection_attr)
        if widget_label:
            layout.removeWidget(widget_label)
            widget_label.deleteLater()
            setattr(widget, label_attr, None)
        if widget_selection:
            layout.removeWidget(widget_selection)
            widget_selection.deleteLater()
            setattr(widget, selection_attr, None)
        widget.pad_checkbox.setVisible(False)
    widget.layout().update()

def update_parameters(widget):
    """
    Update the parameters dictionary based on widget values.
    """
    widget.experiment.update_parameters(widget)  # Correct method call
