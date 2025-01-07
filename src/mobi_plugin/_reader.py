from .readers._tdf_reader import read_tdf
from .readers._edf_reader import read_edf


def napari_get_reader(path):
    """Determine the appropriate reader function based on the file type.

    Parameters
    ----------
    path : str or list of str
        Path to a file, or list of paths.

    Returns
    -------
    function or None
        A reader function that accepts the same path(s) and returns layer data,
        or None if the format is not recognized.
    """
    if isinstance(path, list):
        path = path[0]  # Assume all paths are of the same type

    if path.endswith(".tdf"):
        return read_tdf
    
    if path.endswith(".edf"):
        return read_edf

    return None
