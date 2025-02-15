from qtpy.QtWidgets import QWidget, QPushButton, QVBoxLayout
import napari

class Widget2(QWidget):
    def __init__(self, viewer: napari.Viewer):
        super().__init__()
        self.viewer = viewer

        layout = QVBoxLayout()
        self.button = QPushButton("Start Analysis")
        layout.addWidget(self.button)
        self.setLayout(layout)

        # Connexion du bouton à la méthode
        self.button.clicked.connect(self.start_analysis)

    def start_analysis(self):
        print("Analysis started!")
        print(f"Nombre de couches dans Napari : {len(self.viewer.layers)}")
