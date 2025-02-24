import numpy as np
from mbipy.numpy.phase_retrieval import lcs
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
        return kottler(result[2], result[1], pad=phase_parameters['pad'])
    elif phase_parameters['method'] == 'Frankot_Chellappa':
        return frankot(result[2], result[1], pad=phase_parameters['pad'])
    else:
        raise ValueError(f"Unknown phase retrieval method: {phase_parameters['method']}")

def add_image_to_layer(results, names, method, viewer):
    """
    Add the resulting image to the viewer as a new layer.
    """
    for image, name in zip(results, names):
        viewer.add_image(image, name=name + "_" + method)

def processing(params):
    viewer = params['viewer']
    experiment = params['parameters']
    layer_names = params['layer_names']

    # Apply corrections to the sample and reference layers
    sample_layer, reference_layer = apply_corrections(viewer, layer_names)

    # Call the appropriate processing function
    try:
        if experiment.method == 'lcs':
            result = lcs(reference_layer, sample_layer, alpha=experiment.alpha, weak_absorption=experiment.weak_absorption)
            result = np.moveaxis(result, -1, 0)
            names = ["abs", "dx", "dy"]
        else:
            raise ValueError(f"Unknown method: {experiment.method}")
    except Exception as e:
        print(f"Error during LCS processing: {e}")
        import traceback
        traceback.print_exc()
        return

    # Calculate the phase if phase_parameters are provided
    if experiment.phase_parameters:
        try:
            phase = apply_phase(result, experiment.phase_parameters)
            phase_layer = viewer.add_image(phase, name=f"{layer_names['sample']}_phase")
        except Exception as e:
            print(f"Error during phase calculation: {e}")
            traceback.print_exc()

    # Save the resulting images back to the layers
    try:
        print("Result shape: ", result.shape)
        result_layer = add_image_to_layer(result, names, experiment.method, viewer)
    except Exception as e:
        print(f"Error adding image to layer: {e}")
        traceback.print_exc()

    return result

