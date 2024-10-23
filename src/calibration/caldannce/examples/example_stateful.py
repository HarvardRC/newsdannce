from pprint import pp
from caldannce.calibrate_stateful import Calibrator
from caldannce.logger import init_logger
from caldannce.methods.extrinsics_chessboard import ExtrinsicsChessboard
from caldannce.methods.intrinsics_hires_file import IntrinsicsHiresFile
from caldannce.project_utils import (
    get_extrinsics_media_paths,
    get_hires_files,
    get_intrinsics_image_paths,
)


def EXAMPLE():
    """Example usage of calibrate_stateful flow"""
    init_logger()

    # 1. Get args from somewhere (e.g. GUI or config file or CLI args)

    ROWS = 9
    COLS = 6
    SQUARE_SIZE_MM = 23
    N_CAMERAS = 6
    INTRINSICS_DIR = "/Users/caxon/olveczky/dannce_data/cal_benchmark/intrinsics"
    EXTRINSICS_DIR = "/Users/caxon/olveczky/dannce_data/cal_benchmark/extrinsics"
    OUTPUT_DIR = "/Users/caxon/olveczky/dannce_data/cal_benchmark/out-9-4-24"
    OVERRIDE_INTRINSICS_HIRES_DIR = (
        "/Users/caxon/olveczky/dannce_data/cal_benchmark/out-new"
    )

    # 2. Create a Calibrator object, specifying the types for Intrinsics and Extrinsics methods

    cal = Calibrator[IntrinsicsHiresFile, ExtrinsicsChessboard]()

    # 3. Set the intrinsics and extrinsics methods of the Calibrator object.
    #       make sure you pass along instances of CalibrationMethod instead of the class itself
    #       E.g. pass IntrinsicsHiresFile() instead of IntrinsicsHiresFile

    cal.set_intrinsics_method(IntrinsicsHiresFile())
    cal.set_extrinsics_method(ExtrinsicsChessboard(ROWS, COLS, SQUARE_SIZE_MM))

    # 4. Load any calibration data you will need (e.g. camera names, directories, file paths, etc.)

    hires_files = get_hires_files(OVERRIDE_INTRINSICS_HIRES_DIR, 6)

    pp("HIRES")
    pp(hires_files)

    camera_names = [
        "Camera 1",
        "Camera 2",
        "Camera 3",
        "Camera 4",
        "Camera 5",
        "Camera 6",
    ]

    # intrinsics_paths = get_intrinsics_image_paths(
    #     INTRINSICS_DIR, camera_names, ret_dict=True
    # )

    extrinsics_paths = get_extrinsics_media_paths(
        EXTRINSICS_DIR, camera_names, ret_dict=True
    )

    # 5. Add each camera along with the data it will need for intrinsics and extrinsics calibration

    for idx, cam_name in enumerate(camera_names):
        cal.add_camera(
            camera_name=cam_name,
            intrinsics_camdata=IntrinsicsHiresFile.Camdata(
                hires_file_path=hires_files[idx]
            ),
            extrinsics_camdata=ExtrinsicsChessboard.Camdata(
                extrinsics_path=extrinsics_paths[cam_name]
            ),
        )

    # 6. Run calibration

    cal.calibrate()

    # 7. Export to a file

    cal.export_to_folder(OUTPUT_DIR)


if __name__ == "__main__":
    EXAMPLE()
