import argparse
import logging
import os
import pickle
import time
from pathlib import Path

import cv2
import numpy as np

from .calibration_data import CalibrationData
from .logger import init_logger
from .math_utils import calculate_rpe
from .video_utils import get_first_frame_video, load_image


def get_validation_filepaths(validate_dir: str, filename: str, n_cameras: int):
    """Given a folder containing multiple parameter files (hires_camX_params.mat), return the paths for each camera"""
    path_list = []
    for i in range(n_cameras):
        camera_foldername = f"Camera{i+1}"
        this_path = Path(validate_dir, camera_foldername, filename)

        if not (this_path.exists() and this_path.is_file()):
            raise Exception(
                f"Trying to load validaton file at path: {this_path} but it does not exist or is a directory"
            )
        path_list.append(str(this_path))
    return path_list


def do_validate(
    validate_dir: str,
    params_dir: str,  # UNUSED
    calibration_data: CalibrationData,
    validate_dir_format="VIDEO",
    visualize=True,
):
    logging.info("Running validation")
    logging.debug(f"Validate dir {validate_dir}")
    logging.debug(f"Calibration data: {calibration_data}")

    start = time.perf_counter()
    # do the thing....

    validation_imgs = []

    # load files from validate_dir
    if validate_dir_format == "TIFF":
        img_filepaths = get_validation_filepaths(
            validate_dir=validate_dir,
            filename="0.tiff",
            n_cameras=calibration_data.n_cameras,
        )
        for filepath in img_filepaths:
            img = load_image(filepath)
            validation_imgs.append(img)

    elif validate_dir_format == "VIDEO":
        video_filepaths = get_validation_filepaths(
            validate_dir=validate_dir,
            filename="0.mp4",
            n_cameras=calibration_data.n_cameras,
        )
        for filepath in video_filepaths:
            validation_imgs.append(get_first_frame_video(filepath))
    else:
        raise Exception(f"Unknwon `validate_dir_format`: ${validate_dir_format}")

    logging.info(
        f"Loaded {len(validation_imgs)} images using method: {validate_dir_format}"
    )

    rows = calibration_data.chessboard_rows
    cols = calibration_data.chessboard_cols

    def find_corners(img):
        """Helper funciton to find chessboard corners in an image"""
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        success, image_points = cv2.findChessboardCorners(gray, (cols, rows), None)
        if success is False:
            raise Exception("Chessboard corners not found!")

        return image_points

    # Triangulate the chessboard corners from two (aribtrary) cameras
    corners_cam0 = find_corners(validation_imgs[0])
    corners_cam1 = find_corners(validation_imgs[1])

    params_cam0 = calibration_data.camera_params[0]
    params_cam1 = calibration_data.camera_params[1]

    undist_corners_cam0 = cv2.undistortImagePoints(
        corners_cam0, params_cam0.camera_matrix, params_cam0.dist
    )

    undist_corners_cam1 = cv2.undistortImagePoints(
        corners_cam1, params_cam1.camera_matrix, params_cam1.dist
    )

    # Compute Rt matrice. I.e. 4x3 matrix like: [ Rotation matrix | translation ]
    Rt_cam0 = np.concatenate(
        [params_cam0.rotation_matrix, params_cam0.translation_vector], axis=-1
    )
    perspective_mtx_cam0 = np.matmul(params_cam0.camera_matrix, Rt_cam0)

    Rt_cam1 = np.concatenate(
        [params_cam1.rotation_matrix, params_cam1.translation_vector], axis=-1
    )
    perspective_mtx_cam1 = np.matmul(params_cam1.camera_matrix, Rt_cam1)

    object_pts_homogeneous = cv2.triangulatePoints(
        perspective_mtx_cam0,
        perspective_mtx_cam1,
        undist_corners_cam0,
        undist_corners_cam1,
    )

    object_pts = cv2.convertPointsFromHomogeneous(object_pts_homogeneous.T)

    ### for each camera, project points using that camera's intrinsics matrices, then compute the RPE

    for camera_idx in range(calibration_data.n_cameras):
        logging.debug(f"CAMERA # {camera_idx}")
        img = validation_imgs[camera_idx]
        params = calibration_data.camera_params[camera_idx]

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        success, image_points = cv2.findChessboardCorners(gray, (cols, rows), None)
        if success is False:
            raise Exception("Chessboard corners not found - camera {camera_idx}")

        img_pts = image_points.squeeze()

        re_img_pts_raw = cv2.projectPoints(
            objectPoints=object_pts,
            rvec=params.rvec,
            tvec=params.translation_vector,
            cameraMatrix=params.camera_matrix,
            distCoeffs=params.dist,
        )

        re_ipts = re_img_pts_raw[0].squeeze()
        rpe = calculate_rpe(img_pts, re_ipts)

        logging.info(f"Camera {camera_idx+1}: RPE is {rpe:.4f}")

        # Optionally, draw the detected and re-projected corners using opencv and save to a file
        if visualize:
            draw_img = img.copy()

            cv2.drawChessboardCorners(
                image=draw_img,
                patternSize=(cols, rows),
                corners=re_ipts,
                patternWasFound=False,
            )

            cv2.drawChessboardCorners(
                image=draw_img,
                patternSize=(cols, rows),
                corners=img_pts,
                patternWasFound=True,
            )
            prefix = "./out/validate"
            cv2.imwrite(img=draw_img, filename=f"{prefix}/cam{camera_idx}.png")
            os.makedirs(prefix, exist_ok=True)
            logging.info(f"Saving to: {prefix}/cam{camera_idx}.png")

    # end of the thing ...
    ellapsed_seconds = time.perf_counter() - start
    sec = int(ellapsed_seconds % 60)
    min = int(ellapsed_seconds // 60)
    logging.info(f"Finished validation in {min:02d}:{sec:02d} (mm:ss)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--validate-dir",
        required=True,
        help="Directory containing the validation files (e.g. in format validation_dir/Camera1/0.tiff)",
    )
    parser.add_argument(
        "--pickle-from",
        required=True,
        help="DEBUG ARGUMENT load calibration data from a pickled file",
    )

    parser.add_argument(
        "--validate-dir-format",
        required=False,
        help='Specifies the validation file data format Either "VIDEO" or "TIFF". If this is "VIDEO" it will load the first frame from the video',
    )  # DEFUALT VALUE is specified in the `do_validate` function

    parser.add_argument(
        "--visualize",
        required=False,
        default=False,
        action="store_true",
        help="If this arg is specified, then draw the projected vs re-projected chessboard corners on a file and save it to e.g. ./out/triang/cam0.png ",
    )  # DEFUALT VALUE is specified in the `do_validate` function

    args = parser.parse_args()
    validate_dir = args.validate_dir
    pickle_from = args.pickle_from
    validate_dir_format = args.validate_dir_format
    visualize = args.visualize

    init_logger(log_level=logging.DEBUG)

    pickle_path = Path(args.pickle_from)
    with open(pickle_path, "rb") as f:
        calibration_data = pickle.load(f)

    do_validate(
        calibration_data=calibration_data,
        params_dir=None,
        validate_dir=validate_dir,
        validate_dir_format=validate_dir_format,
        visualize=visualize,
    )
