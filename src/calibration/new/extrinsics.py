from dataclasses import dataclass
import numpy as np
from src.calibration.new.intrinsics import IntrinsicsParams
from src.calibration.new.video_utils import get_first_frame_video
import cv2


@dataclass(frozen=True, slots=True, kw_only=True)
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
    img = get_first_frame_video(video_path=video_path)

    # convert from r,t distort to single dist matrix (k1, k2, p1, p2)
    dist_coeffs = np.hstack((intrinsics.r_distort, intrinsics.t_distort))

    ## undistorting not necessary for solvePnP

    # find corner positions
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    success, corner_coords = cv2.findChessboardCorners(gray, (cols, rows), None)

    if success is False:
        raise Exception("Unable to calibrte extrinsics")

    # solve for camera position using solvePnp instead of camera calibration function
    # ransac version fo solvePNP makes it more stable with possible outlier points
    success, rvec, tvec, inliers = cv2.solvePnPRansac(
        objectPoints=object_points,
        imagePoints=corner_coords,
        cameraMatrix=intrinsics.camera_matrix,
        distCoeffs=dist_coeffs,
    )

    rotation_matrix, jac = cv2.Rodrigues(rvec)

    return ExtrinsicsParams(rotation_matrix=rotation_matrix, translation_vector=tvec)
