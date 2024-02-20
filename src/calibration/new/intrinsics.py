from dataclasses import dataclass
import numpy as np
import cv2
import time

show_img = False


@dataclass(frozen=True)
class IntrinsicsParams:
    """Camera intrinsics parameters:
    - camera_matrix: 3x3 intrinsics matrix - np.ndarray, Size=(3,3). AKA "K"
    - r_distort: radial distortion: [k1, k2] - np.ndarray, Size=(2,). AKA "rDistort"
    - t_distort: tangential distortion [p1, p2] - np.ndarray, Size=(2,). AKA "tDistort"
    """

    camera_matrix: np.ndarray
    r_distort: np.ndarray
    t_distort: np.ndarray

    def __repr__(self) -> str:
        return f"camera_matrix={self.camera_matrix}, r_distort={self.r_distort}, t_distort={self.t_distort}"


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
    reproject_err, camera_matrix, dist, r_vecs, t_vecs = cv2.calibrateCamera(
        objpoints, imgpoints, gray.shape[::-1], None, None, flags=cv2.CALIB_FIX_K3
    )

    r_distort = dist[0, 0:2]
    t_distort = dist[0, 2:4]

    return IntrinsicsParams(
        camera_matrix=camera_matrix, r_distort=r_distort, t_distort=t_distort
    )
