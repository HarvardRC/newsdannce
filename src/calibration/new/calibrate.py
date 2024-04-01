## intro module for new calibration script
import argparse
from src.calibration.new.project_utils import (
    get_calibration_paths,
    write_calibration_params,
)
from src.calibration.new.intrinsics import calibrate_intrinsics, IntrinsicsParams
from src.calibration.new.extrinsics import calibrate_extrinsics
from src.calibration.new.video_utils import get_video_stats, get_chessboard_coordinates
from src.calibration.new.calibration_data import CalibrationData, CameraParams
from dataclasses import asdict
import time
import os

# reasonable max no. of images for a single camera
MAX_IMAGES_ACCEPTED = 400
MIN_IMAGES_ACCEPTED = 10


def do_calibrate(
    project_dir: str,
    output_dir: str,
    rows: int,
    cols: int,
    square_size_mm: float,
    intrinsics_dir: str = None,
    on_progress=None,
    save_rpe=False,
    matlab_intrinsics=True,
    verbose=False,
) -> None:
    print(
        "ALL ARGS ARE:",
        project_dir,
        output_dir,
        rows,
        cols,
        square_size_mm,
        intrinsics_dir,
        matlab_intrinsics,
    )

    # TODO: improve this, but an empty string for intrinsics_dir is not None
    if intrinsics_dir == "":
        intrinsics_dir = None

    calibration_paths = get_calibration_paths(
        project_dir=project_dir, skip_intrinsics=bool(intrinsics_dir)
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

    print("Running calibration on all cameras")
    n_cameras = len(calibration_paths.camera_files)

    for camera_idx, camera_files_single in enumerate(calibration_paths.camera_files):
        camera_name = f"Camera{camera_idx + 1}"
        print(camera_name)

        if intrinsics_dir is None:
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
            # load intrinsics from existing hires file
            intrinsics = IntrinsicsParams.load_from_mat_file(
                os.path.join(intrinsics_dir, f"hires_cam{camera_idx+1}_params.mat"),
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


def parse_and_calibrate():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-p",
        "--project-dir",
        required=True,
        help="Project directory for dannce calibration. Expected to contain a calibration directory with /intrinsics and /extrinsics directories",
    )
    parser.add_argument(
        "-r",
        "--rows",
        type=int,
        required=True,
        help="# of internal verticies in a row of the chessboard pattern (note this is 1- #of square per row). E.g. 6",
    )
    parser.add_argument(
        "-c",
        "--cols",
        type=int,
        required=True,
        help="# of internal verticies in a column of the chessboard pattern (note this is 1- #of square per column). E.g. 9",
    )
    parser.add_argument(
        "-s",
        "--square-size-mm",
        type=int,
        required=True,
        help="Length of a single chessboard pattern square in mm (e.g. 23)",
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        required=False,
        default=None,
        help="Output directory to create hires_cam#_params.mat files. If not provided, will print calibration params to the console.",
    )
    parser.add_argument(
        "--intrinsics-dir",
        required=False,
        default=None,
        help="If specified, load intrinsics from hires_camX.mat files instead of computing them directly",
    )
    parser.add_argument(
        "--matlab-intrinsics",
        required=False,
        default=False,
        action="store_true",
        help="If provided, save intrinsics in matlab format (vs opencv). This means adjusting for matlab (1,1) origin from (0,0)",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        required=False,
        default=False,
        action="store_true",
        help="Additional logging output (useful for debugging)",
    )

    args = parser.parse_args()

    rows = args.rows
    cols = args.cols
    square_size_mm = args.square_size_mm
    project_dir = args.project_dir
    output_dir = args.output_dir
    matlab_intrinsics = args.matlab_intrinsics
    intrinsics_dir = args.intrinsics_dir
    verbose = args.verbose

    # print all input args
    if verbose:
        print("VERBOSE PRINTING ENABLED\n----------\nARGUMENTS:")
        print(f"CHESSBOARD (ROWS, COLS): ({rows}, {cols})")
        print(f"SQUARE SIZE (mm): {square_size_mm}")
        print(f"BASE PROJECT DIR: {project_dir}")
        print(f"PARAM OUTPUT DIR: {output_dir}")
        print(f"CONVERT INTRINSICS TO MATLAB?: {matlab_intrinsics}")
        print(f"INTRINSICS DIR?: {intrinsics_dir}")
        print("-----")

    do_calibrate(
        project_dir=project_dir,
        output_dir=output_dir,
        rows=rows,
        cols=cols,
        square_size_mm=square_size_mm,
        matlab_intrinsics=matlab_intrinsics,
        verbose=args.verbose,
        intrinsics_dir=intrinsics_dir,
    )


if __name__ == "__main__":
    parse_and_calibrate()
