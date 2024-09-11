from dataclasses import dataclass
from src.calibration.methods import IntrinsicsMethod
from src.calibration.intrinsics import IntrinsicsParams


class IntrinsicsHiresFile(IntrinsicsMethod):
    """Obtain intrinsics from existing "hires" calibration files."""

    @dataclass
    class Camdata:
        hires_file_path: str

    def __init__(self) -> None:
        pass

    def _compute_intrinsics(
        self, camera_name: str, camdata: Camdata
    ) -> IntrinsicsParams:
        ret_params = IntrinsicsParams.load_from_mat_file(
            camdata.hires_file_path, cvt_matlab_to_cv2=False
        )
        return ret_params
