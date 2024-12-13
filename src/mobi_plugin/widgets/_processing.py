import napari
from mbipy.numpy.phase_retrieval import lcs, lcs_df


def processing(layer_names, slice_selected, viewer):
    """
    Fonction externe appelée par le widget.
    Parameters:
    slice_selected (str): La valeur du slice sélectionné.
    """
    print(f"Fonction externe appelée avec slice : {slice_selected} et {layer_names}")

    images = load_images_from_layers(viewer, layer_names) #dict

    sample = images[layer_names[0]]
    ref = images[layer_names[1]]
    dark = images[layer_names[2]]
    
    ref = ref - dark
    sample = sample - dark

    result_lcs = lcs(ref, sample, alpha=1e-5, weak_absorption=False)
    result_lcs_df = lcs_df(ref, sample, alpha=1e-5, weak_absorption=False)

    abs_LCS = result_lcs_df[:,:,0]
    dx_LCS = result_lcs_df[:,:,1]
    dy_LCS = result_lcs_df[:,:,2]
    df = result_lcs_df[:,:,3]

    print(abs_LCS.shape)

    # Ajouter les images corrigées au viewer
    viewer.add_image(abs_LCS, name="abs")
    viewer.add_image(dx_LCS, name="dx")
    viewer.add_image(df, name="df")

    print("Images corrigées ajoutées au viewer.")

    # Retourner les données pour débogage ou usage ultérieur
    return {
        "sample_corrected": abs_LCS,
        "ref_corrected": dx_LCS,
        "dark": df,
    }



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
        if layer_names and layer.name not in layer_names:
            continue

        # Vérifiez si le layer est une image
        if isinstance(layer, napari.layers.Image):
            images[layer.name] = layer.data
        else:
            print(f"Le layer '{layer.name}' n'est pas de type Image.")

    return images
