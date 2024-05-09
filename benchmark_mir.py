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
    return f"G:/Videos/6cam/jn187/2024_04_29_chris_validationfor27_mir/videos/Camera{cam_no}/0.mp4" #test with new edge but not recognizible
    # return f"G:/Videos/6cam/jn187/2024_04_23_chris_test/extrinsic_test_1/Camera{cam_no}/0.mp4" #test with edge


videos = [make_path(i) for i in ["1", "2", "3", "4", "5", "6"]]


imgs = []
params = []
base_path = 'G:/Videos/6cam/jn187/2024_04_29_chris_validationfor27_mir/out'
# base_path = 'G:/Videos/6cam/jn187/2024_04_26_chris_test_mir_intrinsic/pyxy3d_noT' # current best calibration results with lowest rpe both intrinsci and extrinsics(though camera 2 4 not best)
# extract images from videos
for camera_idx in range(n_cams):
    print(f'camera{camera_idx}')
    imgs.append(get_first_frame_video(videos[camera_idx]))
    params.append(os.path.join(base_path, f"hires_cam{camera_idx+1}_params.mat"))

# params = [
#     "G:/Videos/6cam/jn187/2024_04_23_chris_test/hires_cam{camera_idx+1}_params.mat",
#     "G:/Videos/6cam/jn187/2024_04_23_chris_test/hires_cam2_params.mat",
#     "G:/Videos/6cam/jn187/2024_04_23_chris_test/hires_cam3_params.mat",
#     "G:/Videos/6cam/jn187/2024_04_23_chris_test/hires_cam4_params.mat",
#     "G:/Videos/6cam/jn187/2024_04_23_chris_test/hires_cam5_params.mat",
#     "G:/Videos/6cam/jn187/2024_04_23_chris_test/hires_cam6_params.mat",
# ]
# ROWS = 6#9#6
# COLS = 9#6#9
# SQUARE_SIZE_MM = 23#22#23

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

corners = {i: {} for i in range(6)}
object_pts_all = []
# print(corners)

for i in range(n_cams):
    corners[i] = find_corners(imgs[i])
    print(f'camera{i+1}')
# corners_0 = find_corners(imgs[0])
# corners_1 = find_corners(imgs[1])
count = 0
for i in range(n_cams):
    for j in range(n_cams-1):
        if i+1>6:
            continue
        if j+1<= i:
            continue

        int0 = IntrinsicsParams.load_from_mat_file(params[i])
        int1 = IntrinsicsParams.load_from_mat_file(params[j+1])

        ext0 = ExtrinsicsParams.load_from_mat_file(params[i])
        ext1 = ExtrinsicsParams.load_from_mat_file(params[j+1])

        undist_corners_0 = cv2.undistortImagePoints(corners[i], int0.camera_matrix, int0.dist)
        undist_corners_1 = cv2.undistortImagePoints(corners[j+1], int1.camera_matrix, int1.dist)


        Rt0 = np.concatenate([ext0.rotation_matrix, ext0.translation_vector.T], axis=-1)
        P0 = np.matmul(int0.camera_matrix, Rt0)

        Rt1 = np.concatenate([ext1.rotation_matrix, ext1.translation_vector.T], axis=-1)
        P1 = np.matmul(int1.camera_matrix, Rt1)

        object_pts_homo = cv2.triangulatePoints(P0, P1, undist_corners_0, undist_corners_1)
        
        objp = cv2.convertPointsFromHomogeneous(object_pts_homo.T)
        object_pts_all.append(objp)
        print(f"Triangulated points are computed with Cam #s: {i}, {j+1}")
        # print(objp)
        count +=1

object_pts = np.median(np.array(object_pts_all), axis=0)
print("Triangulated points are averaged")
# print(object_pts_all)



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
    cv2.imwrite(img=draw_img, filename=os.path.join(base_path, f"out/validation_from_videos6923/cam{camera_idx}.png"))
    os.makedirs(os.path.join(base_path, "out/validation_from_videos6923"), exist_ok=True)
    print("Saving to: ", os.path.join(base_path, f"out/validation_from_videos6923/cam{camera_idx}.png"))
    print("RPE is: ", rpe)


print("ALL DONE :)")
