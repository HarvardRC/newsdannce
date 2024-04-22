## intro module for new calibration script
import argparse
import logging
import os
import time

from src.calibration.new.calibration_data import CalibrationData, CameraParams
from src.calibration.new.extrinsics import calibrate_extrinsics
from src.calibration.new.intrinsics import IntrinsicsParams, calibrate_intrinsics
from src.calibration.new.logger import init_logger
from src.calibration.new.project_utils import (
    get_calibration_paths,
    write_calibration_params,
)
from src.calibration.new.video_utils import get_chessboard_coordinates, get_video_stats

# reasonable max no. of images for a single camera
MAX_IMAGES_ACCEPTED = 400
MIN_IMAGES_ACCEPTED = 10


def do_calibrate(
    project_dir: str,
    output_dir: str,
    rows: int,
    cols: int,
    square_size_mm: float,
    on_progress=None,
    save_rpe=False,
    existing_intrinsics_dir: str = None,
    matlab_intrinsics=True,
    verbose=False,
) -> None:
    start = time.perf_counter()
    # TODO: improve this, but an empty string for intrinsics_dir is not None

    calibration_paths = get_calibration_paths(
        project_dir=project_dir, skip_intrinsics=bool(existing_intrinsics_dir)
    )

    # generate chessboard object points
    object_points = get_chessboard_coordinates(
        chessboard_rows=rows,
        chessboard_cols=cols,
        square_size_mm=square_size_mm,
    )

    all_camera_params = []

    sample_video_path = calibration_paths.camera_files[0].extrinsics_video_path
    video_info = get_video_stats(sample_video_path)

    logging.info("Running calibration on all cameras")
    n_cameras = len(calibration_paths.camera_files)

    for camera_idx, camera_files_single in enumerate(calibration_paths.camera_files):
        camera_name = f"Camera{camera_idx + 1}"
        logging.info(f"Camera {camera_name}")

        if existing_intrinsics_dir is None:
            ##### INTRINSICS #####
            intrinsics = calibrate_intrinsics(
                image_paths=camera_files_single.intrinsics_image_paths,
                rows=rows,
                cols=cols,
                object_points=object_points,
                image_width=video_info.width,
                image_height=video_info.height,
                camera_idx=camera_idx,
            )
        else:
            params_file = os.path.join(
                existing_intrinsics_dir, f"hires_cam{camera_idx+1}_params.mat"
            )
            # load intrinsics from existing hires file
            logging.info(
                f"Loading intrinsics for camera {camera_name} from file: {params_file}"
            )
            intrinsics = IntrinsicsParams.load_from_mat_file(
                params_file,
                cvt_matlab_to_cv2=matlab_intrinsics,
            )

        ##### EXTRINSICS #####
        extrinsics = calibrate_extrinsics(
            video_path=camera_files_single.extrinsics_video_path,
            rows=rows,
            cols=cols,
            object_points=object_points,
            image_width=video_info.width,
            image_height=video_info.height,
            intrinsics=intrinsics,
            camera_idx=camera_idx,
        )

        if on_progress:
            pct = round(100 * (camera_idx + 1) / n_cameras)
            on_progress(pct)

        camera_params = CameraParams(
            camera_matrix=intrinsics.camera_matrix,
            r_distort=intrinsics.r_distort,
            t_distort=intrinsics.t_distort,
            rotation_matrix=extrinsics.rotation_matrix,
            translation_vector=extrinsics.translation_vector,
        )
        all_camera_params.append(camera_params)

    now = time.time()

    camera_names = list(map(lambda x: x.camera_name, calibration_paths.camera_files))

    calibration_data = CalibrationData(
        camera_params=all_camera_params,
        n_cameras=calibration_paths.n_cameras,
        camera_names=camera_names,
        calibration_generated_time=now,
        project_dir=project_dir,
        chessboard_cols=cols,
        chessboard_rows=rows,
        chessboard_square_size_mm=square_size_mm,
    )

    if output_dir:
        write_calibration_params(
            calibration_data=calibration_data,
            output_dir=output_dir,
            matlab_intrinsics=matlab_intrinsics,
        )
    else:
        return calibration_data

    ellapsed_seconds = time.perf_counter() - start
    sec = int(ellapsed_seconds % 60)
    min = int(ellapsed_seconds // 60)
    logging.info(f"Finished calibration in {min:02d}:{sec:02d} (mm:ss)")


def parse_and_calibrate():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--project-dir",
        "-p",
        required=True,
        help="Project directory for dannce calibration. Expected to contain a calibration directory with /intrinsics and /extrinsics directories",
    )
    parser.add_argument(
        "--rows",
        "-r",
        type=int,
        required=True,
        help="# of internal verticies in a row of the chessboard pattern (note this is 1- #of square per row). E.g. 6",
    )
    parser.add_argument(
        "--cols",
        "-c",
        type=int,
        required=True,
        help="# of internal verticies in a column of the chessboard pattern (note this is 1- #of square per column). E.g. 9",
    )
    parser.add_argument(
        "--square-size-mm",
        "-s",
        type=int,
        required=True,
        help="Length of a single chessboard pattern square in mm (e.g. 23)",
    )
    parser.add_argument(
        "--output-dir",
        "-o",
        required=False,
        default=None,
        help="Output directory to create hires_cam#_params.mat files. If not provided, will print calibration params to the console.",
    )

    parser.add_argument(
        "--existing-intrinsics-dir",
        required=False,
        default=None,
        help="If specified and a non-empty string, the app will use the extrinsics from an existing set of .mat calibration files in this specified directory, instead of recalcuating them.",
    )

    parser.add_argument(
        "--matlab-intrinsics",
        required=False,
        default=False,
        action="store_true",
        help="If provided, save intrinsics in matlab format (vs opencv). This means adjusting for matlab (1,1) origin from (0,0)",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        required=False,
        default=False,
        action="count",
        help="Additional logging output (useful for debugging)",
    )

    args = parser.parse_args()

    rows = args.rows
    cols = args.cols
    square_size_mm = args.square_size_mm
    project_dir = args.project_dir
    output_dir = args.output_dir
    matlab_intrinsics = args.matlab_intrinsics
    existing_intrinsics_dir = args.existing_intrinsics_dir
    verbose = args.verbose

    match verbose:
        case 0:
            log_level = logging.INFO
        case 1:
            log_level = logging.DEBUG
        case _:
            raise ValueError(
                "Verbose level must be between 0 and 1 ( e.g. 0: no -v flag, 1: -v)"
            )

    init_logger(log_level=log_level)

    # print all input args
    logging.info("ARGUMENTS")
    logging.info(f"CHESSBOARD (ROWS, COLS): ({rows}, {cols})")
    logging.info(f"SQUARE SIZE (mm): {square_size_mm}")
    logging.info(f"BASE PROJECT DIR: {project_dir}")
    logging.info(f"PARAM OUTPUT DIR: {output_dir}")
    logging.info(f"CONVERT INTRINSICS TO MATLAB?: {matlab_intrinsics}")
    logging.info(f"INTRINSICS DIR?: {existing_intrinsics_dir}")
    logging.info("-----")

    do_calibrate(
        project_dir=project_dir,
        output_dir=output_dir,
        rows=rows,
        cols=cols,
        square_size_mm=square_size_mm,
        matlab_intrinsics=matlab_intrinsics,
        verbose=args.verbose,
        existing_intrinsics_dir=existing_intrinsics_dir,
    )


if __name__ == "__main__":
    parse_and_calibrate()
