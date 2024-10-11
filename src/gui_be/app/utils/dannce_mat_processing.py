from pathlib import Path
from fastapi.background import P
from scipy.io import loadmat
import numpy as np
from dataclasses import dataclass
import re
from datetime import datetime


@dataclass
class CameraParam:
    K: np.ndarray
    r: np.ndarray
    t: np.ndarray
    RDistort: np.ndarray
    TDistort: np.ndarray

    def from_struct(s):
        return CameraParam(
            s["K"][0, 0],
            s["r"][0, 0],
            s["t"][0, 0],
            s["RDistort"][0, 0],
            s["TDistort"][0, 0],
        )

    def as_dict(self):
        return {
            "K": self.K.tolist(),
            "r": self.r.tolist(),
            "t": self.t.tolist(),
            "RDistort": self.RDistort.tolist(),
            "TDistort": self.TDistort.tolist(),
        }


@dataclass
class MatFileInfo:
    n_cameras: int
    n_frames: int
    n_joints: int
    params: dict
    path: str
    filename: str
    is_com: bool
    timestamp: int


def process_label_mat_file(matfile_path):
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
        cam_params = CameraParam.from_struct(mat["params"][i, 0])
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
    maybe_label_data = []
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
    for i in Path(video_folder_path, "DANNCE").glob("**/save_data_AVG.mat"):
        dannce_folders.append(str(i))

    return {"com_predictions": com_folders, "dannce_predictions": dannce_folders}
