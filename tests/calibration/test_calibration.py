# FILE PURPOSE:
# Test calibration scripts for DANNCE

import json
import os

# Test calibration.new module
from pathlib import Path
from pprint import pp

from src.calibration.calibrate import do_calibrate
from src.calibration.calibrate_stateful import Calibrator
from src.calibration.methods.extrinsics_chessboard import ExtrinsicsChessboard
from src.calibration.methods.intrinsics_chessboard import IntrinsicsChessboard
from src.calibration.project_utils import (
    get_calibration_paths,
    get_camera_names,
    get_extrinsics_media_paths,
    get_intrinsics_image_paths,
)
from tests.calibration.helpers import (
    compare_calibration_output,
    with_fake_calib_dirs,
    with_real_calib_data,
)


def test_calibration_paths_png():
    nofixture_test_calibration_paths_png()


@with_fake_calib_dirs(
    intrinsics_extension="png",
    extrinsics_extension="png",
    n_intrinsics_per_cam=10,
)
def nofixture_test_calibration_paths_png(root_dir):
    # Avoid avoid fixture issue with decorators by rapping this in another function
    calibration_paths = get_calibration_paths(
        intrinsics_dir=str(Path(root_dir, "intrinsics")),
        extrinsics_dir=str(Path(root_dir, "extrinsics")),
    )

    assert calibration_paths.n_cameras == 6
    # assert calibration_paths.project_dir == root_dir
    for camera_file in calibration_paths.camera_files:
        camera_name = camera_file.camera_name
        assert Path(root_dir, "extrinsics", camera_name, "0.png").samefile(
            camera_file.extrinsics_media_path
        )
        assert camera_file.n_images_intrinsics == 10
    assert calibration_paths.intrinsics_dir == str(Path(root_dir, "intrinsics"))
    assert calibration_paths.extrinsics_dir == str(Path(root_dir, "extrinsics"))


def test_calibration_paths_jpg():
    nofixture_test_calibration_paths_jpg


@with_fake_calib_dirs(
    intrinsics_extension="jpg",
    extrinsics_extension="jpg",
    n_intrinsics_per_cam=10,
)
def nofixture_test_calibration_paths_jpg(root_dir):
    calibration_paths = get_calibration_paths(
        root_dir,
        skip_intrinsics=False,
    )

    assert calibration_paths.n_cameras == 6
    # assert calibration_paths.project_dir == root_dir
    for camera_file in calibration_paths.camera_files:
        camera_name = camera_file.camera_name
        assert Path(root_dir, "extrinsics", camera_name, "0.jpg").samefile(
            camera_file.extrinsics_media_path
        )
        assert camera_file.n_images_intrinsics == 10
    assert calibration_paths.intrinsics_dir == str(Path(root_dir, "intrinsics"))
    assert calibration_paths.extrinsics_dir == str(Path(root_dir, "extrinsics"))

    pp(calibration_paths)


def test_calibration_e2e():
    nofixture_calibration_e2e()


@with_real_calib_data(
    path_to_tarball="./tests/data/cal_test_data_jpg.tar.gz", print_debug=True
)
def nofixture_calibration_e2e(root_dir):
    # meta-function to avoid fixture issue
    # file containing calibration metadata. Path relative to root_dir of extracted tarball.
    params_file = Path(root_dir, "meta", "calibration_params.json")
    with open(params_file, "rt") as params_file:
        params_dict = json.load(params_file)

    project_dir = root_dir
    output_dir = Path(project_dir, "out")
    intrinsics_dir = Path(project_dir, "intrinsics")
    extrinsics_dir = Path(project_dir, "extrinsics")
    output_dir_ground_truth = Path(project_dir, "out_expected")
    rows = params_dict["rows"]
    cols = params_dict["cols"]
    square_size_mm = params_dict["square_size_mm"]

    do_calibrate(
        intrinsics_dir=intrinsics_dir,
        extrinsics_dir=extrinsics_dir,
        output_dir=output_dir,
        rows=rows,
        cols=cols,
        square_size_mm=square_size_mm,
    )

    output_files = os.listdir(output_dir)
    expected_output_files = [
        "hires_cam1_params.mat",
        "hires_cam2_params.mat",
        "hires_cam3_params.mat",
        "hires_cam4_params.mat",
        "hires_cam5_params.mat",
        "hires_cam6_params.mat",
    ]
    assert set(
        expected_output_files
    ).issubset(
        set(output_files)
    ), f"calibration did not generate the expected files.\n\tGenerated output: {output_files}\n\tExpected output: {expected_output_files}."

    is_equal = compare_calibration_output(
        folder_a=output_dir_ground_truth, folder_b=output_dir
    )

    assert (
        is_equal
    ), "Generated calibration params not equal to expected calibration params"


def test_calibration_stateful_e2e():
    nofixture_calibration_e2e()


@with_real_calib_data(
    path_to_tarball="./tests/data/cal_test_data_jpg.tar.gz", print_debug=True
)
def nofixture_calibration_stateful_e2e(root_dir):
    # meta-function to avoid fixture issue
    # file containing calibration metadata. Path relative to root_dir of extracted tarball.
    params_file = Path(root_dir, "meta", "calibration_params.json")
    with open(params_file, "rt") as params_file:
        params_dict = json.load(params_file)

    project_dir = root_dir
    output_dir = Path(project_dir, "out")
    intrinsics_dir = Path(project_dir, "intrinsics")
    extrinsics_dir = Path(project_dir, "extrinsics")
    output_dir_ground_truth = Path(project_dir, "out_expected")
    rows = params_dict["rows"]
    cols = params_dict["cols"]
    square_size_mm = params_dict["square_size_mm"]

    # stateful calibrator test
    cal = Calibrator[IntrinsicsChessboard, ExtrinsicsChessboard]

    cal.set_intrinsics_method(IntrinsicsChessboard(rows, cols, square_size_mm))
    cal.set_extrinsics_method(ExtrinsicsChessboard(rows, cols, square_size_mm))

    camera_names = get_camera_names(extrinsics_dir=extrinsics_dir)

    extrinsics_paths_dict = get_extrinsics_media_paths(
        extrinsics_dir, camera_names, ret_dict=True
    )

    intrinsics_paths_dict = get_intrinsics_image_paths(
        intrinsics_dir, camera_names, ret_dict=True
    )

    for cam_name in enumerate(camera_names):
        cal.add_camera(
            cam_name,
            IntrinsicsChessboard.Camdata(intrinsics_paths_dict[cam_name]),
            ExtrinsicsChessboard.Camdata(extrinsics_paths_dict[cam_name]),
        )
    cal.calibrate()
    cal.export_to_folder(output_dir)

    # COMPARE RESULTS
    output_files = os.listdir(output_dir)
    expected_output_files = [
        "hires_cam1_params.mat",
        "hires_cam2_params.mat",
        "hires_cam3_params.mat",
        "hires_cam4_params.mat",
        "hires_cam5_params.mat",
        "hires_cam6_params.mat",
    ]
    assert set(
        expected_output_files
    ).issubset(
        set(output_files)
    ), f"calibration did not generate the expected files.\n\tGenerated output: {output_files}\n\tExpected output: {expected_output_files}."

    is_equal = compare_calibration_output(
        folder_a=output_dir_ground_truth, folder_b=output_dir
    )

    assert (
        is_equal
    ), "Generated calibration params not equal to expected calibration params"
