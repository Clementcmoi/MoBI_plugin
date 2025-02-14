import h5py
import numpy as np

import glob
from tkinter import simpledialog
import os

import tkinter as tk
from tkinter import messagebox, ttk

from scipy.ndimage import median_filter

def read_hdf5(paths):
    """
    Reads data from HDF5/NXS files with a single selection of slice and dimension,
    then organizes the layers for each dataset.

    Parameters
    ----------
    paths : list[str] | str
        Paths to files to be processed.

    Returns
    -------
    list
        A list containing tuples for each dataset.
    """

    if isinstance(paths, str):
        paths = [paths]

    if os.path.isdir(paths[0]):
        paths = read_hdf5_folder(paths[0])

    print("Selection of slices and dimensions for each dataset.")
    slices_info = display_and_select_slices(paths[0])

    dataset_layers = {} 

    for path in paths:
        
        with h5py.File(path, "r") as h5file:
            print(f"Files processing : {path}")
            datasets_3d = find_datasets_with_dim_3(h5file)

            if not datasets_3d:
                print(f"No 3D datasets find in {path}.")
                continue

            for keys, shape in datasets_3d:
                if keys in slices_info:
                    slice_info = slices_info[keys]
                    slice_number = slice_info["slice"]
                    dim = slice_info["dimension"]
                    use_median = slice_info["use_median"]

                    if use_median:
                        print("Using median filter on the slice.", path, keys)
                        data = np.median(h5file[keys], axis=dim)
                    else:
                        index = [slice(None)] * 3
                        index[dim] = slice_number
                        data = np.array(h5file[keys][tuple(index)])

                    if keys not in dataset_layers:
                        dataset_layers[keys] = []

                    dataset_layers[keys].append(data)

    layers = []
    for dataset_key, images in dataset_layers.items():
        try:
            if len(images) > 1:
                stacked_images = np.stack(images, axis=0)
            else:
                stacked_images = images[0]  # Une seule image

        except ValueError as e:
            print(
                f"Error while stacking images for dataset {dataset_key}. {e}"
            )
            continue

        name_image = (dataset_key.strip("/").split("/"))[-1]
        metadata = {
            "slice_number": slice_number,
            "dimension": dim,
            "use_median": use_median,
            "paths": paths,
            "dataset_key": dataset_key,
            "multiscale": False,  
        }

        layers.append(
            (
                stacked_images,
                {"name": name_image, "metadata": metadata},
                "image",
            )
        )

    return layers

def find_datasets_with_dim_3(file, group=None, path="", results=None):
    """
    Find all datasets with 3 dimensions in a HDF5 file.
    
    Parameters
    ----------
    file : h5py.File
        HDF5 file to search.
        
    group : h5py.Group
        Group to search.

    path : str
        Current path in the HDF5 file.

    results : list
        List to store the results.

    Returns
    -------
    list
        A list containing tuples with the path and shape of each dataset.
        
    """
    if results is None:
        results = []

    if group is None:
        group = file

    for key in group:
        item = group[key]
        current_path = f"{path}/{key}"
        if isinstance(item, h5py.Group):
            find_datasets_with_dim_3(
                file, group=item, path=current_path, results=results
            )
        elif isinstance(item, h5py.Dataset):
            if len(item.shape) == 3:
                results.append(
                    (current_path, item.shape)
                ) 
    return results

