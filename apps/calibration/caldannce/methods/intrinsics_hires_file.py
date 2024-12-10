from dataclasses import dataclass
from caldannce.methods import IntrinsicsMethod
from caldannce.intrinsics import IntrinsicsParams


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
            camdata.hires_file_path
        )
        return ret_params
