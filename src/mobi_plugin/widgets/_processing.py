import napari
import numpy as np
from mbipy.numpy.phase_retrieval import lcs, lcs_df
from mbipy.src.normal_integration.fourier import kottler, frankot
from mbipy.cupy.phase_retrieval import cst_csvt

def processing(params):
    """
    Fonction externe appelée par le widget.
    Parameters:
    params (dict): Dictionnaire contenant les paramètres nécessaires.
    """
    print(params) # debug

    images = load_images_from_layers(params['viewer'], params['layer_names'])  # dict

    sample = images[params['layer_names']['sample']]
    ref = images[params['layer_names']['reference']]
    dark = images[params['layer_names']['darkfield']] if params['darkfield_selected'] else None
    flat = images[params['layer_names']['flatfield']] if params['flatfield_selected'] else None

    if params['darkfield_selected'] or params['flatfield_selected']:
        ref, sample = apply_corrections(ref, sample, dark, flat)

    pad = "antisym" if params['pad'] else None
        
    match params['method']:
        case "lcs":
            result_lcs = lcs(ref, sample, alpha=float(params['parameters']['alpha']), weak_absorption=params['parameters']['weak_absorption'])
            name = ["abs", "dx", "dy"]

            if params['phase_retrieval_method'] is not None:
                result_phase = phase_retrieval(result_lcs, params['phase_retrieval_method'], pad)
                print(result_phase.shape) # debug
                name.append("phase")

            for img_idx in range(len(name)):
                if img_idx < 3:
                    params['viewer'].add_image(result_lcs[:, :, img_idx], name=name[img_idx] + "_" + params['method'])
                else:
                    params['viewer'].add_image(result_phase, name=name[img_idx] + "_" + params['method'])

        case "lcs_df":
            result_lcs_df = lcs_df(ref, sample, alpha=float(params['parameters']['alpha']), weak_absorption=params['parameters']['weak_absorption'])
            name = ["abs", "dx", "dy", "df"]

            if params['phase_retrieval_method'] is not None:
                result_phase = phase_retrieval(result_lcs_df, params['phase_retrieval_method'], pad)
                print(result_phase.shape) # debug
                name.append("phase")

            for img_idx in range(len(name)):
                if img_idx < 4:
                    params['viewer'].add_image(result_lcs_df[:, :, img_idx], name=name[img_idx] + "_" + params['method'])
                else:
                    params['viewer'].add_image(result_phase, name=name[img_idx] + "_" + params['method'])

        case "cst_csvt":
            result_cst_csvt = cst_csvt(ref, sample, int(params['parameters']['window_size']), (params['parameters']['pixel_shift']))

            print(result_cst_csvt.shape) # debug

            name = ["abs", "dx", "dy"]

            if params['phase_retrieval_method'] is not None:
                result_phase = phase_retrieval(result_cst_csvt, params['phase_retrieval_method'], pad)
                name.append("phase")

            for img_idx in range(len(name)):
                if img_idx < 3:
                    params['viewer'].add_image(result_cst_csvt[:, :, img_idx], name=name[img_idx] + "_" + params['method'])
                else:
                    params['viewer'].add_image(result_phase, name=name[img_idx] + "_" + params['method'])

    return 

def phase_retrieval(result_lcs, phase_retrieval_method, pad):
    gy = result_lcs[:, :, 2]
    gx = result_lcs[:, :, 1]

    match phase_retrieval_method:
        case "Kottler":
            result = kottler(gy, gx, pad=pad)
        case "Frankot_Chellappa":
            result = frankot(gy, gx, pad=pad)

    return result

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
