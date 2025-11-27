import numpy as np
from scipy.ndimage import laplace
from numpy.lib.stride_tricks import sliding_window_view

def vectorised_flow_darkfield(I_ref, I_sample, win_size=(3,3), alpha=1e-5):
    """
    Calcul du LCS entre deux images en utilisant la Single shot ou pas.
    Si LCS plusieurs position choisir taille de fenetre (1,1)
    Si single shot choisir taille de fenetre (3,3) ou plus grande.

    Args:

    I_ref (numpy.ndarray): Image de référence.
    I_sample (numpy.ndarray): Image échantillon.
    win_size (int): Taille de la fenêtre pour le calcul du flux optique.

    Returns:

    numpy.ndarray: Flux optique calculé.

    """


    if I_ref.ndim == 2:

        I_ref = I_ref[..., None] 
        I_sample = I_sample[..., None] 
        grad_y, grad_x = np.gradient(I_ref, axis=(0, 1))
        laplace_ = laplace(I_ref, axes=(0, 1), mode='reflect')




    grad_x_swv = sliding_window_view(grad_x, win_size,axis=(0, 1)) 

    grad_y_swv = sliding_window_view(grad_y, win_size,axis=(0, 1))

    ref_swv = sliding_window_view(I_ref, win_size,axis=(0, 1)) 

    sample_swv = sliding_window_view(I_sample, win_size,axis=(0, 1))

    laplace_swv = sliding_window_view(laplace_, win_size,axis=(0, 1))

    # reshape des fenêtres pour les calculs

    grad_x_swv = grad_x_swv.reshape(*grad_x_swv.shape[:-3], -1)

    grad_y_swv = grad_y_swv.reshape(*grad_y_swv.shape[:-3], -1)

    ref_swv = ref_swv.reshape(*ref_swv.shape[:-3], -1)

    sample_swv = sample_swv.reshape(*sample_swv.shape[:-3], -1)

    laplace_swv = laplace_swv.reshape(*laplace_swv.shape[:-3], -1)

    A = np.stack((ref_swv, -grad_y_swv, -grad_x_swv, laplace_swv), axis=-1)  # shape (H, W, win_size, win_size, 4)

    b = sample_swv # Calcul de la matrice A^T A et de A^T b

    ATA = np.swapaxes(A, -2, -1) @ A

    ATb = np.swapaxes(A, -2, -1) @ b[..., None]

    eye = np.eye(A.shape[-1], dtype=np.float32)  # shape (H, W, 1, 1)

    ATA += alpha * eye   # broadcast automatique sur (H, W, 3, 3)


    results = np.linalg.solve(ATA, ATb).squeeze(-1)

    results[..., 1:] /= results[..., :1] # Normalisation des composantes

    return results
