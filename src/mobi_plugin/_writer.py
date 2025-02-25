"""
This module is an example of a barebones writer plugin for napari.

It implements the Writer specification.
see: https://napari.org/stable/plugins/guides.html?#writers

Replace code below according to your needs.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING, Any, Union
from fabio import tifimage
from imageio import imwrite
import os
from pathlib import Path

if TYPE_CHECKING:
    DataType = Union[Any, Sequence[Any]]
    FullLayerData = tuple[DataType, dict, str]


def write_single_image(path: str, data: Any, meta: dict) -> list[str]:
    """Writes a single image layer.

    Parameters
    ----------
    path : str
        A string path indicating where to save the image file.
    data : The layer data
        The `.data` attribute from the napari layer.
    meta : dict
        A dictionary containing all other attributes from the napari layer
        (excluding the `.data` layer attribute).

    Returns
    -------
    [path] : A list containing the string path to the saved file.
    """
    
    saved_paths = []

    print("Dimension", data.ndim)

    if data.ndim >= 3:
        print("Saving all slices of a 3D image : ", data.shape)
        dir_path = Path(path).with_suffix('')
        dir_path.mkdir(parents=True, exist_ok=True)

        for i in range(data.shape[0]):
            slice_path = dir_path / f"slice_{i}.tif"
            saved_paths.append(write_tif(slice_path, data[i], meta))
                
    else:
        print("Saving 2D image : ", data.shape)
        saved_paths.append(write_tif(path, data, meta))

    return saved_paths


def write_multiple(path: str, data: list[FullLayerData]) -> list[str]:
    """Writes multiple layers of different types.

    Parameters
    ----------
    path : str
        A string path indicating where to save the data file(s).
    data : A list of layer tuples.
        Tuples contain three elements: (data, meta, layer_type)
        `data` is the layer data
        `meta` is a dictionary containing all other metadata attributes
        from the napari layer (excluding the `.data` layer attribute).
        `layer_type` is a string, eg: "image", "labels", "surface", etc.

    Returns
    -------
    [path] : A list containing (potentially multiple) string paths to the saved file(s).
    """
    print("multiple images")
    saved_paths = []
    for i, (layer_data, meta, layer_type) in enumerate(data):
        if layer_data.ndim not in (2, 3):
            raise ValueError(f"Unsupported number of dimensions: {layer_data.ndim}. Expected 2D or 3D data.")

        layer_path = f"{path}_layer_{i}"
        if layer_data.ndim == 3:
            dir_path = Path(layer_path)
            dir_path.mkdir(parents=True, exist_ok=True)

            for j in range(layer_data.shape[0]):
                slice_path = dir_path / f"slice_{j}.tif"
                tif = tifimage.tifimage(layer_data[j])
                tif.write(slice_path)
                saved_paths.append(str(slice_path))
        else:
            tif = tifimage.tifimage(layer_data)
            tif.write(f"{layer_path}.tif")
            saved_paths.append(f"{layer_path}.tif")

    return saved_paths


def write_tif(path, data, meta):
    tif = tifimage.tifimage(data)

    print(meta)

    for key, value in meta.items():
        tif.header[key] = value

    tif.write(path)

    return path
