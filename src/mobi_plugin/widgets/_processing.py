import napari
import numpy as np
from mbipy.numpy.phase_retrieval import lcs, lcs_df
from mbipy.src.normal_integration.fourier import kottler, frankot
from mbipy.cupy.phase_retrieval import cst_csvt
from ..popcorn.LCS_DirDF import processProjectionLCS_DDF
from ._utils import Experiment, Parameters

def apply_corrections(viewer, layer_names):
    """
    Apply flatfield and darkfield corrections to the sample and reference layers.
    """
    sample_layer = viewer.layers[layer_names['sample']].data
    reference_layer = viewer.layers[layer_names['reference']].data

    if 'darkfield' in layer_names:
        darkfield_layer = viewer.layers[layer_names['darkfield']].data
        sample_layer = sample_layer - darkfield_layer
        reference_layer = reference_layer - darkfield_layer

    if 'flatfield' in layer_names:
        flatfield_layer = viewer.layers[layer_names['flatfield']].data
        sample_layer = sample_layer / flatfield_layer
        reference_layer = reference_layer / flatfield_layer

    return sample_layer, reference_layer

def apply_phase(result, phase_parameters):
    """
    Apply phase calculation based on the provided phase parameters.
    """
    if phase_parameters['method'] == 'Kottler':
        return kottler(result[1], result[2], pad=phase_parameters['pad'])
    elif phase_parameters['method'] == 'Frankot_Chellappa':
        return frankot(result[1], result[2], pad=phase_parameters['pad'])
    else:
        raise ValueError(f"Unknown phase retrieval method: {phase_parameters['method']}")
    
def add_image_to_layer(results, names, method, viewer):
    """
    Add the resulting image to the viewer as a new layer.
    """
    for image, name in (results, names):
        viewer.add_image(image, name=name + "_" + method)


def processing(params):
    viewer = params['viewer']
    experiment = params['parameters']
    layer_names = params['layer_names']

    # Apply corrections to the sample and reference layers
    sample_layer, reference_layer = apply_corrections(viewer, layer_names)

    # Call the appropriate processing function
    if experiment.method == 'lcs':
        result = lcs(sample_layer, reference_layer, experiment.alpha, experiment.weak_absorption)
        names = ["abs", "dx", "dy"]
    else:
        raise ValueError(f"Unknown method: {experiment.method}")

    # Calculate the phase if phase_parameters are provided
    if experiment.phase_parameters:
        phase = apply_phase(result, experiment.phase_parameters)
        phase_layer = viewer.add_image(phase, name=f"{layer_names['sample']}_phase")

    # Save the resulting images back to the layers
    result_layer = add_image_to_layer(result, names, experiment.method, viewer)

    return result

