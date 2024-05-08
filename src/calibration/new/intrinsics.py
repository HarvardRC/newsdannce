from dataclasses import dataclass
import numpy as np
import cv2
import time
import json
from typing import Optional
from scipy.io import loadmat, savemat
import pickle
from .math_utils import calculate_rpe
from pathlib import Path
import logging

import matplotlib
from matplotlib import pyplot as plt


show_img = False
write_one = True


@dataclass(frozen=True, slots=True, kw_only=True, eq=False)
class IntrinsicsParams:
    """Camera intrinsics parameters:
    - camera_matrix: 3x3 intrinsics matrix - np.ndarray, Size=(3,3). AKA "K"
    - r_distort: radial distortion: [k1, k2] - np.ndarray, Size=(2,). AKA "rDistort"
    - t_distort: tangential distortion [p1, p2] - np.ndarray, Size=(2,). AKA "tDistort"
    """

    camera_matrix: np.ndarray
    dist: (
        np.ndarray
    )  # format: [k1 k2 (radial) p1 p2 (tangential) [k3 (radial)] ]. k3 ignored.

    @property
    def r_distort(self) -> np.ndarray:  # k1 k2 [k3]
        return self.dist[0:2]

    @property
    def t_distort(self) -> np.ndarray:  # p1 p2
        return self.dist[2:4]

    @staticmethod
    def load_from_mat_file(
        path: str, cvt_matlab_to_cv2: bool = False
    ) -> "IntrinsicsParams":
        """
        cvt_matlab_to_cv2: if this is true, convert from matlab intrinsics matrix to cv2 intrinsics matrix (add 1)
        """
        mat_file = loadmat(path)
        r_distort = np.array(mat_file["RDistort"]).squeeze()
        t_distort = np.array(mat_file["TDistort"]).squeeze()
        dist = np.array([r_distort[0], r_distort[1], t_distort[0], t_distort[1]])
        k = mat_file["K"]

        if cvt_matlab_to_cv2:
            k[0, 2] -= 1
            k[1, 2] -= 1

        return IntrinsicsParams(camera_matrix=k, dist=dist)

    # reprojection_error: Optional[np.ndarray] = None

    def __eq__(self, other: "IntrinsicsParams") -> bool:
        return np.array_equal(self.dist, other.dist) and np.array_equal(
            self.camera_matrix, other.camera_matrix
        )

    def __post_init__(self):
        skew = self.camera_matrix[0, 1]
        if skew != 0:
            raise NotImplementedError("IntrinsicsParams does not support nonzero skew")
        if len(self.dist) >= 5 and self.dist[4] != 0:
            raise NotImplementedError(
                "IntrinsicsParams does not support nonzero k3 in dist: [k1 k2 p1 p2 k3]"
            )

    def __repr__(self) -> str:
        return f"camera_matrix={json.dumps(self.camera_matrix.tolist())}\ndist={json.dumps(self.dist.tolist())}\nr_distort={self.r_distort}, t_distort={self.t_distort}"

    def to_matlab(self) -> "IntrinsicsParamsMatlab":
        f_x = self.camera_matrix[0, 0]
        f_y = self.camera_matrix[1, 1]
        c_x = self.camera_matrix[0, 2] + 1  # convert to matlab (1,1) origin
        c_y = self.camera_matrix[1, 2] + 1  # convert to matlab (1,1) origin

        ret = IntrinsicsParamsMatlab(
            radial_distortion=tuple(self.t_distort),
            tangential_distortion=tuple(self.r_distort),
            # image_size=image_size,
            focal_length=(f_x, f_y),
            principal_point=(c_x, c_y),
        )
        return ret


