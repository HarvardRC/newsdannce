import functools
import logging
import os
import re
import tarfile
import tempfile
from pathlib import Path

from src.calibration.calibration_data import CameraParams


def with_fake_calib_dirs(
    intrinsics_extension,  # e.g. "mp4" or "png" or "tiff", etc.
    extrinsics_extension,  # e.g. "png" or "tiff"
    n_intrinsics_per_cam=10,  # n of images per intrinsic camera (usually 10-100)
    print_debug=False,  # optionally print the directory created for debugging
):
    """Decorator which creates a temp fake directory for the duration of the decorated function to
    test calibration file utilities.

    Note: this injects the tmp root direcotry as the first positional argument of the decorated
    function!

    E.g. usage:
    @with_fake_calib_dirs(intrinsics_extension="png", extrinsics_extension="png")
    def f(root_dir):
        ...


    """

    def decorator_with_fake_calib_dirs(func):
        @functools.wraps(func)
        def inner(*args, **kwargs):
            with tempfile.TemporaryDirectory() as root_dir:
                if print_debug:
                    print(f"Created temporary directory at : {root_dir}")

                extrinsics_dir = Path(root_dir, "extrinsics")
                intrinsics_dir = Path(root_dir, "intrinsics")
                extrinsics_dir.mkdir()
                intrinsics_dir.mkdir()
                camera_names = [
                    "Camera 0",
                    "Camera 1",
                    "Camera 2",
                    "Camera 3",
                    "Camera 4",
                    "Camera 5",
                ]
                for camera_name in camera_names:
                    intrinsics_cam_x = Path(intrinsics_dir, camera_name)
                    extrinsics_cam_x = Path(extrinsics_dir, camera_name)
                    intrinsics_cam_x.mkdir()
                    extrinsics_cam_x.mkdir()
                    for i in range(n_intrinsics_per_cam):
                        Path(intrinsics_cam_x, f"{i}.{intrinsics_extension}").touch()
                    Path(extrinsics_cam_x, f"0.{extrinsics_extension}").touch()

                if print_debug:
                    walked_files = []
                    for root, dirs, files in os.walk(root_dir):
                        for name in files:
                            walked_files.append(
                                Path(root.replace(root_dir, "$ROOT", 1), name)
                            )

                    walked_files = sorted(walked_files)
                    for f in walked_files:
                        print(f)

                args = [root_dir, *args]
                return func(*args, **kwargs)

        return inner

    return decorator_with_fake_calib_dirs


def with_real_calib_data(path_to_tarball: str, print_debug=False, persist=False):
    """Decorator which extracts real calibration test data to a temp directory and runs the wrapped
    function in that context.

    The temp directory is deleted once the function ends"""

    def decorator_with_real_calib_data(func):
        @functools.wraps(func)
        def inner(*args, **kwargs):
            assert tarfile.is_tarfile(path_to_tarball)

            if persist:
                root_dir = tempfile.mkdtemp(prefix="tmp-calibrate-", dir=".")
                print(f"Created temporary directory at : {root_dir}")
                with tarfile.open(path_to_tarball) as f:
                    f.extractall(path=root_dir)

                # call the inner function with root_dir as the first positional argument
                args = [root_dir, *args]
                return func(*args, **kwargs)

            with tempfile.TemporaryDirectory() as root_dir:
                if print_debug:
                    print(f"Created temporary directory at : {root_dir}")
                with tarfile.open(path_to_tarball) as f:
                    f.extractall(path=root_dir)

                # call the inner function with root_dir as the first positional argument
                args = [root_dir, *args]
                return func(*args, **kwargs)

        return inner

    return decorator_with_real_calib_data


def compare_calibration_output(folder_a, folder_b):
    """Compare two folders containing calibration outputs
    Folders are expected to contain the following files:
     - hires_cam1_params
     - ...
     - hires_cam6_params
     (for the # of cameras - the # of cameras for the folders should be identical)
    """

    logging.debug(
        "Comparing params in folders:\n\tFOLDER_A={folder_a}\n\tFOLDER_B={folder_b}"
    )
    # Exclude mac OS files (._filename)
    param_file_regex = r"^(?<!\._)hires_cam(\d+)_params.mat$"

    def filter_folder_params_files(folder_path):
        """Extract params and extra files from the folder name"""
        all_files = os.listdir(folder_path)
        extra_files = []
        params_files = []

        for filename in all_files:
            m = re.fullmatch(param_file_regex, filename)
            if m:
                params_files.append(m.group(0))
            else:
                extra_files.append(filename)

        return params_files, extra_files

    folder_a_params_files, folder_a_extra_files = filter_folder_params_files(
        folder_path=folder_a
    )

    folder_b_params_files, folder_b_extra_files = filter_folder_params_files(
        folder_path=folder_b
    )

    if len(folder_a_extra_files) > 0:
        logging.warning(
            f"WARNING: Folder A has the following extra files (not compared): {folder_a_extra_files}"
        )

    if len(folder_b_extra_files) > 0:
        logging.warning(
            f"WARNING: Folder B has the following extra files (not compared): {folder_b_extra_files}"
        )

    # make sure file names are identical
    assert (
        set(folder_a_params_files) == set(folder_b_params_files)
    ), f"Folders contain different file names {folder_a_params_files}, {folder_b_params_files}"

    assert (
        len(folder_a_extra_files) >= 1
    ), "folders must contain at least one camera param file"
    comparison_array = []

    for filename in folder_a_params_files:
        path_a = Path(folder_a, filename)
        path_b = Path(folder_b, filename)
        params_a = CameraParams.load_from_hires_file(path_a)
        params_b = CameraParams.load_from_hires_file(path_b)
        is_equal = CameraParams.compare(params_a, params_b)

        comparison_array.append({"filename": filename, "is_equal": is_equal})

    comparison_array = sorted(comparison_array, key=lambda x: x["filename"])

    if all(map(lambda x: x["is_equal"], comparison_array)):
        logging.debug("Folder A and Folder B contain identical params")
        return True
    else:
        logging.debug(
            "Folder A and Folder B differ on the following filenames" + comparison_array
        )
        return False
