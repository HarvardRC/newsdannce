import os
import sys
from pathlib import Path
from scipy.io import loadmat, savemat
import cv2
import numpy as np

# import tempfile
import uuid


def get_info_from_df_path(df_path: str):
    p = Path(df_path).glob("*dannce.mat")
    # list files in the data folder (depth=1)
    files = [str(x) for x in p if x.is_file()]

    matfile_data = []
    for matfile in files:
        m = loadmat(matfile)
        n_labeled_frames = m["labelData"][0, 0]["data_3d"][0, 0].shape[0]
        cam_params = []

        for cam_idx in range(6):
            cam_params.append(
                {
                    "K": m["params"][cam_idx, 0][0, 0]["K"].tolist(),
                    "r": m["params"][cam_idx, 0][0, 0]["r"].tolist(),
                    "t": m["params"][cam_idx, 0][0, 0]["t"].tolist(),
                    "RDistort": m["params"][cam_idx, 0][0, 0]["RDistort"].tolist(),
                    "TDistort": m["params"][cam_idx, 0][0, 0]["TDistort"].tolist(),
                }
            )

        matfile_data.append(
            {
                "path": matfile,
                "n_labeled_frames": n_labeled_frames,
                "params": cam_params,
            }
        )

    video_path = Path(df_path, "videos", "Camera1", "0.mp4")
    print("VIDEO PATH IS :", video_path)
    # get first frame of video
    vidcap = cv2.VideoCapture(video_path)
    success, image = vidcap.read()

    filename = f"{uuid.uuid4().hex}.jpg"
    # cv2.imwrite(filename, image)

    cv2.imwrite(f"./static/{filename}", image)

    return {"matfile_data": matfile_data, "image": filename}