@dataclass(frozen=True, slots=True, kw_only=True)
class IntrinsicsParamsMatlab:
    """Matlab version of intrinsics params"""

    focal_length: tuple[float, float]  # [fx, fy] in px
    principal_point: tuple[float, float]  # [cx, cy] in px
    # image_size: tuple[int, int]  # [mrows, ncols] i.e. [height width]
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

    # @staticmethod
    # def load_from_mat(path: str):
    #     mat_file = loadmat(path)
    #     r_distort = np.array(mat_file["RDistort"]).squeeze()
    #     t_distort = np.array(mat_file["TDistort"]).squeeze()
    #     k = mat_file["K"]
    #     # check if camera matrix is upper-triangular -- it should be lower-triangular
    #     if np.any(np.triu(v=k, k=-1) > 0):
    #         raise Exception(
    #             f"Camera matrix is upper triangular, should be lower triangular.\nK={k}"
    #         )
    #     f_x = k[0, 0]
    #     f_y = k[1, 1]
    #     c_x = k[0, 2]
    #     c_y = k[1, 2]
    #     skew = k[0, 1]
    #     if skew >= 0:
    #         raise Exception(f"Does not support non-zero skew.\nskew={skew}")

    #     ret = IntrinsicsParamsMatlab(
    #         focal_length={f_x, f_y},
    #         principal_point={c_x, c_y},
    #     )
    #     return ret


def load_images(image_paths, image_width, image_height) -> np.ndarray:
    n_images = len(image_paths)
    # intitialize np array
    raw_images = np.zeros((n_images, image_height, image_width, 3), dtype=np.uint8)

    logging.info(f"Loading {n_images} images into memory. May take a few seconds")
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
    camera_idx: int = None,  # optionally provide the camera idx (only useful for logging/debugging)
) -> IntrinsicsParams:
    n_images = len(image_paths)
    raw_images = load_images(
        image_paths=image_paths, image_width=image_width, image_height=image_height
    )

    objpoints = []
    imgpoints = []
    failed_imgs = []

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
            logging.warning(f"No pattern detected: Cam# {camera_idx}, Image# {img_idx}")
            logging.debug(f"Image #{img_idx} path: {image_paths[img_idx]}")
            failed_imgs.append(img_idx)

    end = time.perf_counter()

    logging.info(
        f"Found all corners in {(end-start)*1000:.2f} ms [{n_images - len(failed_imgs)}/{n_images} images]"
    )

    start = time.perf_counter()

    # note: we ignore r_vecs & t_vecs because we don't care about location of calibration target in each frame
    reproject_err, camera_matrix, raw_dist, r_vecs, t_vecs = cv2.calibrateCamera(
        objpoints,
        imgpoints,
        gray.shape[::-1],
        None,
        None,
        flags=cv2.CALIB_FIX_K3 | cv2.CALIB_USE_LU,
    )
    end = time.perf_counter()
    logging.info(f"Intrinsics calculation took in {(end-start)*1000:.2f} ms")

    logging.info(f"Intrinsics RPE from calibrateCamera: {reproject_err}")

    dist = raw_dist.squeeze()

    ret = IntrinsicsParams(
        camera_matrix=camera_matrix,
        dist=dist,
        # rpe=reproject_err,
    )

    # TODO: REMOVE
    # plot RPE for testing

    rpes = []
    n_images_success = len(imgpoints)
    for i in range(n_images_success):
        ipts = imgpoints[i].squeeze()
        re_ipts = cv2.projectPoints(
            objpoints[i],
            r_vecs[i],
            t_vecs[i],
            camera_matrix,
            dist,
        )
        re_ipts = re_ipts[0].squeeze()
        rpe = calculate_rpe(ipts, re_ipts)
        rpes.append(rpe)

    logging.debug(f"Intrinsics mean RPE: {np.mean(rpes)}")
    logging.debug(f"Intrinsics max  RPE: {np.max(rpes)}")
    logging.debug(f"Intrinsics min  RPE: {np.min(rpes)}")

    ### Plot intrinsics error
    # use non-interactive MPL backend
    matplotlib.use("agg")
    plt.figure()
    plt.bar(x=[i for i in range(len(rpes))], height=rpes)
    plt.title(f"Camera {camera_idx+1} Intrinsics RPE")
    Path("./out").mkdir(parents=True, exist_ok=True)
    plot_path = f"./out/rpe-cam{camera_idx+1}.png"
    plt.savefig(plot_path)
    logging.debug(
        f"Saved intrinsics error plot for camera #{camera_idx} to path: {plot_path}"
    )

    # TODO: END REMOVE
    return ret
