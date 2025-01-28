from .readers._hdf5_reader import read_hdf5
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

    if path.endswith(".tdf") or path.endswith(".nxs"):
        return read_hdf5
    
    elif path.endswith(".edf"):
        return read_edf

    return None

