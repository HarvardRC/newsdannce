# calibration data classes

from dataclasses import dataclass
import numpy as np
import time


@dataclass(frozen=True)
class CameraParams:
    r_distort: np.ndarray
    t_distort: np.ndarray
    camera_matrix: np.ndarray
    rotation_matrix: np.ndarray
    translation_vector: np.ndarray


@dataclass(frozen=True)
class CalibrationData:
    """
    Complete calibration data container.
    Includes camera params (intrinsic & extrinsics), as well as metadata about the calibration process
    """

    camera_params: list[CameraParams]
    """Raw camera parameters"""

    # --- METADATA ---
    n_cameras: int
    """Number of cameras. E.g. 6"""
    camera_names: list[str]
    """Human-readible camera names e.g. \"Camera1\". The name's index in list corresponds to camera idx"""
    project_dir: str
    """Base directory of the DANNCE proejct"""
    calibration_generated_time: float
    """Timestamp the calibration was generated"""
    chessboard_square_size_mm: float
    """Chessboard square size in mm"""
    chessboard_rows: float
    """Chessboard # of rows of *internal* verticies"""
    chessboard_cols: float
    """Chessboard # of columns of *internal* verticies"""

    def __repr__(self):
        time_fmt = "%Y-%m-%d %H:%M:%S %Z"
        time_str = time.strftime(
            time_fmt, time.localtime(self.calibration_generated_time)
        )
        return f"CalibrationData <\n  n_cameras= {self.n_cameras}\n  camera_names= {self.camera_names}\n  project_dir= {self.project_dir}\n  time= {time_str}\n>"
