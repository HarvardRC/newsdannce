from dataclasses import dataclass
import logging
import cv2
import numpy as np

from src.calibration.methods import ExtrinsicsMethod
from src.calibration.extrinsics import ExtrinsicsParams
from src.calibration.intrinsics import IntrinsicsParams
from src.calibration.math_utils import calculate_rpe, get_chessboard_coordinates
from src.calibration.video_utils import ImageFormat, load_image_or_video


class ExtrinsicsChessboard(ExtrinsicsMethod):
    """Calibrate extrinsincs using a chessboard target"""

    @dataclass
    class Camdata:
        extrinsics_path: str

    rows: int
    cols: int
    square_size_mm: int
    _object_points: np.ndarray

    def __init__(self, rows, cols, square_size_mm) -> None:
        self.rows = rows
        self.cols = cols
        self.square_size_mm = square_size_mm
        self._object_points = get_chessboard_coordinates(rows, cols, square_size_mm)

    def _compute_extrinsics(
        self,
        camera_name: str,
        camdata: Camdata,
        intrinsics_params: IntrinsicsParams,
    ) -> ExtrinsicsParams:
        print("INTRINSICS PARAMS ARE", intrinsics_params)
        img = load_image_or_video(
            media_path=camdata.extrinsics_path, output_image_format=ImageFormat.CV2_BGR
        )
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        success, corner_coords = cv2.findChessboardCorners(
            gray, (self.cols, self.rows), None
        )

        if success is False:
            raise Exception(
                f"Chessboard corners not found - unable to calibrate extrinsics (camera {camera_name})"
            )

        success, r_vec, t_vec = cv2.solvePnP(
            objectPoints=self._object_points,
            imagePoints=corner_coords,
            cameraMatrix=intrinsics_params.camera_matrix,
            distCoeffs=intrinsics_params.dist,
        )
        rotation_matrix, _jacobian = cv2.Rodrigues(r_vec)

        ret_params = ExtrinsicsParams(
            rotation_matrix=rotation_matrix, translation_vector=t_vec
        )

        # Compute extrinsics RPE

        ipts = corner_coords.squeeze()
        re_ipts_raw, _jacobian = cv2.projectPoints(
            objectPoints=self._object_points,
            rvec=r_vec,
            tvec=t_vec,
            cameraMatrix=intrinsics_params.camera_matrix,
            distCoeffs=intrinsics_params.dist,
        )

        re_ipts = re_ipts_raw.squeeze()
        rpe = calculate_rpe(ipts, re_ipts)

        logging.info(f"Extrinsics RPE (single camera): {rpe}")

        if self.calibrator.report:
            self.calibrator.report.extrinsics_rpes[camera_name] = rpe

        return ret_params
