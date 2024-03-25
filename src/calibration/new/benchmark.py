# compare cv2 vs matlab for an aribtrary point
import numpy as np

import cv2
import os

import argparse

import pathlib

from .extrinsics import ExtrinsicsParams
from .intrinsics import IntrinsicsParams
from .video_utils import get_first_frame_video, get_chessboard_coordinates, load_image

from .math_utils import calculate_rpe

n_cams = 6


def make_path(cam_no):
    return f"/Users/caxon/olveczky/dannce_data/2024-03-22_extrinsics_tests/2024-03-22_extrinsics_benchmark_noshield/Camera{cam_no}/corner3-lowlight.mp4"


videos = [make_path(i) for i in ["1", "2", "3", "4", "5", "6"]]


imgs = []

# extract images from videos
for camera_idx in range(n_cams):
    imgs.append(get_first_frame_video(videos[camera_idx]))

params = [
    "/Users/caxon/olveczky/dannce_data/2024-03-22_extrinsics_tests/project_folder/recompute/hires_cam1_params.mat",
    "/Users/caxon/olveczky/dannce_data/2024-03-22_extrinsics_tests/project_folder/recompute/hires_cam2_params.mat",
    "/Users/caxon/olveczky/dannce_data/2024-03-22_extrinsics_tests/project_folder/recompute/hires_cam3_params.mat",
    "/Users/caxon/olveczky/dannce_data/2024-03-22_extrinsics_tests/project_folder/recompute/hires_cam4_params.mat",
    "/Users/caxon/olveczky/dannce_data/2024-03-22_extrinsics_tests/project_folder/recompute/hires_cam5_params.mat",
    "/Users/caxon/olveczky/dannce_data/2024-03-22_extrinsics_tests/project_folder/recompute/hires_cam6_params.mat",
]
ROWS = 6
COLS = 9
SQUARE_SIZE_MM = 23

# object_points = get_chessboard_coordinates(
#     chessboard_rows=ROWS,
#     chessboard_cols=COLS,
#     square_size_mm=SQUARE_SIZE_MM,
# )


def find_corners(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    success, image_points = cv2.findChessboardCorners(gray, (COLS, ROWS), None)
    if success is False:
        raise Exception("Chessboard corners not found!")

    return image_points


corners_0 = find_corners(imgs[0])
corners_1 = find_corners(imgs[1])

int0 = IntrinsicsParams.load_from_mat_file(params[0])
int1 = IntrinsicsParams.load_from_mat_file(params[1])

ext0 = ExtrinsicsParams.load_from_mat_file(params[0])
ext1 = ExtrinsicsParams.load_from_mat_file(params[1])

undist_corners_0 = cv2.undistortImagePoints(corners_0, int0.camera_matrix, int0.dist)
undist_corners_1 = cv2.undistortImagePoints(corners_1, int1.camera_matrix, int1.dist)

Rt0 = np.concatenate([ext0.rotation_matrix, ext0.translation_vector.T], axis=-1)
P0 = np.matmul(int0.camera_matrix, Rt0)

Rt1 = np.concatenate([ext1.rotation_matrix, ext1.translation_vector.T], axis=-1)
P1 = np.matmul(int1.camera_matrix, Rt1)

object_pts_homo = cv2.triangulatePoints(P0, P1, undist_corners_0, undist_corners_1)

object_pts = cv2.convertPointsFromHomogeneous(object_pts_homo.T)

print("Triangulated points are computed with Cam #s: 0, 1")

for camera_idx in range(n_cams):
    print("CAMERA #", camera_idx)
    img = imgs[camera_idx]
    param_path = params[camera_idx]

    intrinsics = IntrinsicsParams.load_from_mat_file(param_path)
    extrinsics = ExtrinsicsParams.load_from_mat_file(param_path)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    success, image_points = cv2.findChessboardCorners(gray, (COLS, ROWS), None)
    if success is False:
        raise Exception("Chessboard corners not found - camera {camera_idx}")

    ipts = image_points.squeeze()

    re_ipts_raw = cv2.projectPoints(
        objectPoints=object_pts,
        rvec=extrinsics.r_vec,
        tvec=extrinsics.translation_vector,
        cameraMatrix=intrinsics.camera_matrix,
        distCoeffs=intrinsics.dist,
    )

    re_ipts = re_ipts_raw[0].squeeze()
    rpe = calculate_rpe(ipts, re_ipts)

    draw_img = img.copy()

    cv2.drawChessboardCorners(
        image=draw_img,
        patternSize=(COLS, ROWS),
        corners=re_ipts,
        patternWasFound=False,
    )

    cv2.drawChessboardCorners(
        image=draw_img,
        patternSize=(COLS, ROWS),
        corners=ipts,
        patternWasFound=True,
    )
    cv2.imwrite(img=draw_img, filename=f"./out/triang/cam{camera_idx}.png")
    print("Saving to: ", f"./out/triang/cam{camera_idx}.png")
    print("RPE is: ", rpe)


print("ALL DONE :)")
