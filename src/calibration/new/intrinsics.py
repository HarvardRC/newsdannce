from dataclasses import dataclass
import numpy as np
import cv2
import time
import json
from typing import Optional

show_img = False


@dataclass(frozen=True, slots=True, kw_only=True)
class IntrinsicsParams:
    """Camera intrinsics parameters:
    - camera_matrix: 3x3 intrinsics matrix - np.ndarray, Size=(3,3). AKA "K"
    - r_distort: radial distortion: [k1, k2] - np.ndarray, Size=(2,). AKA "rDistort"
    - t_distort: tangential distortion [p1, p2] - np.ndarray, Size=(2,). AKA "tDistort"
    """

    camera_matrix: np.ndarray
    dist: np.ndarray

    @property
    def r_distort(self) -> np.ndarray:
        return self.dist[0:2]

    @property
    def t_distort(self) -> np.ndarray:
        return self.dist[2:4]

    # reprojection_error: Optional[np.ndarray] = None

    def __post_init__(self):
        skew = self.camera_matrix[0, 1]
        if skew != 0:
            raise NotImplementedError("IntrinsicsParams does not support nonzero skew")

    def __repr__(self) -> str:
        dist = np.hstack((self.r_distort, self.t_distort))
        return f"camera_matrix={json.dumps(self.camera_matrix.tolist())}\ndist={json.dumps(dist.tolist())}\nr_distort={self.r_distort}, t_distort={self.t_distort}"

    def to_matlab(self, image_size=(1200, 1920)) -> "IntrinsicsParamsMatlab":
        f_x = self.camera_matrix[0, 0]
        f_y = self.camera_matrix[1, 1]
        c_x = self.camera_matrix[0, 2] + 1  # convert to matlab (1,1) origin
        c_y = self.camera_matrix[1, 2] + 1  # convert to matlab (1,1) origin

        ret = IntrinsicsParamsMatlab(
            radial_distortion=tuple(self.t_distort),
            tangential_distortion=tuple(self.r_distort),
            image_size=image_size,
            focal_length=(f_x, f_y),
            principal_point=(c_x, c_y),
        )
        return ret


@dataclass(frozen=True, slots=True, kw_only=True)
class IntrinsicsParamsMatlab:
    """Matlab version of intrinsics params"""

    focal_length: tuple[float, float]  # [fx, fy] in px
    principal_point: tuple[float, float]  # [cx, cy] in px
    image_size: tuple[int, int]  # [mrows, ncols] i.e. [height width]
    radial_distortion: tuple[float, float] = (0.0, 0.0)  # [k1, k1] (fix k3 to 0)
    tangential_distortion: tuple[float, float] = (0.0, 0.0)  # [p1, p2]

    @property
    def k(self):
        """K = camera intrinsics matrix := [ fx s cx ; 0 fy cy ; 0 0 1 ]"""
        f_x = self.focal_length[0]
        f_y = self.focal_length[1]
        _s = 0  # zero skew
        c_x = self.principal_point[0]
        c_y = self.principal_point[1]

        return np.array(
            [[f_x, 0.0, c_x], [0.0, f_y, c_y], [0.0, 0.0, 1]], dtype=np.float32
        )

    def to_cv2(self) -> IntrinsicsParams:
        new_k = self.k.copy()
        new_k[0, 2] -= 1
        new_k[1, 2] -= 1
        r_distort = np.array(self.radial_distortion, dtype=np.float32)
        t_distort = np.array(self.tangential_distortion, dtype=np.float32)

        ret = IntrinsicsParams(
            camera_matrix=new_k,
            r_distort=r_distort,
            t_distort=t_distort,
        )
        return ret


def load_images(image_paths, image_width, image_height) -> np.ndarray:
    n_images = len(image_paths)
    # intitialize np array
    raw_images = np.zeros((n_images, image_height, image_width, 3), dtype=np.uint8)

    print(f"Loading {n_images} into memory. May take a few seconds")
    for idx, img_filepath in enumerate(image_paths):
        this_img = cv2.imread(img_filepath)
        raw_images[idx] = this_img
    return raw_images


def calibrate_intrinsics(
    image_paths: list[str],
    rows: int,
    cols: int,
    object_points: np.ndarray,  # 3d points the calibration object. E.g. shape: (rows x cols, 3)
    image_width: int,  # image width in px
    image_height: int,  # image height in px
) -> IntrinsicsParams:
    n_images = len(image_paths)
    raw_images = load_images(
        image_paths=image_paths, image_width=image_width, image_height=image_height
    )

    objpoints = []
    imgpoints = []

    start = time.perf_counter()

    for img_idx in range(n_images):
        this_img = raw_images[img_idx, :, :, :].copy()
        gray = cv2.cvtColor(this_img, cv2.COLOR_BGR2GRAY)

        # Find the chess board corners
        # 2nd param is Size: (Width, Height)
        success, corner_coords = cv2.findChessboardCorners(gray, (cols, rows), None)

        if success is True:
            imgpoints.append(corner_coords)
            objpoints.append(object_points)

            if show_img is True:
                cv2.drawChessboardCorners(this_img, (cols, rows), corner_coords, True)
        else:
            print("Failure: Image #", img_idx)

    end = time.perf_counter()

    print(f"Found all corners in {(end-start)*1000:.2f} ms [{n_images} images]")

    # note: we ignore r_vecs & t_vecs because we don't care about location of calibration target in each frame
    reproject_err, camera_matrix, raw_dist, _r_vecs, _t_vecs = cv2.calibrateCamera(
        objpoints, imgpoints, gray.shape[::-1], None, None, flags=cv2.CALIB_FIX_K3
    )
    print(reproject_err)

    dist = raw_dist.squeeze()

    return IntrinsicsParams(
        camera_matrix=camera_matrix,
        dist=dist,
        # rpe=reproject_err,
    )
