try:
    from ._version import version as __version__
except ImportError:
    __version__ = "unknown"

# Importation des fonctions nécessaires des différents modules
from ._sample_data import make_sample_data
from ._writer import write_multiple, write_single_image

from ._widgets import (
    LcsWidget,
    LcsdfWidget,
    LcsdirdfWidget,
    MistiWidget,
    Mistii1Widget,
    Mistii2Widget,
    Pavlov2020Widget,
    XsvtWidget,
    ReversflowlcsWidget,
    SpecklematchingWidget
)


# Liste des objets exposés par le package
__all__ = (
    "__version__",
    "write_single_image",
    "write_multiple",
    "make_sample_data",
    "LcsWidget",
    "LcsdfWidget",
    "LcsdirdfWidget",
    "MistiWidget",
    "Mistii1Widget",
    "Mistii2Widget",
    "Pavlov2020Widget",
    "XsvtWidget",
    "ReversflowlcsWidget",
    "SpecklematchingWidget"
)


def napari_experimental_provide_dock_widget():
    return [
        LcsWidget,
        LcsdfWidget,
        LcsdirdfWidget,
        MistiWidget,
        Mistii1Widget,
        Mistii2Widget,
        Pavlov2020Widget,
        XsvtWidget,
        ReversflowlcsWidget,
        SpecklematchingWidget
    ]
