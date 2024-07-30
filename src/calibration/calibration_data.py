# data classes for storing calibration parameters and metadata

import json
import logging
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

    @staticmethod
    def compare(A: "CameraParams", B: "CameraParams"):
        """Compare two CameraParams objects for equality (within a floating point tolerance)
        By default this tolerance is 1e-05 relative + 1e-08 absolute"""
        sames = [
            np.all(np.isclose(A.camera_matrix, B.camera_matrix)),
            np.all(np.isclose(A.r_distort, B.r_distort)),
            np.all(np.isclose(A.t_distort, B.t_distort)),
            np.all(np.isclose(A.rotation_matrix, B.rotation_matrix)),
            np.all(np.isclose(A.translation_vector, B.translation_vector)),
        ]
        return all(sames)


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
    intrinsics_dir: str
    extrinsics_dir: str
    output_dir: str
    """Parameter output dir"""
    calibration_generated_time: float
    """Timestamp when calibration was generated (seconds since epoch)"""
    chessboard_square_size_mm: float
    """Chessboard square size in mm"""
    chessboard_rows: float
    """Chessboard # of rows of *internal* verticies"""
    chessboard_cols: float
    """Chessboard # of columns of *internal* verticies"""

    def __repr__(self):
        time_fmt = "%Y-%m-%dT%H:%M:%S%Z"
        time_str = time.strftime(
            time_fmt, time.localtime(self.calibration_generated_time)
        )
        return f"CalibrationData <\n  n_cameras= {self.n_cameras}\n  camera_names= {self.camera_names}\n  intrinsics_dir= {self.intrinsics_dir}\n  extrinsics_dir= {self.extrinsics_dir}  time= {time_str}\n>"

    def DEV_export_to_file(self, dest_file):
        """Development method to export calibration data in a improved format
        Stored in a single h5 file for all parameters:
        "calibration.json"
        contains the following fields:
        camera_params: {
            camera_matrix: [3x3] FLOAT
            r_distort: [1x2] FLOAT
            t_distort: [1x2] FLOAT
            rotation_matrix: [3x3] FLOAT
            translation_vector: [3x1] FLOAT
        }[]
        n_cameras: INTEGER
        camera_names: STRING[]
        metadata: {
            calibration_timestamp: INTEGER (UNIX SECONDS)
            calibration_repo_commit: STRING (COMMIT HASH)
            target_info: {
                rows: INTEGER
                cols: INTEGER
                square_size_mm: FLOAT
            }
        }
        """
        # import inside fn to avoid circular import
        from src.calibration.project_utils import get_repo_commit_sha

        camera_params_list = []
        for p in self.camera_params:
            camera_params_list.append(
                {
                    "camera_matrix": p.camera_matrix.tolist(),
                    "r_distort": p.r_distort.tolist(),
                    "t_distort": p.t_distort.tolist(),
                    "rotation_matrix": p.rotation_matrix.tolist(),
                    "translation_vector": p.translation_vector.tolist(),
                }
            )

        json_data = {
            "camera_params": camera_params_list,
            "n_cameras": self.n_cameras,
            "camera_names": self.camera_names,
            "metadata": {
                "intrinsics_dir": str(self.intrinsics_dir),
                "extrinsics_dir": str(self.extrinsics_dir),
                "output_dir": str(self.output_dir),
                "calibration_timestamp": self.calibration_generated_time,
                "calibration_repo_commit": get_repo_commit_sha(),
                "target_info": {
                    "chessboard_rows": self.chessboard_rows,
                    "chessboard_cols": self.chessboard_cols,
                    "chessboard_square_size_mm": self.chessboard_square_size_mm,
                },
            },
        }

        logging.debug(f"JSON DATA {json_data}")

        with open(dest_file, "w") as f:
            logging.debug(f"About to save to file {dest_file}")
            json.dump(json_data, f)
            logging.info(f"Saved calibration.json to file:{dest_file}")
