"""Alternative to calibration.py where you build a calibration object and specify the pipeline.

This allows more control of how intrinsics and extrinsics are calculated.

E.g. you can have different chessboard sizes for intrinsics and extrinsics, or you can load intrinsics from hires files instead of raw images"""

from dataclasses import dataclass
import time
from typing import Generic, Optional, TypeVar
from caldannce.calibration_data import CameraParams
from caldannce.methods import ExtrinsicsMethod, IntrinsicsMethod

from caldannce.project_utils import (
    write_calibration_params,
)


class CustomCalibrationReport:
    intrinsics_no_pattern_dict: dict[str, list]
    total_intrinsics_images: int
    successful_intrinsics_images: int
    calibration_time_seconds: int
    extrinsics_rpes: dict = {}
    intrinsics_rpes: dict = {}
    camera_names = list[str]

    def __init__(self, camera_names) -> None:
        self.camera_names = camera_names
        self.total_intrinsics_images = 0
        self.successful_intrinsics_images = 0
        self.calibration_time_seconds = None
        self.intrinsics_no_pattern_dict = {}

        for cam_name in camera_names:
            self.intrinsics_no_pattern_dict[cam_name] = []
            self.intrinsics_rpes[cam_name] = None
            self.extrinsics_rpes[cam_name] = None

    def make_summary(self):
        avg_extrinsics_rpe = sum(self.extrinsics_rpes.values()) / len(
            self.extrinsics_rpes
        )
        # TODO: fix
        if list(self.intrinsics_rpes.values())[0] is not None:
            intrinsics_rpe_string = ", ".join(
                map(lambda x: f"{x:.3f}", self.intrinsics_rpes.values())
            )
        else:
            intrinsics_rpe_string = "N/A"

        summary_string = f"Finished in: {self.calibration_time_seconds:.2f} seconds\n"
        summary_string += f"Intrinsics images detected: {self.successful_intrinsics_images} / {self.total_intrinsics_images}\n"
        summary_string += f"Avg. RPE from extrinsics (px): {avg_extrinsics_rpe:.3f}\n"
        summary_string += (
            f"Avg. intrinsics RPE per camera (px): {intrinsics_rpe_string}\n"
        )

        summary_string += "\n\nYou can safely close this GUI.\n"
        return summary_string


@dataclass
class CustomCalibrationData:
    camera_params: list[CameraParams]
    camera_names: list[str]
    n_cameras: int
    output_dir: Optional[str] = None
    report_summary: Optional[str] = None
    calibrator: "Calibrator" = None


@dataclass
class IntrinsicsExtrinsicsData:
    intrinsics_camdata: any
    extrinsics_camdata: any


T_Int = TypeVar("IntrinsicsMethod", bound=IntrinsicsMethod, covariant=True)
T_Ext = TypeVar("ExtrinsicsMethod", bound=ExtrinsicsMethod, covariant=True)


class Calibrator(Generic[T_Int, T_Ext]):
    output_dir: str

    _intrinsics_method: T_Int
    _extrinsics_method: T_Ext
    _camera_data_dict: dict[str, IntrinsicsExtrinsicsData] = {}
    _calibrate_results: CustomCalibrationData = None
    report = None
    _progress_handler = None

    def __init__(self) -> None:
        pass

    def get_results(self):
        return self._calibrate_results

    def set_intrinsics_method(self, int_method: T_Int):
        self._intrinsics_method = int_method
        self._intrinsics_method.bind_calibrator(self)

    def set_extrinsics_method(self, ext_method: T_Ext):
        self._extrinsics_method = ext_method
        self._extrinsics_method.bind_calibrator(self)

    def get_extrinsics_method(self) -> T_Ext:
        return self._extrinsics_method

    def init_report(self, camera_names: list[str]):
        self.report = CustomCalibrationReport(camera_names)

    def add_camera(
        self,
        camera_name,
        intrinsics_camdata: "T_Int.Camdata",
        extrinsics_camdata: "T_Ext.Camdata",
    ):
        if camera_name in self._camera_data_dict:
            raise Exception(f"Cannot add same camera name twice NAME={camera_name}")

        self._camera_data_dict[camera_name] = IntrinsicsExtrinsicsData(
            intrinsics_camdata=intrinsics_camdata,
            extrinsics_camdata=extrinsics_camdata,
        )

    def set_progress_handler(self, progress_handler):
        self._progress_handler = progress_handler

    def calibrate(self):
        # for each camera:
        # 1. compute intrinsics
        # 2. compute extrinsics (providing intrinsics)
        camera_params = []
        if self._progress_handler:
            self._progress_handler(0)
        n_cameras = len(self._camera_data_dict)

        for idx, camera_name in enumerate(self._camera_data_dict.keys()):
            d = self._camera_data_dict[camera_name]
            intrinsics = self._intrinsics_method.compute_intrinsics(
                camera_name=camera_name,
                camdata=d.intrinsics_camdata,
            )
            extrinsics = self._extrinsics_method.compute_extrinsics(
                camera_name=camera_name,
                intrinsics_params=intrinsics,
                camdata=d.extrinsics_camdata,
            )
            camera_params.append(
                CameraParams.from_intrinsics_extrinsics(intrinsics, extrinsics)
            )

            if self._progress_handler:
                pct = round(100 * (idx + 1) / n_cameras)
                self._progress_handler(pct)

        camera_names = list(self._camera_data_dict.keys())

        self._calibrate_results = CustomCalibrationData(
            camera_params=camera_params,
            camera_names=camera_names,
            n_cameras=len(camera_names),
        )

    def export_to_folder(self, output_dir):
        write_calibration_params(
            calibration_data=self._calibrate_results,
            output_dir=output_dir,
            disable_label3d_format=False,
            include_calibration_json=False,
        )
