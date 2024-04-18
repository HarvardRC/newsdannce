from dataclasses import dataclass
import numpy as np
from src.calibration.new.intrinsics import IntrinsicsParams
from src.calibration.new.video_utils import get_first_frame_video
import cv2
from .math_utils import calculate_rpe
from scipy.io import loadmat
import logging


@dataclass(frozen=True, slots=True, kw_only=True)
class ExtrinsicsParams:
    """Camera extrinsics parameters:
    - rotation_matrix: 3x3 rotation transformation matrix - np.ndarray, Size=(3,3). AKA "r"
    - translation_vector: [tx, ty, tz] - np.ndarray, Size=(3,). AKA "t"
    """

    rotation_matrix: np.ndarray
    translation_vector: np.ndarray

    @property
    def r_vec(self) -> np.ndarray:  # p1 p2
        """Rotation vector (converted by cv2.Rodrigues)"""
        r_vec_out, _jacobian = cv2.Rodrigues(src=self.rotation_matrix)
        return r_vec_out

    @staticmethod
    def load_from_mat_file(path) -> "ExtrinsicsParams":
        mat_file = loadmat(path)
        r = mat_file["r"]
        t = mat_file["t"]
        return ExtrinsicsParams(rotation_matrix=r, translation_vector=t)


def calibrate_extrinsics(
    video_path: str,
    rows: int,
    cols: int,
    object_points: np.ndarray,  # 3d points the calibration object. E.g. shape: (rows x cols, 3)
    intrinsics: IntrinsicsParams,
    image_width: int,
    image_height: int,
    camera_idx: int,
):
    # load distorted image from video frame
    img = get_first_frame_video(video_path=video_path)

    ## undistorting not necessary for solvePnP

    # find corner positions
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    success, corner_coords = cv2.findChessboardCorners(gray, (cols, rows), None)

    if success is False:
        raise Exception("Chessboard corners not found - unable to calibrate extrinsics")

    # solve for camera position using solvePnp instead of camera calibration function
    # ransac version fo solvePNP makes it more stable with possible outlier points
    success, r_vec, t_vec = cv2.solvePnP(
        objectPoints=object_points,
        imagePoints=corner_coords,
        cameraMatrix=intrinsics.camera_matrix,
        distCoeffs=intrinsics.dist,
    )

    rotation_matrix, _jacobian = cv2.Rodrigues(r_vec)

    ret = ExtrinsicsParams(rotation_matrix=rotation_matrix, translation_vector=t_vec)

    # TODO: REMOVE
    # COMPUTE RPE for testing

    ipts = corner_coords.squeeze()
    re_ipts_raw, _jacobian = cv2.projectPoints(
        objectPoints=object_points,
        rvec=r_vec,
        tvec=t_vec,
        cameraMatrix=intrinsics.camera_matrix,
        distCoeffs=intrinsics.dist,
    )

    re_ipts = re_ipts_raw.squeeze()
    cv2.drawChessboardCorners(
        image=gray, corners=re_ipts, patternSize=(cols, rows), patternWasFound=True
    )

    cv2.imwrite(f"./out/ext_reproj_cam{camera_idx+1}.png", gray)

    rpe = calculate_rpe(ipts, re_ipts)
    logging.info(f"Extrinsics RPE: {rpe}")

    # TODO: END REMOVE

    return ret
