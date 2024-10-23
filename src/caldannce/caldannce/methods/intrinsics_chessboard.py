from dataclasses import dataclass
import logging
import time
import cv2
import numpy as np

from caldannce.methods import IntrinsicsMethod
from caldannce.intrinsics import IntrinsicsParams
from caldannce.math_utils import calculate_rpe, get_chessboard_coordinates
from caldannce.video_utils import load_images


class IntrinsicsChessboard(IntrinsicsMethod):
    @dataclass
    class Camdata:
        intrinsics_paths: list[str]

    rows: int
    cols: int
    square_size_mm: int
    _object_points: np.ndarray

    def __init__(self, rows, cols, square_size_mm) -> None:
        self.rows = rows
        self.cols = cols
        self.square_size_mm = square_size_mm
        self._object_points = get_chessboard_coordinates(rows, cols, square_size_mm)

    def _compute_intrinsics(
        self, camera_name: str, camdata: Camdata
    ) -> IntrinsicsParams:
        # get info from the first image in the list (assume all intrinsincs are same dimensions)
        n_images = len(camdata.intrinsics_paths)
        raw_images = load_images(camdata.intrinsics_paths)
        imgpoints = []
        objpoints = []
        failed_imgs = []

        start = time.perf_counter()

        # collect all object and image points for each intrinsics image
        for img_idx in range(n_images):
            this_img = raw_images[img_idx, :, :, :].copy()
            gray = cv2.cvtColor(this_img, cv2.COLOR_BGR2GRAY)

            # Find the chess board corners
            # 2nd param is Size: (Width, Height)
            success, corner_coords = cv2.findChessboardCorners(
                gray, (self.cols, self.rows), None
            )

            if success is True:
                imgpoints.append(corner_coords)
                objpoints.append(self._object_points)
            else:
                failed_image_path = camdata.intrinsics_paths[img_idx]
                logging.warning(
                    f"No pattern detected: Cam# {camera_name}, path:{failed_image_path }"
                )
                failed_imgs.append(img_idx)

                # record list of failed images
                if self.calibrator.report:
                    self.calibrator.report.intrinsics_no_pattern_dict[
                        camera_name
                    ].append(failed_image_path)

        reproject_err, camera_matrix, raw_dist, r_vecs, t_vecs = cv2.calibrateCamera(
            objpoints,
            imgpoints,
            gray.shape[::-1],
            None,
            None,
            # NOTE: CALIB_USE_LU speeds up calibration significantly on Windows Comptuers
            flags=cv2.CALIB_FIX_K3 | cv2.CALIB_USE_LU,
        )
        dist = raw_dist.squeeze()

        ret_params = IntrinsicsParams(
            camera_matrix=camera_matrix,
            dist=dist,
        )

        end = time.perf_counter()

        logging.info(
            f"Found all corners in {(end-start)*1000:.2f} ms [{n_images - len(failed_imgs)}/{n_images} images]"
        )

        # compute reprojection error
        if self.calibrator.report:
            self.calibrator.report.total_intrinsics_images += n_images
            self.calibrator.report.successful_intrinsics_images += n_images
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

            self.calibrator.report.intrinsics_rpes[camera_name] = mean_rpe

            logging.debug(f"Intrinsics mean RPE: {mean_rpe}")
            logging.debug(f"Intrinsics max  RPE: {np.max(rpes)}")
            logging.debug(f"Intrinsics min  RPE: {np.min(rpes)}")

        return ret_params
