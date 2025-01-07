from typing import TYPE_CHECKING

import numpy as np
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
    QFrame,)
from .widgets._processing import processing
import matplotlib.pyplot as plt

if TYPE_CHECKING:
    import napari


# Uses the `autogenerate: true` flag in the plugin manifest
# to indicate it should be wrapped as a magicgui to autogenerate
# a widget.


class StartProcessing(QWidget):
    """
    Widget personnalisé pour traiter les données dans Napari.
    """

    def __init__(self, viewer: "napari.viewer.Viewer"):
        """
        Initialise le widget avec les boutons et les labels nécessaires.

        Parameters:
        viewer (napari.viewer.Viewer): Instance du viewer Napari.
        """
        super().__init__()
        self.viewer = viewer

        # Configuration de la mise en page principale
        self.setup_ui()


    def setup_ui(self):
        """
        Configure l'interface utilisateur.
        """
        methodes_liste = ["lcs"]

        # Layout principal
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Section : Résultat
        self.result_label = QLabel("Results :")
        self.layout.addWidget(self.result_label)

        # Section : Liste des layers
        btn_list_layers = QPushButton("Display list of layers :")
        btn_list_layers.clicked.connect(self.get_list_layers)
        self.layout.addWidget(btn_list_layers)

        self.layer_label = QLabel("List of layers :")
        self.layout.addWidget(self.layer_label)

        # Ligne horizontale
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        self.layout.addWidget(line)

        # Section : Sélection d'une tranche
        self.ref_registration_selection_label = QLabel("Select a Reference for Registration :")
        self.layout.addWidget(self.ref_registration_selection_label)

        self.ref_registration_selection_value = QLineEdit()
        self.layout.addWidget(self.ref_registration_selection_value)

        btn_validate_ref = QPushButton("Confirm selection")
        btn_validate_ref.clicked.connect(self.registration)
        self.layout.addWidget(btn_validate_ref)

        self.display_selected_slice = QLabel("No reference selected")
        self.layout.addWidget(self.display_selected_slice)

        # Section : Sélection des layers
        self.darkfield_label = QLabel("Select darkfield :")
        self.layout.addWidget(self.darkfield_label)
        self.darkfield_selection = QComboBox()
        self.layout.addWidget(self.darkfield_selection)

        self.reference_label = QLabel("Select reference :")
        self.layout.addWidget(self.reference_label)
        self.reference_selection = QComboBox()
        self.layout.addWidget(self.reference_selection)

        self.sample_label = QLabel("Select sample :")
        self.layout.addWidget(self.sample_label)
        self.sample_selection = QComboBox()
        self.layout.addWidget(self.sample_selection)

        # Section : Flatfield (avec layout imbriqué)
        whitefield_layout = QVBoxLayout()  # Layout imbriqué pour la case à cocher et les widgets dynamiques
        checkbox_layout = QHBoxLayout()   # Layout pour aligner la case à cocher et son label

        checkbox_layout.addWidget(QLabel("Flatfield :"))
        self.checkbox = QCheckBox("")
        self.checkbox.setChecked(False)
        checkbox_layout.addWidget(self.checkbox)

        whitefield_layout.addLayout(checkbox_layout)
        self.layout.addLayout(whitefield_layout)  # Ajoute le layout imbriqué au layout principal

        # Connecter la case à cocher à son callback
        self.flatfield_label = None
        self.flatfield_selection = None
        self.checkbox.stateChanged.connect(
            lambda state: self.on_checkbox_state_changed(state, whitefield_layout)
        )

        # Section : Sélection de la méthode
        self.methode_label = QLabel("Select Methode :")
        self.layout.addWidget(self.methode_label)
        self.methode_selection = QComboBox()
        self.layout.addWidget(self.methode_selection)
        self.methode_selection.addItems(methodes_liste)

        # Section : Bouton de traitement
        btn_start_processing = QPushButton("Start processing")
        btn_start_processing.clicked.connect(self.call_processing)
        self.layout.addWidget(btn_start_processing)

        # Ajouter un espace flexible pour maintenir les widgets en haut
        self.layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # Bouton test
        btn_test = QPushButton("test")
        btn_test.clicked.connect(self.test_function)
        self.layout.addWidget(btn_test)


    def on_checkbox_state_changed(self, checked, layout):
        """Callback pour vérifier l'état de la checkbox."""
        if checked == Qt.Checked:
            self.flatfield_label = QLabel("Select flatfield :")
            layout.addWidget(self.flatfield_label)

            self.flatfield_selection = QComboBox()
            layout.addWidget(self.flatfield_selection)

            for layer in self.viewer.layers:
                self.flatfield_selection.addItem(layer.name)

        else:
        # Supprimer les widgets dynamiques
            self.layout.removeWidget(self.flatfield_label)
            self.flatfield_label.deleteLater()
            self.flatfield_label = None

            self.layout.removeWidget(self.flatfield_selection)
            self.flatfield_selection.deleteLater()
            self.flatfield_selection = None


    def get_list_layers(self):
        """
        Affiche la liste des layers chargés dans le viewer.
        """
        if not self.viewer.layers:
            self.layer_label.setText("Aucun layer chargé.")
            return

        # Liste des noms de layers
        layer_names = [layer.name for layer in self.viewer.layers]
        self.layer_label.setText("Layers :\n" + "\n".join(layer_names))

        # Vérification des combobox avant de les utiliser
        self.darkfield_selection.clear()
        self.reference_selection.clear()
        self.sample_selection.clear()

        for layer in self.viewer.layers:
            self.darkfield_selection.addItem(layer.name)
            self.reference_selection.addItem(layer.name)
            self.sample_selection.addItem(layer.name)
        
        # Met à jour la plage dynamique pour la référence
        self.update_ref_registration_range()

    def registration(self):
        slice_selected = self.ref_registration_selection_value.text()
        self.display_selected_slice.setText(
            f"Selected reference: {slice_selected}"
        )



        return slice_selected

    def update_ref_registration_range(self):
        """
        Met à jour l'intervalle valide pour la sélection d'une référence.
        """
        # Vérifie s'il y a des layers dans le viewer
        if not self.viewer.layers:
            self.ref_registration_selection_label.setText("No layers loaded.")
            return

        # Récupère les dimensions des layers pour déterminer min et max
        min_slice = 0
        max_slice = max(layer.data.shape[0] for layer in self.viewer.layers if hasattr(layer.data, "shape"))-1

        # Met à jour le label avec la plage
        self.ref_registration_selection_label.setText(
            f"Select a Reference for Registration (between {min_slice} and {max_slice}):"
        )

        # Conserve la plage pour validation future
        self.min_slice = min_slice
        self.max_slice = max_slice



    def call_processing(self):
        """
        Appelle une fonction externe en passant les données nécessaires.
        """

        # Récupérer les noms des couches (layers) disponibles
        layer_names = [self.sample_selection.currentText(), self.reference_selection.currentText(), self.darkfield_selection.currentText()]

        if self.flatfield_selection is not None:
            layer_names.append(self.flatfield_selection.currentText())

        methode = self.methode_selection.currentText()

        # Vérifiez que des couches sont présentes
        if len(layer_names) < 3:  # Exemple : s'assurer d'avoir au moins 3 couches
            self.result_label.setText("Veuillez sélectionner au moins trois layers.")
            return

        # Affiche les informations pour débogage
        print("Couches sélectionnées :", layer_names)
        # Appel de la fonction externe avec les données
        try:
            processing(layer_names, self.viewer, methode)
            self.result_label.setText("Traitement terminé avec succès.")
        except Exception as e:
            self.result_label.setText(f"Erreur lors du traitement : {e}")
            print(f"Erreur : {e}")

    def test_function(self):
        """
        Affiche l'histogramme de la couche sélectionnée.
        """
        # Vérifie qu'une couche est sélectionnée dans le combobox "sample_selection"
        selected_layer_name = self.sample_selection.currentText()
        if not selected_layer_name:
            self.result_label.setText("Veuillez sélectionner une couche dans 'Select sample'.")
            return

        # Récupère la couche correspondante
        selected_layer = self.viewer.layers[selected_layer_name]
        if not hasattr(selected_layer, "data"):
            self.result_label.setText("La couche sélectionnée ne contient pas de données valides.")
            return

        # Récupère les données de la couche
        data = selected_layer.data

        # Vérifie si les données sont 2D ou 3D et les aplati pour l'histogramme
        if data.ndim > 1:
            data = data.ravel()

        # Affiche l'histogramme avec Matplotlib
        plt.figure(figsize=(8, 6))
        plt.hist(data, bins=50, color="blue", alpha=0.7)
        plt.title(f"Histogramme de la couche : {selected_layer_name}")
        plt.xlabel("Valeurs de pixels")
        plt.ylabel("Fréquence")
        plt.grid(True)
        plt.show()