import numpy as np
from mbipy.numpy.phase_retrieval import lcs
from mbipy.src.normal_integration.fourier import kottler, frankot
from ..popcorn.LCS_DirDF import processProjectionLCS_DDF
from ..popcorn.LCS_DF import process_projection_LCS_DF
from ..popcorn.MISTI import MISTI
from ..popcorn.MISTII_1 import processProjectionMISTII_1
from ..popcorn.MISTII_2 import processProjectionMISTII_2
from ..popcorn.Pavlov2020 import tie_Pavlovetal2020
from ..popcorn.XSVT import processProjectionXSVT
from ..popcorn.ReverseFlow_LCS import processProjection_rLCS
from ..popcorn.speckle_matching import processProjectionUMPA
from ._utils import Experiment  # Correct import

def apply_corrections(viewer, experiment):
    """
    Appliquer les corrections flatfield et darkfield aux couches sample et reference 
    en utilisant les données stockées dans l'objet experiment.
    """
    print("Applying corrections")
    sample_layer = viewer.layers[experiment.sample_images].data
    reference_layer = viewer.layers[experiment.reference_images].data

    if experiment.darkfield is not None:
        darkfield_layer = viewer.layers[experiment.darkfield].data
        sample_layer = sample_layer - darkfield_layer
        reference_layer = reference_layer - darkfield_layer

    if experiment.flatfield is not None:
        flatfield_layer = viewer.layers[experiment.flatfield].data
        sample_layer = sample_layer / flatfield_layer
        reference_layer = reference_layer / flatfield_layer

    return sample_layer, reference_layer

def apply_phase(result, phase_parameters):
    """
    Apply phase calculation based on the provided phase parameters.
    """
    if phase_parameters['method'] == 'Kottler':
        return kottler(result['dy'], result['dx'], pad=phase_parameters['pad'])
    elif phase_parameters['method'] == 'Frankot_Chellappa':
        return frankot(result['dy'], result['dx'], pad=phase_parameters['pad'])
    else:
        raise ValueError(f"Unknown phase retrieval method: {phase_parameters['method']}")

def add_image_to_layer(results, method, viewer):
    """
    Add the resulting image to the viewer as a new layer.
    """
    for name, image in results.items():
        viewer.add_image(image.real, name=f"{name}_{method}")

def processing(experiment, viewer):
    """
    Traiter les données en utilisant les paramètres contenus dans l'objet experiment.
    Le viewer est utilisé pour accéder aux données des couches et pour ajouter les images résultantes.
    """
    # Appliquer les corrections à partir des données contenues dans experiment
    
    sample_layer, reference_layer = apply_corrections(viewer, experiment)

    experiment.sample_images = sample_layer
    experiment.reference_images = reference_layer

    try:
        print(f"Processing with method: {experiment.method}")
        if experiment.method == 'lcs':
            result = lcs(reference_layer, sample_layer, alpha=experiment.alpha, weak_absorption=experiment.weak_absorption)
            result = np.moveaxis(result, -1, 0)
            result = {'abs': result[0], 'dx': result[1], 'dy': result[2]}
        elif experiment.method == 'lcs_df':
            result = process_projection_LCS_DF(experiment)
        elif experiment.method == 'lcs_dirdf':
            result = processProjectionLCS_DDF(experiment)
        elif experiment.method == 'misti':
            result = MISTI(experiment)
        elif experiment.method == 'mistii1':
            result = processProjectionMISTII_1(experiment)
        elif experiment.method == 'mistii2':
            result = processProjectionMISTII_2(experiment)
        elif experiment.method == 'pavlov2020':
            result = tie_Pavlovetal2020(experiment)
        elif experiment.method == 'xsvt':
            result = processProjectionXSVT(experiment)
        elif experiment.method == 'reversflowlcs':
            result = processProjection_rLCS(experiment)
        elif experiment.method == 'specklematching':
            result = processProjectionUMPA(experiment)
        else:
            raise ValueError(f"Unknown method: {experiment.method}")
    except Exception as e:
        print(f"Error during processing: {e}")
        import traceback
        traceback.print_exc()
        return

    # Si des paramètres de phase sont définis, calculer la phase
    if experiment.phase_parameters:
        try:
            phase = apply_phase(result, experiment.phase_parameters)
            # Le nom de la couche phase est basé sur le nom de la couche sample
            viewer.add_image(phase, name=f"{experiment.method}_phase")
        except Exception as e:
            print(f"Error during phase calculation: {e}")
            import traceback
            traceback.print_exc()

    # Ajouter les images résultantes au viewer
    try:
        add_image_to_layer(result, experiment.method, viewer)
    except Exception as e:
        print(f"Error adding image to layer: {e}")
        import traceback
        traceback.print_exc()

    return result


