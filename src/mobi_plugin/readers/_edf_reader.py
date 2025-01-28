import h5py
import numpy as np

import tkinter as tk
from tkinter import messagebox, ttk

import fabio

from scipy.ndimage import median_filter

def read_edf(paths, stack=False):
    """
    Read data from EDF files and organize layers for each dataset.

    Parameters
    ----------
    paths : list[str] | str
        Paths to the files to process.
    stack : bool
        If True, stack the data from different files into slices.

    Returns
    -------
    list
        A list containing tuples for each dataset.
    """
    if isinstance(paths, str):
        paths = [paths]

    layers = []

    for path in paths:
        print(f"Processing file: {path}")
        edf_file = fabio.open(path)
        data = edf_file.data

        # Handle 2D images
        if data.ndim == 2:
            layers.append(data)
            continue

        # Default to the first slice and dimension for 3D images
        slice_number = 0
        dim = 0
        use_median = False

        if use_median:
            data = np.median(data, axis=dim)
        else:
            index = [slice(None)] * 3
            index[dim] = slice_number
            data = data[tuple(index)]

        layers.append(data)

    # Stack the data from different files into a 3D array
    stacked_data = np.stack(layers, axis=0)
    stacked_metadata = {"name": "stacked_data", "metadata": {"paths": paths}}
    return [(stacked_data, stacked_metadata, "image")]


