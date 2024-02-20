## intro module for new calibration script
import numpy as np
import argparse
from src.calibration.new.project_utils import get_calibration_paths
from src.calibration.new.intrinsics import calibrate_intrinsics
from src.calibration.new.extrinsics import calibrate_extrinsics
from src.calibration.new.utils import get_video_stats, get_chessboard_coordinates
from dataclasses import dataclass, asdict
import time


# reasonable max no. of images for a single camera
MAX_IMAGES_ACCEPTED = 400
MIN_IMAGES_ACCEPTED = 10


@dataclass(frozen=True)
class CameraParams:
    r_distort: np.ndarray
    t_distort: np.ndarray
    camera_matrix: np.ndarray
    rotation_matrix: np.ndarray
    translation_vector: np.ndarray


@dataclass(frozen=True)
class CalibrationData:
    """
    Complete calibration data container.
    Includes camera params (intrinsic & extrinsics), as well as metadata about the calibration process
    """

    camera_params: list[CameraParams]
    """Raw camera parameters"""

    # --- METADATA ---
    n_cameras: int
    """Number of cameras. E.g. 6"""
    camera_names: list[str]
    """Human-readible camera names e.g. \"Camera1\". The name's index in list corresponds to camera idx"""
    project_dir: str
    """Base directory of the DANNCE proejct"""
    calibration_generated_time: float
    """Timestamp the calibration was generated"""
    chessboard_square_size_mm: float
    """Chessboard square size in mm"""
    chessboard_rows: float
    """Chessboard # of rows of *internal* verticies"""
    chessboard_cols: float
    """Chessboard # of columns of *internal* verticies"""

    def __repr__(self):
        time_fmt = "%Y-%m-%d %H:%M:%S %Z"
        time_str = time.strftime(
            time_fmt, time.localtime(self.calibration_generated_time)
        )
        return f"CalibrationData <\n  n_cameras= {self.n_cameras}\n  camera_names= {self.camera_names}\n  project_dir= {self.project_dir}\n  time= {time_str}\n>"


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

    args = parser.parse_args()

    rows = args.rows
    cols = args.cols
    square_size_mm = args.square_size_mm
    project_dir = args.project_dir

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
        print(f"Intrinsics results: {intrinsics}")

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

    print(calibration_data)
    return


#     parser.add_argument(
#         "-i",
#         "--image-folder",
#         required=True,
#         help=f"Folder containing calibration images. Expects between {MIN_IMAGES_ACCEPTED} and {MAX_IMAGES_ACCEPTED} .tiff files",
#     )

#     parser.add_argument(
#         "-o", "--output", required=True, help="Output file for calibration values"
#     )

#     args = parser.parse_args()

#     print(args)

if __name__ == "__main__":
    main()
