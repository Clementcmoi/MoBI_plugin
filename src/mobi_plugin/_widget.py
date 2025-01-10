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
    QFrame,
)
from .widgets._processing import processing

if TYPE_CHECKING:
    import napari


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
        self.parameters = {}  # Dictionnaire pour stocker les paramètres

        # Configuration de la mise en page principale
        self.setup_ui()

        # Connecter les signaux de changement de couches
        self.viewer.layers.events.inserted.connect(self.update_layer_selections)
        self.viewer.layers.events.removed.connect(self.update_layer_selections)
        self.viewer.layers.events.changed.connect(self.update_layer_selections)

    def setup_ui(self):
        """
        Configure l'interface utilisateur.
        """
        methodes_liste = ["lcs", "lcs_df", "cst" , "wst", "csvt", "wsvt", "xsvt", "xst_xsvt", "cst_csvt", "kotler", "frankot_chellappa"]

        # Layout principal
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Section : Résultat
        self.result_label = QLabel("Results:")
        self.layout.addWidget(self.result_label)

        # Section : Liste des layers
        self.layer_label = QLabel("List of layers:")
        self.layout.addWidget(self.layer_label)

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

        # Appel automatique de la méthode pour obtenir la liste des couches
        self.update_layer_selections()

        # Section : Flatfield (avec layout imbriqué)
        whitefield_layout = QVBoxLayout()  # Layout imbriqué pour la case à cocher et les widgets dynamiques
        checkbox_layout = QHBoxLayout()  # Layout pour aligner la case à cocher et son label

        checkbox_layout.addWidget(QLabel("Flatfield :"))
        self.checkbox = QCheckBox("")
        self.checkbox.setChecked(False)
        checkbox_layout.addWidget(self.checkbox)

        whitefield_layout.addLayout(checkbox_layout)
        self.layout.addLayout(whitefield_layout)  # Ajoute le layout imbriqué au layout principal

        # Connecter la case à cocher à son callback
        self.flatfield_label = None
        self.flatfield_selection = None
        self.checkbox.stateChanged.connect(lambda state: self.on_checkbox_state_changed(state, whitefield_layout))

        # Section : Sélection de la méthode
        self.methode_label = QLabel("Select Methode :")
        self.layout.addWidget(self.methode_label)
        self.methode_selection = QComboBox()
        self.layout.addWidget(self.methode_selection)
        self.methode_selection.addItems(methodes_liste)
        self.methode_selection.currentIndexChanged.connect(self.update_variables_for_method)

        # Section : Variables dynamiques
        self.variables_layout = QVBoxLayout()
        self.layout.addLayout(self.variables_layout)

        # Appel explicite pour mettre à jour les variables lors de l'initialisation
        self.update_variables_for_method()

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

    def update_layer_selections(self, event=None):
        """
        Update the QComboBox selections with the list of layers.
        """
        layers = [layer.name for layer in self.viewer.layers]

        self.darkfield_selection.clear()
        self.reference_selection.clear()
        self.sample_selection.clear()

        self.darkfield_selection.addItems(layers)
        self.reference_selection.addItems(layers)
        self.sample_selection.addItems(layers)

    def get_list_layers(self):
        """
        Get and display the list of layers.
        """
        self.layers = [layer.name for layer in self.viewer.layers]
        self.layer_label.setText("List of layers: " + ", ".join(self.layers))
        self.update_layer_selections()

    def registration(self):
        slice_selected = self.ref_registration_selection_value.text()
        self.display_selected_slice.setText(
            f"Selected reference: {slice_selected}"
        )

        return slice_selected

    def call_processing(self):
        """
        Appelle une fonction externe en passant les données nécessaires.
        """

        # Récupérer les noms des couches (layers) disponibles
        layer_names = [
            self.sample_selection.currentText(),
            self.reference_selection.currentText(),
            self.darkfield_selection.currentText(),
        ]

        if self.flatfield_selection is not None:
            layer_names.append(self.flatfield_selection.currentText())

        methode = self.methode_selection.currentText()

        # Vérifiez que des couches sont présentes
        if (
            len(layer_names) < 3
        ):  # Exemple : s'assurer d'avoir au moins 3 couches
            self.result_label.setText(
                "Veuillez sélectionner au moins trois layers."
            )
            return

        # Affiche les informations pour débogage
        print("Couches sélectionnées :", layer_names)
        # Appel de la fonction externe avec les données
        try:
            processing(layer_names, self.viewer, methode, self.parameters)
            self.result_label.setText("Traitement terminé avec succès.")
        except Exception as e:
            self.result_label.setText(f"Erreur lors du traitement : {e}")
            print(f"Erreur : {e}")

    def test_function(self):
        """
        Affiche l'histogramme de la couche sélectionnée et la plage de ses valeurs.
        """
        # Vérifie qu'une couche est sélectionnée dans le combobox "sample_selection"
        selected_layer = list(self.viewer.layers.selection)
        if not selected_layer:
            self.result_label.setText(
                "Veuillez sélectionner une couche dans 'Select sample'."
            )
            return

        # Récupère la première couche sélectionnée
        selected_layer = selected_layer[0]
        if not hasattr(selected_layer, "data"):
            self.result_label.setText(
                "La couche sélectionnée ne contient pas de données valides."
            )
            return

        # Récupère les données de la couche
        data = selected_layer.data

        # Vérifie si les données sont 2D ou 3D et les aplati pour l'histogramme
        if data.ndim > 1:
            data = data.ravel()

        # Calcul du minimum et maximum des données
        data_min = data.min()
        data_max = data.max()

        # Affiche l'histogramme avec Matplotlib
        plt.figure(figsize=(8, 6))
        plt.hist(data, bins=50, color="blue", alpha=0.7)
        plt.title(
            f"Histogramme de la couche : {selected_layer.name}\nPlage : {data_min:.2f} - {data_max:.2f}"
        )
        plt.xlabel("Valeurs de pixels")
        plt.ylabel("Fréquence")
        plt.grid(True)
        plt.show()

        # Met à jour le label avec les valeurs min et max
        self.result_label.setText(
            f"Plage des valeurs : Min = {data_min:.2f}, Max = {data_max:.2f}"
        )

    def update_variables_for_method(self):
        """
        Met à jour les variables affichées en fonction de la méthode sélectionnée.
        """
        # Effacer les widgets existants
        while self.variables_layout.count():
            child = self.variables_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # Ajouter des widgets en fonction de la méthode sélectionnée
        selected_method = self.methode_selection.currentText()
        if selected_method == "lcs":
            self.add_lcs_variables()

    def add_lcs_variables(self):
        """
        Ajoute les widgets pour les variables spécifiques à la méthode 'lcs'.
        """
        # Paramètre alpha
        self.alpha_label = QLabel("Alpha:")
        self.variables_layout.addWidget(self.alpha_label)
        self.alpha_input = QLineEdit()
        self.variables_layout.addWidget(self.alpha_input)
        self.alpha_input.textChanged.connect(self.update_parameters)

        # Case à cocher pour weak_absorption
        self.weak_absorption_checkbox = QCheckBox("Weak Absorption")
        self.variables_layout.addWidget(self.weak_absorption_checkbox)
        self.weak_absorption_checkbox.stateChanged.connect(self.update_parameters)

    def update_parameters(self):
        """
        Met à jour le dictionnaire des paramètres en fonction des valeurs des widgets.
        """
        self.parameters['alpha'] = self.alpha_input.text()
        self.parameters['weak_absorption'] = self.weak_absorption_checkbox.isChecked()
