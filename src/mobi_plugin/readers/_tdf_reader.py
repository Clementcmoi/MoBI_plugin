import h5py
import numpy as np
from scipy.ndimage import median_filter
import tkinter as tk
from tkinter import simpledialog

def get_total_radios(path):
    """
    Obtenir le nombre total de tranches dans un fichier .tdf sans charger les données.

    Parameters
    ----------
    path : str
        Chemin vers le fichier .tdf.

    Returns
    -------
    int
        Nombre total de tranches disponibles dans le fichier.
    """
    with h5py.File(path, "r") as f:
        if "exchange" not in f or "data" not in f["exchange"]:
            raise KeyError("Le fichier ne contient pas de groupe 'exchange' ou 'data'.")
        # Obtenir les dimensions des données sans les charger
        data_shape = f["exchange"]["data"].shape
        return data_shape[1]  # Deuxième dimension représente le nombre de tranches


def ask_integer(paths, prompt="Enter a radio number :"):
    """
    Display a dialog box to ask the user for an integer input.

    Parameters
    ----------
    prompt : str
        The prompt message displayed in the dialog box.

    Returns
    -------
    int
        The integer input from the user.
    """
    root = tk.Tk()
    root.withdraw()  # Hide the main tkinter window

    min_value, max_value = [0, get_total_radios(paths[0])]

    try:
        # Demande un entier à l'utilisateur
        user_input = simpledialog.askinteger("Numéro de tranche", prompt)

        # Si l'utilisateur clique sur "Cancel", lever une exception
        if user_input is None:
            raise ValueError("Saisie annulée par l'utilisateur.")

        # Vérifie si l'entier est dans la plage valide
        if not (min_value <= user_input <= max_value):
            raise ValueError(f"Veuillez entrer un entier entre {min_value} et {max_value}.")

        return user_input
    finally:
        root.destroy()  # Ferme la fenêtre Tkinter même en cas d'exception


def read_elettra_tdf(path, slice_number):
    """
    Read and preprocess a single .tdf file.

    Parameters
    ----------
    path : str
        Path to the .tdf file.
    slice_number : int
        The slice index to extract from the sample data.

    Returns
    -------
    tuple
        - Sample data for the given slice (numpy.ndarray).
        - Processed reference data (numpy.ndarray).
        - Processed dark noise data (numpy.ndarray).
    """
    with h5py.File(path, "r") as f:
        # Verify dataset structure
        if "exchange" not in f:
            raise KeyError("Missing 'exchange' group in the file.")
        exchange = f["exchange"]
        required_keys = {"data", "data_white", "data_dark"}
        if not required_keys.issubset(exchange):
            missing = required_keys - set(exchange.keys())
            raise KeyError(f"Missing required keys in 'exchange': {missing}")

        # Extract datasets
        data = exchange["data"]
        ref = exchange["data_white"]
        dark_noise = exchange["data_dark"]

        # Preprocess reference data
        ref = np.asarray(ref)
        ref = np.swapaxes(ref, axis1=1, axis2=0)
        median_ref = median_filter(ref[5, :, :], size=3)

        # Preprocess dark noise data
        dark_noise = np.asarray(dark_noise)
        dark_noise = np.swapaxes(dark_noise, axis1=1, axis2=0)
        median_dark_noise = dark_noise[5, :, :]

        # Preprocess sample data
        samp = np.asarray(data[:, slice_number, :])
        samp = median_filter(samp, size=3)

        print(f"Data shape: {data.shape}")

    return samp, median_ref, median_dark_noise


def read_tdf(paths):
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

    slice_number = ask_integer(paths, "Enter the slice number to process:")

    # Loop over all files and stack results
    results = np.array(
        [read_elettra_tdf(path, slice_number) for path in paths]
    )

    print(results.shape)

    # Split stacked results into separate arrays
    samples = np.stack(results[:, 0])
    references = np.stack(results[:, 1])
    dark_noises = np.stack(results[:, 2])

    # Prepare the data for Napari
    layers = [
        (samples, {"name": "Sample Data", "metadata":{"slice_number": slice_number, "paths": paths}}, "image"),
        (references, {"name": "Reference Data", "metadata":{"slice_number": slice_number, "paths": paths}}, "image"),
        (dark_noises, {"name": "Dark Noise", "metadata":{"slice_number": slice_number, "paths": paths}}, "image"),
    ]

    return layers
