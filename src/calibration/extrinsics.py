import logging
from dataclasses import dataclass
from enum import Enum
from src.calibration.report_utils import get_calibration_report

import cv2
import numpy as np
from scipy.io import loadmat

from src.calibration.intrinsics import IntrinsicsParams
from src.calibration.video_utils import load_image_or_video, ImageFormat

from .math_utils import calculate_rpe


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
    media_path: str,
    rows: int,
    cols: int,
    object_points: np.ndarray,  # 3d points the calibration object. E.g. shape: (rows x cols, 3)
    intrinsics: IntrinsicsParams,
    image_width: int,
    image_height: int,
    camera_idx: int,
):
    img = load_image_or_video(
        media_path=media_path, output_image_format=ImageFormat.CV2_BGR
    )

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

    # TODO: START REMOVE (Compute RPE for testing)

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
        image=img, corners=re_ipts, patternSize=(cols, rows), patternWasFound=True
    )
    cv2.drawChessboardCorners(
        image=img,
        corners=corner_coords,
        patternSize=(cols, rows),
        patternWasFound=False,
    )

    extrinsics_plot_output = f"./out/ext_reproj_cam{camera_idx+1}.png"
    logging.debug(f"Saving extrinsics RPE image to file: {extrinsics_plot_output}")
    cv2.imwrite(extrinsics_plot_output, img)

    rpe = calculate_rpe(ipts, re_ipts)
    logging.info(f"Extrinsics RPE (single camera): {rpe}")

    # TODO: END REMOVE (Compute RPE for testing)

    report = get_calibration_report()
    report.extrinsics_rpes.append(rpe)

    return ret