def display_and_select_slices(file_path):
    """
    Display a window to select a slice and a dimension for each 3D image in a HDF5 file.

    Parameters
    ----------
    file_path : str
        Path to the HDF5 file.  

    Returns
    -------
    dict
        A dictionary containing the slice, dimension and use_median for each dataset.
    """

    def submit_selection():
        try:
            for i, (path, shape) in enumerate(datasets_3d):
                slice_value = slice_entries[i].get()
                if not slice_value.isdigit() or not (
                    0 <= int(slice_value) < shape[int(dimensions[i].get())]
                ):
                    raise ValueError(
                        f"Slice invalide pour {path}. Entrez une valeur entre 0 et {shape[int(dimensions[i].get())] - 1}."
                    )

                dimension_value = dimensions[i].get()
                if dimension_value not in ("0", "1", "2"):
                    raise ValueError(
                        f"Dimension invalide pour {path}. Choisissez 0, 1 ou 2."
                    )

                use_median_value = use_median_vars[i].get()

                selections[path] = {
                    "slice": int(slice_value),
                    "dimension": int(dimension_value),
                    "use_median": use_median_value,
                }
            root.destroy() 
        except ValueError as e:
            messagebox.showerror("Erreur", str(e))

    try:
        with h5py.File(file_path, "r") as f:
            datasets_3d = find_datasets_with_dim_3(f)
            if not datasets_3d:
                messagebox.showinfo(
                    "Informations", "Aucune image 3D trouvée dans le fichier."
                )
                return {}

            root = tk.Tk()
            root.title("Sélection des slices et dimensions")

            tk.Label(
                root,
                text="Sélectionnez une slice et une dimension pour chaque image 3D",
                font=("Arial", 14),
            ).grid(row=0, column=0, columnspan=5, pady=10)

            tk.Label(
                root, text="Chemin de l'image", font=("Arial", 12, "bold")
            ).grid(row=1, column=0, padx=5, pady=5, sticky="w")
            tk.Label(root, text="Dimensions", font=("Arial", 12, "bold")).grid(
                row=1, column=1, padx=5, pady=5, sticky="w"
            )
            tk.Label(
                root, text="Slice sélectionnée", font=("Arial", 12, "bold")
            ).grid(row=1, column=2, padx=5, pady=5, sticky="w")
            tk.Label(root, text="Dimension", font=("Arial", 12, "bold")).grid(
                row=1, column=3, padx=5, pady=5, sticky="w"
            )
            tk.Label(root, text="Utiliser médiane", font=("Arial", 12, "bold")).grid(
                row=1, column=4, padx=5, pady=5, sticky="w"
            )

            slice_entries = []
            dimensions = []
            use_median_vars = []
            selections = {}
            for i, (path, shape) in enumerate(datasets_3d):
                tk.Label(root, text=path, wraplength=300).grid(
                    row=i + 2, column=0, padx=5, pady=5, sticky="w"
                )
                tk.Label(root, text=str(shape)).grid(
                    row=i + 2, column=1, padx=5, pady=5, sticky="w"
                )

                slice_entry = ttk.Entry(root, width=10)
                slice_entry.insert(0, "0") 
                slice_entry.grid(row=i + 2, column=2, padx=5, pady=5)
                slice_entries.append(slice_entry)

                dimension_var = tk.StringVar(value="0")
                dimension_menu = ttk.Combobox(
                    root,
                    textvariable=dimension_var,
                    values=["0", "1", "2"],
                    state="readonly",
                    width=5,
                )
                dimension_menu.grid(row=i + 2, column=3, padx=5, pady=5)
                dimensions.append(dimension_var)

                use_median_var = tk.BooleanVar()
                use_median_checkbox = ttk.Checkbutton(root, variable=use_median_var)
                use_median_checkbox.grid(row=i + 2, column=4, padx=5, pady=5)
                use_median_vars.append(use_median_var)

            submit_button = ttk.Button(
                root, text="Valider", command=submit_selection
            )
            submit_button.grid(
                row=len(datasets_3d) + 2, column=0, columnspan=5, pady=10
            )

            root.mainloop()
            return selections
    except Exception as e:
        messagebox.showerror("Error", f"A : {e}")
        return {}


def read_hdf5_folder(path):
    """
    Cherche les fichiers HDF5 contenus dans toute l'arborescence en utilisant glob.

    Une fenêtre s'ouvre pour demander à l'utilisateur une partie du nom des fichiers à ouvrir.

    Parameters:
    path (str): Chemin du dossier où chercher les fichiers.

    Returns:
    list: Une liste contenant les chemins des fichiers à traiter.
    """
    root = tk.Tk()
    root.withdraw()
    text = simpledialog.askstring(
        "Recherche de fichiers HDF5",
        "Entrez une partie du nom des fichiers HDF5 à ouvrir :",
    )
    if not text:
        return []

    paths = glob.glob(path + r"\*\*" + text + r"*.tdf")

    print("Paths found:", paths)

    return paths
