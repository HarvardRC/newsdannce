from dataclasses import dataclass
import numpy as np
from src.calibration.new.intrinsics import IntrinsicsParams
from src.calibration.new.utils import get_first_frame_video
import cv2


@dataclass(frozen=True)
class ExtrinsicsParams:
    """Camera extrinsics parameters:
    - rotation_matrix: 3x3 rotation transformation matrix - np.ndarray, Size=(3,3). AKA "r"
    - translation_vector: [tx, ty, tz] - np.ndarray, Size=(3,). AKA "t"
    """

    rotation_matrix: np.ndarray
    translation_vector: np.ndarray


def calibrate_extrinsics(
    video_path: str,
    rows: int,
    cols: int,
    object_points: np.ndarray,  # 3d points the calibration object. E.g. shape: (rows x cols, 3)
    intrinsics: IntrinsicsParams,
    image_width: int,
    image_height: int,
):
    # load distorted image from video frame

    distorted_img = get_first_frame_video(video_path=video_path)

    # convert from r,t distort to single dist matrix (k1, k2, p1, p2)
    dist_coeffs = np.hstack((intrinsics.r_distort, intrinsics.t_distort))
    undistorted_img = cv2.undistort(
        src=distorted_img, cameraMatrix=intrinsics.camera_matrix, distCoeffs=dist_coeffs
    )

    # undistort frame using intrinsics

    #

    return ExtrinsicsParams(
        rotation_matrix=np.zeros((3, 3)), translation_vector=np.zeros((3,))
    )
