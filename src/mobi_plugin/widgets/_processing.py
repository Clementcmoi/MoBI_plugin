import napari
import numpy as np
from mbipy.numpy.phase_retrieval import lcs, lcs_df

def processing(layer_names, viewer, methode, parameters, darkfield_selected, flatfield_selected):
    """
    Fonction externe appelée par le widget.
    Parameters:
    slice_selected (str): La valeur du slice sélectionné.
    """

    images = load_images_from_layers(viewer, layer_names)  # dict

    sample = images[layer_names['sample']]
    ref = images[layer_names['reference']]
    dark = images[layer_names['darkfield']] if darkfield_selected else None
    flat = images[layer_names['flatfield']] if flatfield_selected else None

    if darkfield_selected or flatfield_selected:
        ref, sample = apply_corrections(ref, sample, dark, flat)
        
    match methode:
        case "lcs":

            # Afficher les types des variables

            result_lcs = lcs(ref, sample, alpha=float(parameters['alpha']), weak_absorption=parameters['weak_absorption'])

            name = ["abs", "dx", "dy"]

            for img in range(result_lcs.shape[2]):
                viewer.add_image(result_lcs[:, :, img], name=name[img] + methode)

        case "lcs_df":

            result_lcs_df = lcs_df(ref, sample, alpha=float(parameters['alpha']), weak_absorption=parameters['weak_absorption'])

            name = ["abs", "dx", "dy", "df"]

            for img in range(result_lcs_df.shape[2]):
                viewer.add_image(result_lcs_df[:, :, img], name=name[img] + methode)

    return 

def load_images_from_layers(viewer, layer_names):
    """
    Charge les images en mémoire à partir des layers sélectionnés dans le viewer Napari.

    Parameters:
    viewer (napari.viewer.Viewer): Instance du viewer Napari.
    layer_names (list, optional): Liste des noms des layers à charger. Si None, charge tous les layers.

    Returns:
    dict: Dictionnaire où les clés sont les noms des layers et les valeurs sont les données des images.
    """
    images = {}

    for layer in viewer.layers:
        # Vérifiez si le layer est dans la liste sélectionnée (si une liste est fournie)
        if layer_names and layer.name not in layer_names.values():
            continue

        # Vérifiez si le layer est une image
        if isinstance(layer, napari.layers.Image):
            images[layer.name] = layer.data
        else:
            print(f"Le layer '{layer.name}' n'est pas de type Image.")

    return images


def apply_corrections(ref, sample, dark, flat):
    """
    Applique les corrections darkfield et flatfield aux images de référence et d'échantillon.

    Parameters:
    ref (numpy.ndarray): Image de référence.
    sample (numpy.ndarray): Image d'échantillon.
    dark (numpy.ndarray): Image darkfield.
    flat (numpy.ndarray): Image flatfield.

    Returns:
    tuple: Tuple contenant les images corrigées dans l'ordre (ref, sample).
    """
    if dark is not None and flat is not None:
        flat_dark = flat - dark

        flat_dark[flat_dark == 0] = 1e-6

        ref = (ref - dark) / (flat_dark)
        sample = (sample - dark) / (flat_dark)

    elif dark is not None:
        ref = ref - dark
        sample = sample - dark

    elif flat is not None:

        flat[flat == 0] = 1e-6

        ref = ref / flat
        sample = sample / flat

    return ref, sample
