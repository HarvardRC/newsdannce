import logging
import time


from src.calibration.calibrate_stateful import Calibrator
from src.calibration.methods.extrinsics_chessboard import ExtrinsicsChessboard
from src.calibration.methods.intrinsics_chessboard import IntrinsicsChessboard
from src.calibration.methods.intrinsics_hires_file import IntrinsicsHiresFile
from src.calibration.project_utils import (
    get_camera_names,
    get_extrinsics_media_paths,
    get_hires_files,
    get_intrinsics_image_paths,
)


def do_calibrate_stateful(
    intrinsics_dir: str,
    extrinsics_dir: str,
    output_dir: str,
    rows: int,
    cols: int,
    square_size_mm: float,
    on_progress=None,
    override_intrinsics_dir=None,
) -> None:
    start = time.perf_counter()
    # TODO: improve this, but an empty string for intrinsics_dir is not None

    camera_names = get_camera_names(extrinsics_dir)
    n_cameras = len(camera_names)

    extrinsics_paths = get_extrinsics_media_paths(
        extrinsics_dir, camera_names, ret_dict=True
    )

    if override_intrinsics_dir:
        cal = Calibrator[IntrinsicsHiresFile, ExtrinsicsChessboard]()
        int_method = IntrinsicsHiresFile()
        ext_method = ExtrinsicsChessboard(rows, cols, square_size_mm)

        cal.set_intrinsics_method(int_method)
        cal.set_extrinsics_method(ext_method)

        hires_files = get_hires_files(override_intrinsics_dir, n_cameras)

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

    else:
        cal = Calibrator[IntrinsicsChessboard, ExtrinsicsChessboard]()
        int_method = IntrinsicsChessboard(rows, cols, square_size_mm)
        ext_method = ExtrinsicsChessboard(rows, cols, square_size_mm)
        cal.set_intrinsics_method(int_method=int_method)
        cal.set_extrinsics_method(ext_method=ext_method)

        intrinsics_paths = get_intrinsics_image_paths(
            intrinsics_dir, camera_names, ret_dict=True
        )

        for idx, cam_name in enumerate(camera_names):
            cal.add_camera(
                camera_name=cam_name,
                intrinsics_camdata=IntrinsicsChessboard.Camdata(
                    intrinsics_paths=intrinsics_paths[cam_name]
                ),
                extrinsics_camdata=ExtrinsicsChessboard.Camdata(
                    extrinsics_path=extrinsics_paths[cam_name]
                ),
            )

    if on_progress:
        cal.set_progress_handler(on_progress)

    cal.init_report(camera_names)
    cal.calibrate()
    cal.export_to_folder(output_dir)

    ellapsed_seconds = time.perf_counter() - start
    cal.report.calibration_time_seconds = ellapsed_seconds
    sec = int(ellapsed_seconds % 60)
    min = int(ellapsed_seconds // 60)
    logging.info(f"Finished calibration in {min:02d}:{sec:02d} (mm:ss)")

    results = cal.get_results()
    results.output_dir = output_dir
    results.report_summary = cal.report.make_summary()

    return results
