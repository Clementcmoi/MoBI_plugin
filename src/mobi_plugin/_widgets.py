from typing import TYPE_CHECKING
from qtpy.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QSpacerItem,
    QSizePolicy,
)
from .widgets._utils import LayerUtils, Experiment
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
        self.experiment = Experiment(method="lcs")
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
        self.layout().addSpacerItem(
            QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        )


class LcsdfWidget(QWidget):
    """
    Custom widget for LCS with Darkfield processing in Napari.
    """

    def __init__(self, viewer: "napari.viewer.Viewer"):
        super().__init__()
        self.viewer = viewer
        self.experiment = Experiment(method="lcs_df")
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
        self.layout().addSpacerItem(
            QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        )


class LcsdirdfWidget(QWidget):
    """
    Custom widget for LCS with directional Darkfield processing in Napari.
    """

    def __init__(self, viewer: "napari.viewer.Viewer"):
        super().__init__()
        self.viewer = viewer
        self.experiment = Experiment(method="lcs_dirdf")
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
        self.layout().addSpacerItem(
            QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        )


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

        add_processing_button(self)

        LayerUtils.update_layer_selections(self)
        self.layout().addSpacerItem(
            QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        )


class Mistii1Widget(QWidget):
    """
    Custom widget for MISTII_1 processing in Napari.
    """

    def __init__(self, viewer: "napari.viewer.Viewer"):
        super().__init__()
        self.viewer = viewer
        self.experiment = Experiment(method="mistii1")
        print(f"Initialized self.experiment_parameters: {self.experiment}")

        self.setup_ui()
        LayerUtils.connect_signals(self)

    def setup_ui(self):
        """
        Set up the user interface components.
        """
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(QLabel("MISTII_1 Processing"))

        add_layer_selection_section(self)
        add_darkfield_section(self)
        add_flatfield_section(self)

        add_mistii1_variables(self)

        add_processing_button(self)

        LayerUtils.update_layer_selections(self)
        self.layout().addSpacerItem(
            QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        )


class Mistii2Widget(QWidget):
    """
    Custom widget for MISTII_2 processing in Napari.
    """

    def __init__(self, viewer: "napari.viewer.Viewer"):
        super().__init__()
        self.viewer = viewer
        self.experiment = Experiment(method="mistii2")
        print(f"Initialized self.experiment_parameters: {self.experiment}")

        self.setup_ui()
        LayerUtils.connect_signals(self)

    def setup_ui(self):
        """
        Set up the user interface components.
        """
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(QLabel("MISTII_2 Processing"))

        add_layer_selection_section(self)
        add_darkfield_section(self)
        add_flatfield_section(self)

        add_mistii2_variables(self)

        add_processing_button(self)

        LayerUtils.update_layer_selections(self)
        self.layout().addSpacerItem(
            QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        )


class Pavlov2020Widget(QWidget):
    """
    Custom widget for Pavlov2020 processing in Napari.
    """

    def __init__(self, viewer: "napari.viewer.Viewer"):
        super().__init__()
        self.viewer = viewer
        self.experiment = Experiment(method="pavlov2020")
        print(f"Initialized self.experiment_parameters: {self.experiment}")

        self.setup_ui()
        LayerUtils.connect_signals(self)

    def setup_ui(self):
        """
        Set up the user interface components.
        """
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(QLabel("Pavlov2020 Processing"))

        add_layer_selection_section(self)
        add_darkfield_section(self)
        add_flatfield_section(self)

        add_pavlov2020_variables(self)

        add_processing_button(self)

        LayerUtils.update_layer_selections(self)
        self.layout().addSpacerItem(
            QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        )


class XsvtWidget(QWidget):
    """
    Custom widget for XSVT processing in Napari.
    """

    def __init__(self, viewer: "napari.viewer.Viewer"):
        super().__init__()
        self.viewer = viewer
        self.experiment = Experiment(method="xsvt")
        print(f"Initialized self.experiment_parameters: {self.experiment}")

        self.setup_ui()
        LayerUtils.connect_signals(self)

    def setup_ui(self):
        """
        Set up the user interface components.
        """
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(QLabel("XSVT Processing"))

        add_layer_selection_section(self)
        add_darkfield_section(self)
        add_flatfield_section(self)

        add_xsvt_variables(self)

        add_phase_retrieval_section(self)

        add_processing_button(self)

        LayerUtils.update_layer_selections(self)
        self.layout().addSpacerItem(
            QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        )

class ReversflowlcsWidget(QWidget):
    """
    Custom widget for Reversflow LCS processing in Napari.
    """

    def __init__(self, viewer: "napari.viewer.Viewer"):
        super().__init__()
        self.viewer = viewer
        self.experiment = Experiment(method="reversflowlcs")
        print(f"Initialized self.experiment_parameters: {self.experiment}")

        self.setup_ui()
        LayerUtils.connect_signals(self)

    def setup_ui(self):
        """
        Set up the user interface components.
        """
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(QLabel("Reversflow LCS Processing"))

        add_layer_selection_section(self)
        add_darkfield_section(self)
        add_flatfield_section(self)

        add_reversflowlcs_variables(self)

        add_phase_retrieval_section(self)

        add_processing_button(self)

        LayerUtils.update_layer_selections(self)
        self.layout().addSpacerItem(
            QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        )

class SpecklematchingWidget(QWidget):
    """
    Custom widget for Specklematching processing in Napari.
    """

    def __init__(self, viewer: "napari.viewer.Viewer"):
        super().__init__()
        self.viewer = viewer
        self.experiment = Experiment(method="specklematching")
        print(f"Initialized self.experiment_parameters: {self.experiment}")

        self.setup_ui()
        LayerUtils.connect_signals(self)

    def setup_ui(self):
        """
        Set up the user interface components.
        """
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(QLabel("Specklematching Processing"))

        add_layer_selection_section(self)
        add_darkfield_section(self)
        add_flatfield_section(self)

        add_specklematching_variables(self)

        add_phase_retrieval_section(self)

        add_processing_button(self)

        LayerUtils.update_layer_selections(self)
        self.layout().addSpacerItem(
            QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        )