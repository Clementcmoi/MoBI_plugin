import h5py
import numpy as np
import glob
import os
from PyQt5.QtWidgets import (
    QApplication, QDialog, QLabel, QVBoxLayout, QHBoxLayout, QPushButton,
    QLineEdit, QComboBox, QCheckBox, QFileDialog, QFormLayout, QMessageBox
)
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

class SliceSelectionDialog(QDialog):
    def __init__(self, datasets_3d):
        super().__init__()
        self.setWindowTitle("Sélection des slices et dimensions")
        self.datasets_3d = datasets_3d
        self.selections = {}

        layout = QVBoxLayout()
        form_layout = QFormLayout()

        self.slice_inputs = {}
        self.dimension_inputs = {}
        self.median_checks = {}

        for path, shape in datasets_3d:
            row_layout = QHBoxLayout()
            
            label = QLabel(f"{path} - Dimensions: {shape}")
            slice_input = QLineEdit("0")
            dimension_input = QComboBox()
            dimension_input.addItems(["0", "1", "2"])
            median_check = QCheckBox("Utiliser médiane")
            
            self.slice_inputs[path] = slice_input
            self.dimension_inputs[path] = dimension_input
            self.median_checks[path] = median_check

            form_layout.addRow(label, slice_input)
            form_layout.addRow(QLabel("Dimension :"), dimension_input)
            form_layout.addRow(QLabel("Filtre médian :"), median_check)

        layout.addLayout(form_layout)
        
        submit_button = QPushButton("Valider")
        submit_button.clicked.connect(self.submit_selection)
        layout.addWidget(submit_button)

        self.setLayout(layout)

    def submit_selection(self):
        try:
            for path, shape in self.datasets_3d:
                slice_value = int(self.slice_inputs[path].text())
                dimension_value = int(self.dimension_inputs[path].currentText())
                use_median = self.median_checks[path].isChecked()

                if not (0 <= slice_value < shape[dimension_value]):
                    raise ValueError(f"Slice invalide pour {path}. Doit être entre 0 et {shape[dimension_value] - 1}.")

                self.selections[path] = {
                    "slice": slice_value,
                    "dimension": dimension_value,
                    "use_median": use_median,
                }
            self.accept()
        except ValueError as e:
            QMessageBox.critical(self, "Erreur", str(e))

from PyQt5.QtWidgets import QApplication

def display_and_select_slices(file_path):
    with h5py.File(file_path, "r") as f:
        datasets_3d = find_datasets_with_dim_3(f)
        if not datasets_3d:
            QMessageBox.information(None, "Informations", "Aucune image 3D trouvée dans le fichier.")
            return {}

        app = QApplication.instance()  # Vérifie si QApplication existe déjà
        if app is None:
            app = QApplication([])

        dialog = SliceSelectionDialog(datasets_3d)
        if dialog.exec_():
            return dialog.selections
        return {}

def read_hdf5_folder(path):
    app = QApplication.instance()  # Vérifie si QApplication existe déjà
    if app is None:
        app = QApplication([])

    file_dialog = QFileDialog()
    file_dialog.setFileMode(QFileDialog.ExistingFiles)
    file_dialog.setNameFilter("HDF5 Files (*.hdf5 *.nxs *.h5)")
    if file_dialog.exec_():
        return file_dialog.selectedFiles()
    return []

