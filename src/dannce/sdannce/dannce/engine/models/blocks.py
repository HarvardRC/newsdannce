import torch.nn as nn
import torch.nn.functional as F
from typing import TypeAlias, Literal

from .normalization import LayerNormalization

NORMALIZATION_MODES = {
    "batch": nn.BatchNorm3d,
    "instance": nn.InstanceNorm3d,
    "layer": LayerNormalization,  # nn.LayerNorm
}

NormMethods: TypeAlias = Literal["batch", "instance", "layer"]


class Basic3DBlock(nn.Module):
    def __init__(
        self,
        in_planes: int,
        out_planes: int,
        norm_method: NormMethods,
        input_shape: tuple[int, int, int, int],
        kernel_size=3,
    ):
        super().__init__()
        self.normalization = NORMALIZATION_MODES[norm_method]

        if norm_method == "layer":
            norm_module1 = self.normalization([out_planes, *input_shape])
            norm_module2 = self.normalization([out_planes, *input_shape])
        else:  # norm_method == "instance" or "batch"
            norm_module1 = self.normalization(out_planes)
            norm_module2 = self.normalization(out_planes)

        self.block = nn.Sequential(
            nn.Conv3d(
                in_planes,
                out_planes,
                kernel_size=kernel_size,
                stride=1,
                padding=((kernel_size - 1) // 2),
            ),
            norm_module1,  # self.normalization(...)
            nn.ReLU(True),
            nn.Conv3d(
                out_planes,
                out_planes,
                kernel_size=kernel_size,
                stride=1,
                padding=((kernel_size - 1) // 2),
            ),
            norm_module2,  # self.normalization(...)
            nn.ReLU(True),
        )

    def forward(self, x):
        return self.block(x)


class Res3DBlock(nn.Module):
    def __init__(
        self,
        in_planes: int,
        out_planes: int,
        norm_method: NormMethods,
        input_shape: tuple[int, int, int, int],
    ):
        super().__init__()
        self.normalization = NORMALIZATION_MODES[norm_method]

        if norm_method == "layer":
            norm_module1 = self.normalization([out_planes, *input_shape])
            norm_module2 = self.normalization([out_planes, *input_shape])
        else:  # norm_method == "instance" or "batch"
            norm_module1 = self.normalization(out_planes)
            norm_module2 = self.normalization(out_planes)

        self.res_branch = nn.Sequential(
            nn.Conv3d(in_planes, out_planes, kernel_size=3, stride=1, padding=1),
            norm_module1,  # self.normalization(...)
            nn.ReLU(True),
            nn.Conv3d(out_planes, out_planes, kernel_size=3, stride=1, padding=1),
            norm_module2,  # self.normalization(...)
        )

        # optionally skip convolution step
        if in_planes == out_planes:
            self.skip_conv = nn.Sequential()
        else:
            self.skip_conv = nn.Sequential(
                nn.Conv3d(in_planes, out_planes, kernel_size=1, stride=1, padding=0),
                self.normalization([out_planes, *input_shape])
                if norm_method == "layer"
                else self.normalization(out_planes),
            )

    def forward(self, x):
        res = self.res_branch(x)
        skip = self.skip_conv(x)
        return F.relu(res + skip, True)


class Pool3DBlock(nn.Module):
    def __init__(self, pool_size: int):
        super().__init__()
        self.pool_size = pool_size

    def forward(self, x):
        return F.max_pool3d(x, kernel_size=self.pool_size, stride=self.pool_size)


class BasicUpSample3DBlock(nn.Module):
    def __init__(
        self,
        in_planes: int,
        out_planes: int,
        kernel_size: int,
        stride: int,
        _norm_method,
        _input_shape,
    ):
        super().__init__()
        self.block = nn.Sequential(
            nn.ConvTranspose3d(
                in_planes,
                out_planes,
                kernel_size=kernel_size,
                stride=stride,
                padding=0,
                output_padding=0,
            )
        )

    def forward(self, x):
        return self.block(x)


class Upsample3DBlock(nn.Module):
    def __init__(
        self,
        in_planes: int,
        out_planes: int,
        kernel_size: int,
        stride: int,
        norm_method: NormMethods,
        input_shape: tuple[int, int, int, int],
    ):
        super().__init__()

        assert kernel_size == 2
        assert stride == 2

        self.normalization = NORMALIZATION_MODES[norm_method]

        if norm_method == "layer":
            norm_module1 = self.normalization([out_planes, *input_shape])
        else:  # norm_method == "instance" or "batch"
            norm_module1 = self.normalization(out_planes)

        self.block = nn.Sequential(
            nn.ConvTranspose3d(
                in_planes,
                out_planes,
                kernel_size=kernel_size,
                stride=stride,
                padding=0,
                output_padding=0,
            ),
            norm_module1,
            nn.ReLU(True),
        )

    def forward(self, x):
        return self.block(x)


class Basic2DBlock(nn.Module):
    def __init__(
        self,
        in_planes: int,
        out_planes: int,
        norm_method: NormMethods,
        input_shape: tuple[int, int, int, int],
        kernel_size: int = 3,
    ):
        super().__init__()

        self.normalization = NORMALIZATION_MODES[norm_method]
        if norm_method == "layer":
            norm_module1 = self.normalization([out_planes, *input_shape])
            norm_module2 = self.normalization([out_planes, *input_shape])
        else:  # norm_method == "instance" or "batch"
            norm_module1 = self.normalization(out_planes)
            norm_module2 = self.normalization(out_planes)

        self.block = nn.Sequential(
            nn.Conv2d(
                in_planes,
                out_planes,
                kernel_size=kernel_size,
                stride=1,
                padding=((kernel_size - 1) // 2),
            ),
            norm_module1,
            nn.ReLU(True),
            nn.Conv2d(
                out_planes,
                out_planes,
                kernel_size=kernel_size,
                stride=1,
                padding=((kernel_size - 1) // 2),
            ),
            norm_module2,
            nn.ReLU(True),
        )

    def forward(self, x):
        return self.block(x)


class Pool2DBlock(nn.Module):
    def __init__(self, pool_size: int):
        super().__init__()
        self.pool_size = pool_size

    def forward(self, x):
        return F.max_pool2d(x, kernel_size=self.pool_size, stride=self.pool_size)


class BasicUpSample2DBlock(nn.Module):
    def __init__(
        self,
        in_planes: int,
        out_planes: int,
        kernel_size: int,
        stride: int,
        _norm_method,
        _input_shape,
    ):
        super().__init__()
        self.block = nn.Sequential(
            nn.ConvTranspose2d(
                in_planes,
                out_planes,
                kernel_size=kernel_size,
                stride=stride,
                padding=0,
                output_padding=0,
            )
        )

    def forward(self, x):
        return self.block(x)
