### Run calibration using the test file: ./test/data/cal_test_data_jpg.tar.gz
# Persist the temporary file so it still exists after running (unlike test_calibration.py)
# This file will be git-ignored, but you have to delete it manually

import json
from pathlib import Path

from src.calibration.calibrate import do_calibrate
from src.calibration.extrinsics import ExtrinsicsMediaFormat
from tests.calibration.helpers import with_real_calib_data


@with_real_calib_data(
    path_to_tarball="./tests/data/cal_test_data_jpg.tar.gz",
    print_debug=True,
    persist=True,
)
def run_example(root_dir):
    # meta-function to avoid fixture issue
    # file containing calibration metadata. Path relative to root_dir of extracted tarball.
    params_file = Path(root_dir, "meta", "calibration_params.json")
    with open(params_file, "rt") as params_file:
        params_dict = json.load(params_file)

    project_dir = root_dir
    output_dir = Path(project_dir, "out")
    rows = params_dict["rows"]
    cols = params_dict["cols"]
    square_size_mm = params_dict["square_size_mm"]
    extrinsics_format = ExtrinsicsMediaFormat(params_dict["extrinsics_format"])

    do_calibrate(
        project_dir=project_dir,
        output_dir=output_dir,
        rows=rows,
        cols=cols,
        square_size_mm=square_size_mm,
        extrinsics_format=extrinsics_format,
    )


if __name__ == "__main__":
    run_example()
