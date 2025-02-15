from typing import TYPE_CHECKING
from qtpy.QtWidgets import QWidget, QVBoxLayout, QLabel, QSpacerItem, QSizePolicy
from ._utils import LayerUtils, Parameters
from ._section import add_layer_selection_section, add_darkfield_section, add_flatfield_section, add_lcs_variables, add_phase_retrieval_section, add_processing_button

if TYPE_CHECKING:
    import napari

class LcsWidget(QWidget):
    """
    Custom widget for LCS processing in Napari.
    """
    def __init__(self, viewer: "napari.viewer.Viewer"):
        super().__init__()
        self.viewer = viewer
        self.parameters = Parameters(method="lcs")  # Initialize parameters with default method "lcs"
        print(f"Initialized self.parameters: {self.parameters}")

        self.setup_ui()
        LayerUtils.connect_signals(self)

    def setup_ui(self):
        """
        Set up the user interface components.
        """
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(QLabel("LCS Processing Widget"))

        add_layer_selection_section(self)
        add_darkfield_section(self)
        add_flatfield_section(self)

        add_lcs_variables(self)

        add_phase_retrieval_section(self)

        add_processing_button(self)

        LayerUtils.update_layer_selections(self)
        self.layout().addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))