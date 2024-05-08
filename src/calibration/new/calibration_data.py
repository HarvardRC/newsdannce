# calibration data classes

import time
from dataclasses import dataclass

import cv2
import numpy as np

from .extrinsics import ExtrinsicsParams
from .intrinsics import IntrinsicsParams


@dataclass(frozen=True, slots=True, kw_only=True)
class CameraParams:
    r_distort: np.ndarray
    t_distort: np.ndarray
    camera_matrix: np.ndarray
    """3x3 ndarray matrix"""
    rotation_matrix: np.ndarray
    """3x3 ndarray matrix"""
    translation_vector: np.ndarray
    """3x1 ndarray matrix"""

    @property
    def dist(self) -> np.ndarray:
        """Returns a dist array formatted as [k1 k2 p1 p2 [k3]]. Note k3 is optional and not genereated
        This format is expected by some cv2 functions which use camera parameters (intrinsics)"""
        return np.hstack([self.r_distort, self.t_distort])

    @property
    def rvec(self) -> np.ndarray:
        """Genereate a rotation vector from the camera's intrinsic matrix (k). This the Rodrigues function
        This format is expected by some cv2 functions e.g. projectPoints"""
        rotation_vector, jacobian = cv2.Rodrigues(self.rotation_matrix)
        return rotation_vector

    @staticmethod
    def load_from_hires_file(filename):
        """Generate a CaemraParams matrix from a file path to a hires file"""
        intrinsics = IntrinsicsParams.load_from_mat_file(
            filename, cvt_matlab_to_cv2=False
        )
        extrinsics = ExtrinsicsParams.load_from_mat_file(filename)

        return CameraParams(
            r_distort=intrinsics.r_distort,
            t_distort=intrinsics.t_distort,
            camera_matrix=intrinsics.camera_matrix,
            rotation_matrix=extrinsics.rotation_matrix,
            translation_vector=extrinsics.translation_vector,
        )


@dataclass(frozen=True, slots=True, kw_only=True)
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
    output_dir: str
    """Parameter output dir"""

    def __repr__(self):
        time_fmt = "%Y-%m-%d %H:%M:%S %Z"
        time_str = time.strftime(
            time_fmt, time.localtime(self.calibration_generated_time)
        )
        return f"CalibrationData <\n  n_cameras= {self.n_cameras}\n  camera_names= {self.camera_names}\n  project_dir= {self.project_dir}\n  time= {time_str}\n>"
