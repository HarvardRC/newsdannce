import cv2
import os

import argparse

import pathlib

from ..extrinsics import ExtrinsicsParams
from ..intrinsics import IntrinsicsParams
from ..video_utils import get_first_frame_video, get_chessboard_coordinates, load_image

from ..math_utils import calculate_rpe


def test_matlab(
    hires_file,
    img,
    output_dir,
    rows=6,
    cols=9,
    square_size_mm=23,
):
    intrinsics = IntrinsicsParams.load_from_mat_file(hires_file, cvt_matlab_to_cv2=True)
    extrinsics = ExtrinsicsParams.load_from_mat_file(hires_file)

    object_points = get_chessboard_coordinates(
        chessboard_rows=rows,
        chessboard_cols=cols,
        square_size_mm=square_size_mm,
    )

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    success, image_points = cv2.findChessboardCorners(gray, (cols, rows), None)

    if success is False:
        raise Exception(
            "Chessboard corners not found - unable to test extrisnics params [matlab]"
        )

    ipts = image_points.squeeze()
    re_ipts_raw = cv2.projectPoints(
        objectPoints=object_points,
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
        patternSize=(cols, rows),
        corners=re_ipts,
        patternWasFound=False,
    )

    out_path = os.path.join(output_dir, "matlab-reprojections.png")
    cv2.imwrite(img=draw_img, filename=out_path)

    print("MATLAB RPE is ", rpe)

    return {"rpe": rpe, "re_imgpoints": re_ipts}


def test_cv2(hires_file, img, output_dir, rows=6, cols=9, square_size_mm=23):
    intrinsics = IntrinsicsParams.load_from_mat_file(
        hires_file, cvt_matlab_to_cv2=False
    )
    extrinsics = ExtrinsicsParams.load_from_mat_file(hires_file)

    object_points = get_chessboard_coordinates(
        chessboard_rows=rows,
        chessboard_cols=cols,
        square_size_mm=square_size_mm,
    )

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    success, image_points = cv2.findChessboardCorners(gray, (cols, rows), None)

    if success is False:
        raise Exception(
            "Chessboard corners not found - unable to test extrisnics params [cv2]"
        )

    ipts = image_points.squeeze()
    re_ipts_raw = cv2.projectPoints(
        objectPoints=object_points,
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
        patternSize=(cols, rows),
        corners=re_ipts,
        patternWasFound=False,
    )

    cv2.drawChessboardCorners(
        image=draw_img,
        patternSize=(cols, rows),
        corners=image_points.squeeze(),
        patternWasFound=True,
    )

    out_path = os.path.join(output_dir, "cv2-reprojections.png")
    cv2.imwrite(img=draw_img, filename=out_path)

    print("CV2 RPE is ", rpe)

    return {"rpe": rpe, "re_imgpoints": re_ipts}


def do_compare(matlab_hires_file, cv2_hires_file, img, output_dir="./out"):
    test_matlab(hires_file=matlab_hires_file, img=img, output_dir=output_dir)
    test_cv2(hires_file=cv2_hires_file, img=img, output_dir=output_dir)
    print("DONE!")


def parse_and_compare():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-o",
        "--output-dir",
        required=False,
        default="./out",
        help="Output directory to create hires_cam#_params.mat files. If not provided, will print calibration params to the console.",
    )
    parser.add_argument(
        "-m",
        "--matlab-hires-file",
        required=True,
        help="Path to hires_camX_param.mat file from matlab calibration to compare",
    )
    parser.add_argument(
        "-c",
        "--cv2-hires-file",
        required=True,
        help="Path to hires_camX_param.mat file from cv2 calibration to compare",
    )
    parser.add_argument(
        "-v",
        "--video-input",
        required=False,
        default=None,
        help="Path video file containing a checkerboard to test (EITHER THIS OR --image-input must be specified)",
    )
    parser.add_argument(
        "-i",
        "--image-input",
        required=False,
        default=None,
        help="Path image file containing a checkerboard to test (EITHER THIS OR --video-input must be specified)",
    )

    args = parser.parse_args()
    output_dir = args.output_dir
    matlab_hires_file = args.matlab_hires_file
    cv2_hires_file = args.cv2_hires_file
    video_input = args.video_input
    image_input = args.image_input
    if (video_input is None and image_input is None) or (
        video_input is not None and image_input is not None
    ):
        raise Exception(
            "Must specifiy either --video-input OR --image-input, but NOT BOTH"
        )

    if video_input:
        img = get_first_frame_video(video_path=video_input)
    else:
        img = load_image(image_path=image_input)

    print("Making output directory if does not exist: ", output_dir)
    pathlib.Path(output_dir).mkdir(exist_ok=True, parents=True)

    do_compare(
        matlab_hires_file=matlab_hires_file,
        cv2_hires_file=cv2_hires_file,
        img=img,
        output_dir=output_dir,
    )


if __name__ == "__main__":
    parse_and_compare()
