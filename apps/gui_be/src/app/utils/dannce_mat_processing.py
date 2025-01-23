from pathlib import Path
from scipy.io import loadmat
import numpy as np
from dataclasses import dataclass, replace
import re
from datetime import datetime

from caldannce.calibration_data import CameraParams


@dataclass
class MatFileInfo:
    n_cameras: int
    n_frames: int
    n_joints: int
    params: list[CameraParams]
    """Calibration params"""
    path: str
    filename: str
    is_com: bool
    timestamp: int

    def without_params(self):
        # Return a clone of this object without the params dict
        return replace(self, params=None)


def process_label_mat_file(matfile_path) -> MatFileInfo:
    p = Path(matfile_path)
    filename = p.name
    match = re.match(
        r"(\d\d\d\d)(\d\d)(\d\d)_(\d\d)(\d\d)(\d\d)_(?:(.+)_Label3D_)?dannce.mat",
        filename,
    )
    if not match:
        return None
    mat = loadmat(matfile_path)
    n_cameras = mat["params"].shape[0]
    n_joints = mat["labelData"][0, 0]["data_3d"][0, 0].shape[1] // 3
    n_frames = mat["labelData"][0, 0]["data_3d"][0, 0].shape[0]
    is_com = n_joints == 1
    params = []

    time_segments = [int(match[i]) for i in range(1, 7)]
    dt = datetime(
        year=time_segments[0],
        month=time_segments[1],
        day=time_segments[2],
        hour=time_segments[3],
        minute=time_segments[4],
        second=time_segments[5],
    )
    timestamp = dt.timestamp()

    for i in range(n_cameras):
        cam_params = CameraParams.from_struct(mat["params"][i, 0])
        params.append(cam_params.as_dict())

    info = MatFileInfo(
        n_cameras=n_cameras,
        n_joints=n_joints,
        n_frames=n_frames,
        params=params,
        path=matfile_path,
        filename=filename,
        is_com=is_com,
        timestamp=timestamp,
    )
    return info


def get_labeled_data_in_dir(video_folder_id, video_folder_path):
    maybe_label_data: list[MatFileInfo] = []
    for i in Path(video_folder_path).glob("*dannce.mat"):
        this_label_data = process_label_mat_file(str(i))
        if this_label_data:
            maybe_label_data.append(this_label_data)

    return maybe_label_data


def get_predicted_data_in_dir(video_folder_id, video_folder_path):
    com_folders = []
    dannce_folders = []

    for i in Path(video_folder_path, "COM").glob("**/com3d.mat"):
        com_folders.append(str(i))
    for i in Path(video_folder_path, "DANNCE").glob("**/save_data_AVG0.mat"):
        dannce_folders.append(str(i))

    return {"com_predictions": com_folders, "dannce_predictions": dannce_folders}


def get_com_pred_data_3d(com3d_file: Path, frames: list[int]) -> np.ndarray:
    """Get 3d data from COM predictions file.

    OUTPUT SHAPE (n_frames, n_joints[1], n_dims[3])
    Return (n_frames x 3 x1) ndarray. Rows=n_frames; Cols=3"""
    mat = loadmat(com3d_file)
    # now you have a VIDOE_FRAMES x 3 shaped ndarray
    # index by frames list
    com_data = mat["com"][frames, np.newaxis, :]
    # com_data = np.transpose(com_data, (0,))

    return com_data


def get_dannce_pred_data_3d(dannce_pred_file: Path, frames: list[int]) -> np.ndarray:
    """Get 3d data from DANNCE predictions file.

    OUTPUT SHAPE (n_frames, n_joints, n_dims[3])
    Return (n_frames x 3 x n_joints) ndarray. Rows=n_frames; Cols=3"""
    mat = loadmat(dannce_pred_file)
    # now you have a VIDOE_FRAMES x 3 shaped ndarray
    # index by frames list
    # pred array (n_framesn, n_animals, n_dims, n_joints)
    dannce_data = mat["pred"][frames, 0, :, :]
    dannce_data = np.transpose(dannce_data, (0, 2, 1))
    return dannce_data


# def get_pred_3d_data(prediction_file: Path) -> np.ndarray:
#     mat = loadmat(matfile_path)
#     n_joints = mat["pred"][0, 0]["data_3d"][0, 0].shape[1] // 3
