try:
    from ._version import version as __version__
except ImportError:
    __version__ = "unknown"

# Importation des fonctions nécessaires des différents modules
from ._sample_data import make_sample_data
from ._widget import StartProcessing
from ._writer import write_multiple, write_single_image

# Liste des objets exposés par le package
__all__ = (
    "__version__",
    "napari_get_reader",
    "write_single_image",
    "write_multiple",
    "make_sample_data",
    "StartProcessing",
)
