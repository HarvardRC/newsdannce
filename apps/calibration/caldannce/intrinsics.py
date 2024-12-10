import json
import logging
import time
from dataclasses import dataclass
from pathlib import Path

import cv2

# must import module to disable interactive rendering for logs
import matplotlib
import numpy as np
from matplotlib import pyplot as plt
from scipy.io import loadmat

from caldannce.video_utils import load_images

from .math_utils import calculate_rpe

# debug flag to display each image after the chessboard has been detected
DEBUG_SHOW_DETECTED_CHESSBOARD = False


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
    def load_from_mat_file(path: str) -> "IntrinsicsParams":
        """
        convert from matlab intrinsics matrix to cv2: adjust upper left px from (1,1) to (0,0) and transpose camera_matrix
        """
        mat_file = loadmat(path)
        r_distort = np.array(mat_file["RDistort"]).squeeze()
        t_distort = np.array(mat_file["TDistort"]).squeeze()
        dist = np.array([r_distort[0], r_distort[1], t_distort[0], t_distort[1]])
        k = mat_file["K"]

        # convert from label3d format
        k = k.T
        k[0, 2] -= 1
        k[1, 2] -= 1
        return IntrinsicsParams(camera_matrix=k, dist=dist)

    def __eq__(self, other: "IntrinsicsParams") -> bool:
        return np.array_equal(self.dist, other.dist) and np.array_equal(
            self.camera_matrix, other.camera_matrix
        )

    def __post_init__(self):
        # brief error-checking occurs after initialization
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
        # focal length (x,y)
        f_x = self.camera_matrix[0, 0]
        f_y = self.camera_matrix[1, 1]
        # principal point (x,y)
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


def calibrate_intrinsics(
    image_paths: list[str],
    rows: int,
    cols: int,
    object_points: np.ndarray,  # 3d points the calibration object. E.g. shape: (rows x cols, 3)
    image_width: int,  # image width in px
    image_height: int,  # image height in px
    camera_idx: int = None,  # optionally provide the camera idx (only useful for logging/debugging)
    plot_rpe=False,
) -> IntrinsicsParams:
    """Primary method to calibrate camera intrinsics given a set of images paths and metadata

    Returns an IntrinsicsParams object for a single camera"""
    n_images = len(image_paths)

    raw_images = load_images(
        image_paths=image_paths, image_width=image_width, image_height=image_height
    )

    objpoints = []
    imgpoints = []
    failed_imgs = []

    start = time.perf_counter()

    # calibration report
    from caldannce.report_utils import get_calibration_report

    report = get_calibration_report()

    for img_idx in range(n_images):
        this_img = raw_images[img_idx, :, :, :].copy()
        gray = cv2.cvtColor(this_img, cv2.COLOR_BGR2GRAY)

        # Find the chess board corners
        # 2nd param is Size: (Width, Height)
        success, corner_coords = cv2.findChessboardCorners(gray, (cols, rows), None)

        if success is True:
            imgpoints.append(corner_coords)
            objpoints.append(object_points)

            if DEBUG_SHOW_DETECTED_CHESSBOARD is True:
                cv2.drawChessboardCorners(this_img, (cols, rows), corner_coords, True)
        else:
            report.add_no_pattern_detected(
                camera_idx=camera_idx, image_path=image_paths[img_idx]
            )
            logging.warning(
                f"No pattern detected: Cam# {camera_idx}, path:{image_paths[img_idx]}"
            )
            failed_imgs.append(img_idx)

    end = time.perf_counter()

    report.total_intrinsics_images += n_images
    report.successful_intrinsics_images += n_images - len(failed_imgs)

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
        # NOTE: CALIB_USE_LU speeds up calibration significantly on Windows Comptuers
        flags=cv2.CALIB_FIX_K3 | cv2.CALIB_USE_LU,
    )
    end = time.perf_counter()
    logging.info(f"Intrinsics calculation took in {(end-start)*1000:.2f} ms")

    logging.info(f"Intrinsics RPE from calibrateCamera: {reproject_err}")

    dist = raw_dist.squeeze()

    ret = IntrinsicsParams(
        camera_matrix=camera_matrix,
        dist=dist,
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

    mean_rpe = np.mean(rpes)

    report.intrinsics_rpes.append(mean_rpe)

    logging.debug(f"Intrinsics mean RPE: {mean_rpe}")
    logging.debug(f"Intrinsics max  RPE: {np.max(rpes)}")
    logging.debug(f"Intrinsics min  RPE: {np.min(rpes)}")

    if plot_rpe:
        ### Plot intrinsics error
        # use non-interactive MPL backend
        matplotlib.use("agg")
        plt.figure()
        plt.bar(x=[i for i in range(len(rpes))], height=rpes)
        plt.title(f"Camera {camera_idx+1} Intrinsics RPE")
        Path("./out").mkdir(parents=True, exist_ok=True)
        plot_path = f"./out/rpe_cam{camera_idx+1}.png"
        plt.savefig(plot_path)
        logging.debug(
            f"Saved intrinsics error plot for camera #{camera_idx} to path: {plot_path}"
        )

    # TODO: END REMOVE
    return ret
