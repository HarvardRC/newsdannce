import logging
from typing import TYPE_CHECKING

import cv2
import numpy as np

from caldannce.calibrate_stateful import CustomCalibrationData
from caldannce.math_utils import calculate_rpe, triangulate_all
from caldannce.methods.extrinsics_chessboard import ExtrinsicsChessboard
from caldannce.project_utils import get_verification_files
from caldannce.video_utils import load_image_or_video

if TYPE_CHECKING:
    from caldannce.gui import CalibrationWindow
import PySide6.QtWidgets as QtWidgets

# matplotlib tools
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar

from caldannce.calibration_data import CalibrationData


class CustomNavToolbar(NavigationToolbar):
    toolitems = [
        t for t in NavigationToolbar.toolitems if t[0] in ("Home", "Pan", "Zoom")
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class ValidationManager:
    #     """Provides context data and functions for running camera validation"""

    #     validation_image_paths: list[str]
    #     """list of len [n_cameras] where each entry is a path to the camera of that index used for calibration"""
    #     keypoints_2d: list[tuple[float, float]]
    #     """2D keypoints for each camera image, picked by the GUI"""
    #     scatter_paths: list
    #     """List of matplotlib paths used to redraw user-selected keypoints in gui"""
    #     static_axes: list
    #     """List of matplotlib axes for each of the n cameras"""
    calibration_data: CustomCalibrationData

    def __init__(self, calibration_data: CalibrationData):
        self.calibration_data = calibration_data
        self.avg_rpe = None


def setup_chessboard_validation_window(
    calibration_window: "CalibrationWindow",
    root_frame: QtWidgets.QFrame,
    calibration_data: CalibrationData,
):
    window = calibration_window

    validation_manager = ValidationManager(calibration_data=calibration_data)

    browse_button: QtWidgets.QPushButton = window.findChild(
        QtWidgets.QPushButton, "chessboardVerifyBrowse"
    )
    validation_button: QtWidgets.QPushButton = window.findChild(
        QtWidgets.QPushButton, "chessboardRunValidateButton"
    )
    validation_folder_edit: QtWidgets.QLineEdit = window.findChild(
        QtWidgets.QLineEdit, "chessboardVerifyEdit"
    )
    validation_results: QtWidgets.QLabel = window.findChild(
        QtWidgets.QLabel, "chessboardValidationResults"
    )

    browse_button.clicked.connect(
        calibration_window.handleBrowseDirPartial(
            name="Validation Folder", target_edit=validation_folder_edit
        )
    )

    validation_button.clicked.connect(
        lambda: do_validation_samethread(
            validation_manager,
            results_label=validation_results,
            validation_folder_edit=validation_folder_edit,
        )
    )


def do_validation_samethread(
    validation_manager: ValidationManager,
    results_label: QtWidgets.QLabel,
    validation_folder_edit: QtWidgets.QLineEdit,
):
    validate_dir = validation_folder_edit.text().strip()

    if len(validate_dir) < 1:
        logging.warning("Chessboard folder field is empty")
        return

    calibration_data = validation_manager.calibration_data

    logging.info("Running validation")
    logging.debug(f"Validate dir {validate_dir}")
    logging.debug(f"Calibration data: {calibration_data}")

    camera_names = calibration_data.camera_names
    camera_params = calibration_data.camera_params
    n_cameras = len(camera_names)

    media_paths = get_verification_files(validate_dir, camera_names, ret_dict=True)
    validation_imgs = {n: load_image_or_video(media_paths[n]) for n in camera_names}

    logging.info(f"Loaded {len(validation_imgs)} images")

    calibrator = calibration_data.calibrator
    if type(calibrator.get_extrinsics_method()) != ExtrinsicsChessboard:
        raise Exception(
            "Can only run chessboard validation if extrinsics method was ExtrinsicsChessboard"
        )

    rows = calibrator._extrinsics_method.rows
    cols = calibrator._extrinsics_method.cols
    logging.info("Using (rows, cols) for validaiton: ({},{})".format(rows, cols))

    n_points = rows * cols
    all_ipts = np.zeros([n_cameras, n_points, 2])
    all_view_mtx = np.zeros([n_cameras, 3, 4])

    # detect all image points

    for idx in range(n_cameras):
        n = camera_names[idx]
        img = validation_imgs[n]
        pth = media_paths[n]

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        success, imgs_pts = cv2.findChessboardCorners(gray, (cols, rows), None)
        if success is False:
            raise Exception(f"Chessboard corners not found in validation img: {pth}")

        all_ipts[idx, :, :] = imgs_pts.squeeze()[:, :]
        view_mtx = camera_params[idx].make_projection_matrix()
        all_view_mtx[idx, :, :] = view_mtx

    cam_rpes = np.zeros([n_cameras])
    # triangulate using all points for each camera
    for idx in range(n_cameras):
        n = camera_names[idx]
        img = validation_imgs[n].copy()

        cam_wps = triangulate_all(all_ipts, all_view_mtx)

        cam_ipts = all_ipts[idx, :, :]
        cam_reproj_ipts = camera_params[idx].project_multiple_world_points(cam_wps)

        cam_rpes[idx] = calculate_rpe(cam_ipts, cam_reproj_ipts)

    rpe_string = (
        f"RPE per camera (px): {', '.join(map(lambda x: f'{x:.3f}', cam_rpes))}"
    )
    results_label.setText(rpe_string)
