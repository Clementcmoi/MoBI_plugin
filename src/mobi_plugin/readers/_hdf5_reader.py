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
    Lit les données des fichiers HDF5/NXS avec une seule sélection de slice et dimension,
    puis organise les layers pour chaque dataset.

    Parameters
    ----------
    paths : list[str] | str
        Chemins vers les fichiers à traiter.

    Returns
    -------
    list
        Une liste contenant des tuples pour chaque dataset.
    """

    if isinstance(paths, str):
        paths = [paths]

    if os.path.isdir(paths[0]):
        paths = read_hdf5_folder(paths[0])

    print("Paths found:", paths)

    # Sélection unique des slices et dimensions
    print("Sélection de la slice et de la dimension pour tous les fichiers.")
    slices_info = display_and_select_slices(paths[0])

    # Préparation des layers
    dataset_layers = {}  # Stockera les images par clé (dataset_key)

    for path in paths:
        
        with h5py.File(path, "r") as h5file:
            print(f"Traitement du fichier : {path}")
            datasets_3d = find_datasets_with_dim_3(h5file)

            if not datasets_3d:
                print(f"Aucun dataset 3D trouvé dans {path}.")
                continue

            for keys, shape in datasets_3d:
                if keys in slices_info:
                    slice_info = slices_info[keys]
                    slice_number = slice_info["slice"]
                    dim = slice_info["dimension"]
                    use_median = slice_info["use_median"]

                    if use_median:
                        # Calculer l'image médiane le long de l'axe spécifié
                        print("Using median filter on the slice.", path, keys)
                        data = np.median(h5file[keys], axis=dim)
                    else:
                        # Crée un index pour extraire la slice dans la dimension spécifiée
                        index = [slice(None)] * 3
                        index[dim] = slice_number
                        # Charger les données selon l'index calculé
                        data = np.array(h5file[keys][tuple(index)])

                    # Ajouter les données au dataset correspondant à la clé
                    if keys not in dataset_layers:
                        dataset_layers[keys] = []

                    dataset_layers[keys].append(data)

    # Construire les layers en empilant les données pour chaque dataset si nécessaire
    layers = []
    for dataset_key, images in dataset_layers.items():
        try:
            # Si plusieurs images, on les empile
            if len(images) > 1:
                stacked_images = np.stack(images, axis=0)
            else:
                stacked_images = images[0]  # Une seule image

        except ValueError as e:
            print(
                f"Erreur lors de l'empilement des images pour la clé {dataset_key}: {e}"
            )
            continue

        # Construire les métadonnées
        name_image = (dataset_key.strip("/").split("/"))[-1]
        metadata = {
            "slice_number": slice_number,
            "dimension": dim,
            "use_median": use_median,
            "paths": paths,
            "dataset_key": dataset_key,
            "multiscale": False,  # Toujours défini pour éviter des erreurs
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
    Trouve les chemins des datasets avec 3 dimensions dans un fichier HDF5.

    Parameters:
        file: Le fichier HDF5 ouvert (avec h5py.File).
        group: Le groupe ou chemin à explorer (None pour commencer au root).
        path: Chemin actuel dans l'arborescence.
        results: Liste pour stocker les chemins des datasets trouvés.

    Returns:
        Liste des chemins des datasets avec 3 dimensions.
    """
    if results is None:
        results = []

    if group is None:
        group = file

    for key in group:
        item = group[key]
        current_path = f"{path}/{key}"
        if isinstance(item, h5py.Group):
            # Recurse dans les sous-groupes
            find_datasets_with_dim_3(
                file, group=item, path=current_path, results=results
            )
        elif isinstance(item, h5py.Dataset):
            # Vérifie si le dataset a 3 dimensions
            if len(item.shape) == 3:
                results.append(
                    (current_path, item.shape)
                )  # Ajoute le chemin et la forme
    return results

def display_and_select_slices(file_path):
    """
    Affiche les informations sur toutes les images 3D dans une seule fenêtre Tkinter
    et permet à l'utilisateur de sélectionner une slice et une dimension pour chaque image.

    Parameters
    ----------
    file_path : str
        Chemin vers le fichier HDF5 ou Nexus.

    Returns
    -------
    dict
        Dictionnaire contenant les slices et dimensions sélectionnées pour chaque image.
        Exemple : {"/group1/image1": {"slice": 10, "dimension": 1, "use_median": False}}
    """

    def submit_selection():
        try:
            for i, (path, shape) in enumerate(datasets_3d):
                # Récupérer la slice
                slice_value = slice_entries[i].get()
                if not slice_value.isdigit() or not (
                    0 <= int(slice_value) < shape[int(dimensions[i].get())]
                ):
                    raise ValueError(
                        f"Slice invalide pour {path}. Entrez une valeur entre 0 et {shape[int(dimensions[i].get())] - 1}."
                    )

                # Récupérer la dimension
                dimension_value = dimensions[i].get()
                if dimension_value not in ("0", "1", "2"):
                    raise ValueError(
                        f"Dimension invalide pour {path}. Choisissez 0, 1 ou 2."
                    )

                # Récupérer l'option d'utilisation de la médiane
                use_median_value = use_median_vars[i].get()

                selections[path] = {
                    "slice": int(slice_value),
                    "dimension": int(dimension_value),
                    "use_median": use_median_value,
                }
            root.destroy()  # Ferme la fenêtre une fois validé
        except ValueError as e:
            messagebox.showerror("Erreur", str(e))

    try:
        with h5py.File(file_path, "r") as f:
            # Trouver tous les datasets avec 3 dimensions
            datasets_3d = find_datasets_with_dim_3(f)
            if not datasets_3d:
                messagebox.showinfo(
                    "Informations", "Aucune image 3D trouvée dans le fichier."
                )
                return {}

            # Préparation de l'interface Tkinter
            root = tk.Tk()
            root.title("Sélection des slices et dimensions")

            # Titre général
            tk.Label(
                root,
                text="Sélectionnez une slice et une dimension pour chaque image 3D",
                font=("Arial", 14),
            ).grid(row=0, column=0, columnspan=5, pady=10)

            # Tableau des informations
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

            # Initialisation des entrées
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

                # Champ pour la slice
                slice_entry = ttk.Entry(root, width=10)
                slice_entry.insert(0, "0")  # Valeur par défaut
                slice_entry.grid(row=i + 2, column=2, padx=5, pady=5)
                slice_entries.append(slice_entry)

                # Menu déroulant pour la dimension
                dimension_var = tk.StringVar(value="0")  # Valeur par défaut
                dimension_menu = ttk.Combobox(
                    root,
                    textvariable=dimension_var,
                    values=["0", "1", "2"],
                    state="readonly",
                    width=5,
                )
                dimension_menu.grid(row=i + 2, column=3, padx=5, pady=5)
                dimensions.append(dimension_var)

                # Checkbox pour l'utilisation de la médiane
                use_median_var = tk.BooleanVar()
                use_median_checkbox = ttk.Checkbutton(root, variable=use_median_var)
                use_median_checkbox.grid(row=i + 2, column=4, padx=5, pady=5)
                use_median_vars.append(use_median_var)

            # Bouton de validation
            submit_button = ttk.Button(
                root, text="Valider", command=submit_selection
            )
            submit_button.grid(
                row=len(datasets_3d) + 2, column=0, columnspan=5, pady=10
            )

            root.mainloop()
            return selections
    except Exception as e:
        messagebox.showerror("Erreur", f"Une erreur s'est produite : {e}")
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
