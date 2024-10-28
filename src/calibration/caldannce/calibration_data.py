# data classes for storing calibration parameters and metadata

import json
import logging
from pathlib import Path
import re
import time
from dataclasses import dataclass
from scipy.io import loadmat
import textwrap

import cv2
import numpy as np

from .extrinsics import ExtrinsicsParams
from .intrinsics import IntrinsicsParams
from .math_utils import is_upper

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

    def __post_init__(self):
        assert self.r_distort.shape == (2,), "r_distort must be 1d np array of size 2"
        assert self.t_distort.shape == (2,), "t_distort must be 1d np array of size 2"
        assert self.camera_matrix.shape == (3, 3), "camera matrix [k] must be 3x3 np array"
        assert self.rotation_matrix.shape == (3, 3), "Rotation matrix [r] must be 3x3 np array"
        assert self.translation_vector.shape == (3, 1), "Translation vector [t] must be a 3x1 column array"
        assert is_upper(self.camera_matrix), "Camera matrix must be upper-triangular"

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
    def from_intrinsics_extrinsics(
        intrinsics: IntrinsicsParams, extrinsics: ExtrinsicsParams
    ):
        return CameraParams(
            r_distort=intrinsics.r_distort,
            t_distort=intrinsics.t_distort,
            camera_matrix=intrinsics.camera_matrix,
            rotation_matrix=extrinsics.rotation_matrix,
            translation_vector=extrinsics.translation_vector,
        )

    @staticmethod
    def load_from_hires_file(filename):
        """Generate a CaemraParams matrix from a file path to a hires file"""
        intrinsics = IntrinsicsParams.load_from_mat_file(
            filename, cvt_from_label3d_format=True
        )
        extrinsics = ExtrinsicsParams.load_from_mat_file(filename)

        return CameraParams.from_intrinsics_extrinsics(intrinsics, extrinsics)

    @staticmethod
    def from_struct(s):
        """Create a CameraParams from a matlab/numpy struct"""

        return CameraParams(
            camera_matrix=s["K"][0, 0].reshape(3, 3),
            rotation_matrix=s["r"][0, 0].reshape(3, 3),
            translation_vector=s["t"][0, 0].reshape(
                3, 1
            ),  # ensure translation vector is column vector 3x1 not 1x3
            r_distort=s["RDistort"][0, 0].reshape(2),
            t_distort=s["TDistort"][0, 0].reshape(2),
        )

    @staticmethod
    def load_list_from_hires_folder(
        calibration_folder: str | Path,
    ) -> list["CameraParams"]:
        """Load a list of camera params from a folder containing hires_camX_params.mat files"""
        hires_folder = Path(calibration_folder)
        hires_files = [f for f in hires_folder.glob("hires_cam*params.mat")]
        if len(hires_files) == 0:
            raise Exception(
                "No valid calibration files found (format=hires_camX_params.mat where X is 1,2,3...)"
            )
        # sort the files so the hires_cam1 is before hires_cam2 (etc. )
        hires_files = sorted(
            hires_files,
            key=lambda x: int(re.match(r"hires_cam(\d+)_params.mat", x.name).group(1)),
        )
        params_list = [CameraParams.load_from_hires_file(f) for f in hires_files]
        return params_list

    @staticmethod
    def load_list_from_dannce_mat_file(
        dannce_mat_file: str | Path,
    ) -> list["CameraParams"]:
        """Load a list of camera params from a COM or DANNCE *dannce.mat file"""
        dannce_mat_file = Path(dannce_mat_file)
        mat = loadmat(dannce_mat_file)
        params = mat["params"]
        n_cams = params.shape[0]
        # return as params_list
        params_list = []
        for i in range(n_cams):
            params_list.append(CameraParams.from_struct(params[i, 0]))
        return params_list

    @staticmethod
    def load_from_dict(obj: dict) -> "CameraParams":
        """Load a single camera param object from a serializable object"""
        return CameraParams(
            r_distort=np.array(obj["r_distort"]),
            t_distort=np.array(obj["t_distort"]),
            camera_matrix=np.array(obj["camera_matrix"]),
            translation_vector=np.array(obj["translation_vector"]),
            rotation_matrix=np.array(obj["rotation_matrix"]),
        )

    @staticmethod
    def load_list_from_json_string(json_string: str) -> list["CameraParams"]:
        """Load a list of camera parameters given a json string"""
        obj = json.loads(json_string)
        n_views = len(obj)
        params_list = []
        for i in range(n_views):
            cam_i = obj[i]
            params_i = CameraParams.load_from_dict(cam_i)
            params_list.append(params_i)
        return params_list

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

    def make_projection_matrix(self):
        # rt_mtx = [ R | T ] -- (size: 3x4)
        rt_mtx = np.zeros((3, 4), dtype=np.float64)
        rt_mtx[0:3, 0:3] = self.rotation_matrix
        rt_mtx[0:3, 3:4] = self.translation_vector
        proj_mtx = self.camera_matrix @ rt_mtx
        return proj_mtx

    def project_world_point(self, world_point):
        """Projection of world point in image-space.
        World point should be a 3d (non-homogeneous) np array

        Returns a numpy vector with size 2: (u,v) in pixels
        """
        assert world_point.size == 3, "world point must have 3 fields (x,y,z)"
        world_point = world_point.reshape((3, 1))
        # use homogeneous world point: (x , y , z , 1).T
        world_point = np.vstack([world_point, 1])
        proj_mtx = self.make_projection_matrix()
        x_homog = proj_mtx @ world_point
        # convert to non-homogeneous by dividing by last entry (w)
        x = x_homog[0:2, 0] / [x_homog[2, 0]]
        x = x.reshape((2,))  # return a vector instead of a 2d matrix
        return x

    def project_multiple_world_points(self, world_points: np.ndarray):
        """Project M world_points from world coords to this camera image coords.

        World points ndarray shape: (M, 3)
        Returns an ndarray of shape: (M, 2)

        """

        m_world_points = world_points.shape[0]
        proj_points = np.zeros((m_world_points, 2))
        for i in range(m_world_points):
            proj_points[i, :] = self.project_world_point(world_points[i, :])
        return proj_points

    def as_dict(self):
        return {
            "camera_matrix": self.camera_matrix.tolist(),
            "rotation_matrix": self.rotation_matrix.tolist(),
            "translation_vector": self.translation_vector.tolist(),
            "r_distort": self.r_distort.tolist(),
            "t_distort": self.t_distort.tolist(),
        }

    def __eq__(self, other):
        attrs = [
            "camera_matrix",
            "rotation_matrix",
            "translation_vector",
            "r_distort",
            "t_distort",
        ]
        for attr in attrs:
            selfvalue = getattr(self, attr)
            othervalue = getattr(other, attr)
            if not (np.all(np.isclose(selfvalue, othervalue, rtol=1e-7, atol=1e-8))):
                return False
        return True

    def __repr__(self):
        return f"""CameraParam
 > camera_matrix [K]:
{textwrap.indent(np.array_str(self.camera_matrix, precision=3, suppress_small=True), "    ")}
 > rotation_matrix [r]:
{textwrap.indent(np.array_str(self.rotation_matrix, precision=3, suppress_small=True), "    ")}
 > translation_vector [t]:
{textwrap.indent(np.array_str(self.translation_vector, precision=3, suppress_small=True), "    ")}
 > r_distort:
 {textwrap.indent(np.array_str(self.r_distort, precision=3, suppress_small=True), "    ")}
 > t_distort:
{textwrap.indent(np.array_str(self.t_distort, precision=3, suppress_small=True), "    ")}
"""


