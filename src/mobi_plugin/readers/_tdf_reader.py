import h5py
import numpy as np
from scipy.ndimage import median_filter


def read_elettra_tdf(path, slice_number):
    """Read a single .tdf file and process sample, reference, and dark noise data."""
    with h5py.File(path, "r") as f:
        exchange = f["exchange"]
        data = exchange["data"]
        ref = exchange["data_white"]
        dark_noise = exchange["data_dark"]

        # Preprocess reference data
        ref = np.asarray(ref)
        ref = np.swapaxes(ref, axis1=1, axis2=0)
        median_ref = ref[5, :, :]
        median_ref = median_filter(median_ref, 3)

        # Preprocess dark noise data
        dark_noise = np.asarray(dark_noise)
        dark_noise = np.swapaxes(dark_noise, axis1=1, axis2=0)
        median_dark_noise = dark_noise[5, :, :]

        # Preprocess sample data
        samp = data[:, slice_number, :]
        samp = median_filter(samp, 3)

    return samp, median_ref, median_dark_noise


def read_tdf(paths, slice_number=20):
    """
    Read multiple .tdf files and process them into sample, reference, and dark noise arrays.

    Parameters
    ----------
    paths : str or list of str
        Path(s) to the .tdf file(s).
    slice_number : int, optional
        The slice number to extract from each dataset.

    Returns
    -------
    list of tuples
        Each tuple contains:
        - data (numpy.ndarray): The combined data for all layers.
        - metadata (dict): Metadata for the layer.
        - layer_type (str): The type of layer ("image").
    """
    # If a single path is provided, convert it into a list
    if isinstance(paths, str):
        paths = [paths]

    # Loop over all files and stack results
    results = np.array(
        [read_elettra_tdf(path, slice_number) for path in paths]
    )

    # Split stacked results into separate arrays
    samples = np.stack(results[:, 0])
    references = np.stack(results[:, 1])
    dark_noises = np.stack(results[:, 2])

    # Prepare the data for Napari
    layers = [
        (samples, {"name": "Sample Data"}, "image"),
        (references, {"name": "Reference Data"}, "image"),
        (dark_noises, {"name": "Dark Noise"}, "image"),
    ]

    return layers
