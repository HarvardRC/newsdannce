from src.calibration import (
    calibration_data,
)  # import this way to use types without circular ref.


class _CalibrationReport:
    intrinsics_no_pattern_list: list[list[str]]
    total_intrinsics_images: int = 0
    successful_intrinsics_images: int = 0
    calibration_time_seconds: int = 0
    extrinsics_rpes: list[float] = []
    intrinsics_rpes: list[float] = []
    calibration_data: "calibration_data.CalibrationData" = None

    """Dict for intrinsics images where chessboard pattern was not found. key is camera index (number); value is list of paths"""

    def __init__(self, n_cameras):
        self.intrinsics_no_pattern_list = [[] for _ in range(n_cameras)]

    def add_no_pattern_detected(self, camera_idx: int, image_path: str):
        """Record that no pattern was detected for a camera index"""
        self.intrinsics_no_pattern_list[camera_idx].append(image_path)

    def make_summary(self):
        avg_extrinsics_rpe = sum(self.extrinsics_rpes) / len(self.extrinsics_rpes)
        intrinsics_rpe_string = ", ".join(
            map(lambda x: f"{x:.3f}", self.intrinsics_rpes)
        )
        summary_string = f"Finished in: {self.calibration_time_seconds:.2f} seconds\n"
        summary_string += f"Extrinsics images detected: {self.successful_intrinsics_images} / {self.total_intrinsics_images}\n"
        summary_string += f"Avg. RPE from extrinsics (px): {avg_extrinsics_rpe:.3f}\n"
        summary_string += (
            f"Avg. intrinsics RPE per camera (px): {intrinsics_rpe_string}\n"
        )

        summary_string += f"\nParameters have been saved to directory: {self.calibration_data.output_dir}"

        summary_string += "\n\nYou can safely close this GUI.\n"
        return summary_string


# calibration report global object
_calibration_report = None


def init_calibration_report(*args, **kwargs):
    global _calibration_report
    _calibration_report = _CalibrationReport(*args, **kwargs)


def get_calibration_report():
    return _calibration_report