@dataclass(frozen=True, slots=True, kw_only=True)
class CalibrationData:
    pass
    # raise NotImplementedError("CalibrationData has been depreciated. Use CustomCalibrationData instead")
    # """
    # Complete calibration data container.
    # Includes camera params (intrinsic & extrinsics), as well as metadata about the calibration process
    # """

    # camera_params: list[CameraParams]
    # """Raw camera parameters"""

    # # --- METADATA ---
    # n_cameras: int
    # """Number of cameras. E.g. 6"""
    # camera_names: list[str]
    # """Human-readible camera names e.g. \"Camera1\". The name's index in list corresponds to camera idx"""
    # intrinsics_dir: str
    # extrinsics_dir: str
    # output_dir: str
    # """Parameter output dir"""
    # calibration_generated_time: float
    # """Timestamp when calibration was generated (seconds since epoch)"""
    # chessboard_square_size_mm: float
    # """Chessboard square size in mm"""
    # chessboard_rows: float
    # """Chessboard # of rows of *internal* verticies"""
    # chessboard_cols: float
    # """Chessboard # of columns of *internal* verticies"""

    # def __repr__(self):
    #     time_fmt = "%Y-%m-%dT%H:%M:%S%Z"
    #     time_str = time.strftime(
    #         time_fmt, time.localtime(self.calibration_generated_time)
    #     )
    #     return f"CalibrationData <\n  n_cameras= {self.n_cameras}\n  camera_names= {self.camera_names}\n  intrinsics_dir= {self.intrinsics_dir}\n  extrinsics_dir= {self.extrinsics_dir}  time= {time_str}\n>"

    # def DEV_export_to_file(self, dest_file):
    #     """Development method to export calibration data in a improved format
    #     Stored in a single json file for all parameters:
    #     "calibration.json"
    #     contains the following fields:
    #     camera_params: {
    #         camera_matrix: 2D LIST (3,3) OF FLOAT
    #         r_distort: LIST(2,) FLOAT
    #         t_distort: LIST(2,) FLOAT
    #         rotation_matrix: LIST(3,3) FLOAT
    #         translation_vector: LIST(3,1) FLOAT
    #     }[]
    #     n_cameras: INTEGER
    #     camera_names: STRING[]
    #     metadata: {
    #         calibration_timestamp: INTEGER (UNIX SECONDS)
    #         calibration_repo_commit: STRING (COMMIT HASH)
    #         target_info: {
    #             rows: INTEGER
    #             cols: INTEGER
    #             square_size_mm: FLOAT
    #         }
    #     }
    #     """
     
    #     camera_params_list = []
    #     for p in self.camera_params:
    #         camera_params_list.append(
    #             {
    #                 "camera_matrix": p.camera_matrix.tolist(),
    #                 "r_distort": p.r_distort.tolist(),
    #                 "t_distort": p.t_distort.tolist(),
    #                 "rotation_matrix": p.rotation_matrix.tolist(),
    #                 "translation_vector": p.translation_vector.tolist(),
    #             }
    #         )

    #     json_data = {
    #         "camera_params": camera_params_list,
    #         "n_cameras": self.n_cameras,
    #         "camera_names": self.camera_names,
    #         "metadata": {
    #             # "intrinsics_dir": str(self.intrinsics_dir),
    #             # "extrinsics_dir": str(self.extrinsics_dir),
    #             "output_dir": str(self.output_dir),
    #             "calibration_timestamp": self.calibration_generated_time,
    #             # "caldannce_version": version_string,
    #             "target_info": {
    #                 "method": "CHESSBOARD",
    #                 "chessboard_rows": self.chessboard_rows,
    #                 "chessboard_cols": self.chessboard_cols,
    #                 "chessboard_square_size_mm": self.chessboard_square_size_mm,
    #             },
    #         },
    #     }

    #     with open(dest_file, "wt") as f:
    #         logging.debug(f"About to save to file {dest_file}")
    #         try:
    #             json.dump(json_data, f)
    #         except BaseException as e:
    #             logging.error(f"Unable to save json calibration file. Error= {e}" )
    #         logging.info(f"Saved calibration.json to file:{dest_file}")
