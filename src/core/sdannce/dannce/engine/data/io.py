"""Data loading and saving operations."""

import mat73
import numpy as np
import scipy.io as sio


def load_label3d_data(path: str, key: str):
    """Load Label3D data

    Args:
        path (str): Path to Label3D file
        key (str): Field to access

    Returns:
        TYPE: Data from field
    """
    try:
        d = sio.loadmat(path)[key]
        dataset = [f[0] for f in d]

        # Data are loaded in this annoying structure where the array
        # we want is at dataset[i][key][0,0], as a nested array of arrays.
        # Simplify this structure (a numpy record array) here.
        # Additionally, cannot use views here because of shape mismatches. Define
        # new dict and return.
        data = []
        for d in dataset:
            d_ = {}
            for key in d.dtype.names:
                d_[key] = d[key][0, 0]
            data.append(d_)
    except Exception:
        d = mat73.loadmat(path)[key]
        data = [f[0] for f in d]
    return data


def load_camera_params(path: str) -> list[dict]:
    """Load camera parameters from Label3D file.

    Args:
        path (str): Path to Label3D file

    Returns:
        list[dict]: List of camera parameter dictionaries.
    """
    params = load_label3d_data(path, "params")
    for p in params:
        if "r" in p:
            p["R"] = p["r"]
        if len(p["t"].shape) == 1:
            p["t"] = p["t"][np.newaxis, ...]
    return params


def load_sync(path: str) -> list[dict]:
    """Load synchronization data from Label3D file.

    Args:
        path (str): Path to Label3D file.

    Returns:
        list[dict]: List of synchronization dictionaries.
    """
    dataset = load_label3d_data(path, "sync")
    for d in dataset:
        d["data_frame"] = d["data_frame"].astype(int)
        d["data_sampleID"] = d["data_sampleID"].astype(int)
    return dataset


def load_labels(path: str) -> list[dict]:
    """Load labelData from Label3D file.

    Args:
        path (str): Path to Label3D file.

    Returns:
        list[dict]: List of labelData dictionaries.
    """
    dataset = load_label3d_data(path, "labelData")
    for d in dataset:
        d["data_frame"] = d["data_frame"].astype(int)
        d["data_sampleID"] = d["data_sampleID"].astype(int)
    return dataset


def load_com(path: str) -> dict:
    """Load COM from .mat file.

    Args:
        path (str): Path to .mat file with "com" field

    Returns:
        dict: Dictionary with com data
    """
    try:
        d = sio.loadmat(path)["com"]
        data = {}
        data["com3d"] = d["com3d"][0, 0]
        data["sampleID"] = d["sampleID"][0, 0].astype(int)
    except Exception:
        data = mat73.loadmat(path)["com"]
        data["sampleID"] = data["sampleID"].astype(int)
    return data


def load_camnames(path: str) -> list | None:
    """Load camera names from .mat file.

    Args:
        path (str): Path to .mat file with "camnames" field

    Returns:
        list | None: List of cameranames
    """
    try:
        label_3d_file = sio.loadmat(path)
        if "camnames" in label_3d_file:
            names = label_3d_file["camnames"][:]
            if len(names) != len(label_3d_file["labelData"]):
                camnames = [name[0] for name in names[0]]
            else:
                camnames = [name[0][0] for name in names]
        else:
            camnames = None
    except Exception:
        label_3d_file = mat73.loadmat(path)
        if "camnames" in label_3d_file:
            camnames = [name[0] for name in label_3d_file["camnames"]]
    return camnames
