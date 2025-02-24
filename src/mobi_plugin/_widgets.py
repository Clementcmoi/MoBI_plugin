from typing import TYPE_CHECKING
from qtpy.QtWidgets import QWidget, QVBoxLayout, QLabel, QSpacerItem, QSizePolicy
from .widgets._utils import LayerUtils, Experiment  # Correct import
from .widgets._section import * 

if TYPE_CHECKING:
    import napari

class LcsWidget(QWidget):
    """
    Custom widget for LCS processing in Napari.
    """
    def __init__(self, viewer: "napari.viewer.Viewer"):
        super().__init__()
        self.viewer = viewer
        self.experiment = Experiment(method="lcs")  # Initialize parameters with default method "lcs"
        print(f"Initialized self.experiment_parameters: {self.experiment}")

        self.setup_ui()
        LayerUtils.connect_signals(self)

    def setup_ui(self):
        """
        Set up the user interface components.
        """
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(QLabel("LCS Processing"))

        add_layer_selection_section(self)
        add_darkfield_section(self)
        add_flatfield_section(self)

        add_lcs_variables(self)

        add_phase_retrieval_section(self)

        add_processing_button(self)

        LayerUtils.update_layer_selections(self)
        self.layout().addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))


class LcsdfWidget(QWidget):
    """
    Custom widget for LCS with Darkfield processing in Napari.
    """
    def __init__(self, viewer: "napari.viewer.Viewer"):
        super().__init__()
        self.viewer = viewer
        self.experiment = Experiment(method="lcs_df")  # Initialize parameters with default method "lcs_df"
        print(f"Initialized self.experiment_parameters: {self.experiment}")

        self.setup_ui()
        LayerUtils.connect_signals(self)

    def setup_ui(self):
        """
        Set up the user interface components.
        """
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(QLabel("LCS DF Processing"))

        add_layer_selection_section(self)
        add_darkfield_section(self)
        add_flatfield_section(self)

        add_lcs_df_variables(self)

        add_phase_retrieval_section(self)

        add_processing_button(self)

        LayerUtils.update_layer_selections(self)
        self.layout().addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

class LcsdirdfWidget(QWidget):
    """
    Custom widget for LCS with directional Darkfield processing in Napari.
    """
    def __init__(self, viewer: "napari.viewer.Viewer"):
        super().__init__()
        self.viewer = viewer
        self.experiment = Experiment(method="lcs_dirdf")  # Initialize parameters with default method "lcs_df"
        print(f"Initialized self.experiment_parameters: {self.experiment}")

        self.setup_ui()
        LayerUtils.connect_signals(self)

    def setup_ui(self):
        """
        Set up the user interface components.
        """
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(QLabel("LCS Dir DF Processing"))

        add_layer_selection_section(self)
        add_darkfield_section(self)
        add_flatfield_section(self)

        add_lcs_df_variables(self)

        add_phase_retrieval_section(self)

        add_processing_button(self)

        LayerUtils.update_layer_selections(self)
        self.layout().addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

class MistiWidget(QWidget):
    """
    Custom widget for MISTI processing in Napari.
    """
    def __init__(self, viewer: "napari.viewer.Viewer"):
        super().__init__()
        self.viewer = viewer
        self.experiment = Experiment(method="misti")
        print(f"Initialized self.experiment_parameters: {self.experiment}")

        self.setup_ui()
        LayerUtils.connect_signals(self)

    def setup_ui(self):
        """
        Set up the user interface components.
        """
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(QLabel("MISTI Processing"))

        add_layer_selection_section(self)
        add_darkfield_section(self)
        add_flatfield_section(self)

        add_misti_variables(self)
        
        add_phase_retrieval_section(self)

        add_processing_button(self)

        LayerUtils.update_layer_selections(self)
        self.layout().addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))