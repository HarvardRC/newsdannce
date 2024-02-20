## intro module for new calibration script
import argparse
from src.calibration.new.project_utils import (
    get_calibration_paths,
    write_calibration_params,
)
from src.calibration.new.intrinsics import calibrate_intrinsics
from src.calibration.new.extrinsics import calibrate_extrinsics
from src.calibration.new.utils import get_video_stats, get_chessboard_coordinates
from src.calibration.new.calibration_data import CalibrationData, CameraParams
from dataclasses import asdict
import time


# reasonable max no. of images for a single camera
MAX_IMAGES_ACCEPTED = 400
MIN_IMAGES_ACCEPTED = 10


def main():
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

    args = parser.parse_args()

    rows = args.rows
    cols = args.cols
    square_size_mm = args.square_size_mm
    project_dir = args.project_dir
    output_dir = args.output_dir

    calibration_paths = get_calibration_paths(project_dir=project_dir)

    # generate chessboard object points
    object_points = get_chessboard_coordinates(
        chessboard_rows=rows,
        chessboard_cols=cols,
        square_size_mm=square_size_mm,
    )

    all_camera_params = []

    sample_video_path = calibration_paths.camera_files[0].extrinsics_video_path
    video_info = get_video_stats(sample_video_path)
    print("Video Info: ", video_info)

    print("Running calibration on all cameras")
    for camera_idx, camera_files_single in enumerate(calibration_paths.camera_files):
        camera_name = f"Camera{camera_idx + 1}"

        ##### INTRINSICS #####
        print(f"{camera_name}: Intrinsics")
        intrinsics = calibrate_intrinsics(
            image_paths=camera_files_single.intrinsics_image_paths,
            rows=rows,
            cols=cols,
            object_points=object_points,
            image_width=video_info.width,
            image_height=video_info.height,
        )

        ##### EXTRINSICS #####
        print(f"{camera_name}: Extrinsics")
        extrinsics = calibrate_extrinsics(
            video_path=camera_files_single.extrinsics_video_path,
            rows=rows,
            cols=cols,
            object_points=object_points,
            image_width=video_info.width,
            image_height=video_info.height,
            intrinsics=intrinsics,
        )

        camera_params = CameraParams(**asdict(intrinsics), **asdict(extrinsics))
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

    ##NOTE: opencv spatial coordinate system upper left pixel center at (0,0)
    # matlab spaital cordinate systemm pixel cener at 1,1.
    # opencv -> matlab add 1 to both x and y vaues of converted principal point

    if output_dir:
        write_calibration_params(
            calibration_data=calibration_data, output_dir=output_dir
        )
    else:
        print(calibration_data)


if __name__ == "__main__":
    main()
