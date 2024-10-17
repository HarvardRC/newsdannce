# Abstract class for all intrinsics methods
from abc import ABCMeta, abstractmethod
from typing import TYPE_CHECKING

from attr import dataclass

from caldannce.extrinsics import ExtrinsicsParams
from caldannce.intrinsics import IntrinsicsParams

# import only for the type checker - avoid circular imports
if TYPE_CHECKING:
    from caldannce.calibrate_stateful import Calibrator


# Abstract class for all intrinsics methods
class IntrinsicsMethod(metaclass=ABCMeta):
    calibrator: "Calibrator"

    @dataclass
    class Camdata:
        pass

    @abstractmethod
    def _compute_intrinsics(
        self, camera_name: str, camdata: Camdata
    ) -> IntrinsicsParams:
        pass

    def compute_intrinsics(self, camera_name: str, camdata: Camdata):
        if type(camdata) != self.Camdata:
            raise Exception(
                f"Wrong camdata type passed to compute_intrinsics. You must pass a camdata object of type: {self.Camdata}"
            )
        return self._compute_intrinsics(camera_name, camdata)

    def bind_calibrator(self, calibrator):
        self.calibrator = calibrator


# Abstract class for all extrinsics methods
class ExtrinsicsMethod(metaclass=ABCMeta):
    calibrator: "Calibrator"

    @abstractmethod
    @dataclass
    class Camdata:
        pass

    @abstractmethod
    def _compute_extrinsics(
        self, camera_name: str, camdata: Camdata, intrinsics_params: IntrinsicsParams
    ) -> ExtrinsicsParams:
        pass

    def compute_extrinsics(
        self, camera_name: str, camdata: Camdata, intrinsics_params: IntrinsicsParams
    ) -> ExtrinsicsParams:
        if type(camdata) != self.Camdata:
            raise Exception(
                f"Wrong camdata type passed to compute_extrinsics. You must pass a camdata object of type: {self.Camdata}"
            )
        return self._compute_extrinsics(
            camera_name=camera_name,
            camdata=camdata,
            intrinsics_params=intrinsics_params,
        )

    def bind_calibrator(self, calibrator):
        self.calibrator = calibrator
