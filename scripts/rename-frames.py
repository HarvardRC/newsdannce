import numpy as np
from scipy.io import loadmat, savemat
from functools import reduce
import subprocess
import os
from pathlib import Path


# COM FILE
dannce_file1 = (
    "/Users/caxon/olveczky/dannce_data/unit_test_alone/export/COM_Label3D_dannce.mat"
)
dannce_file2 = (
    "/Users/caxon/olveczky/dannce_data/unit_test_alone/export/RAT23_Label3D_dannce.mat"
)


project_dir = "/Users/caxon/olveczky/dannce_data/unit_test_alone"

os.chdir(project_dir)

videos_dir = Path(project_dir, "videos")

n_cameras = 6

mat1 = loadmat(dannce_file1)
mat2 = loadmat(dannce_file2)

data_frame1 = set(mat1["labelData"][0, 0]["data_frame"][0, 0].squeeze())
data_frame2 = set(mat2["labelData"][0, 0]["data_frame"][0, 0].squeeze())

data_frame1.update(data_frame2)  # add COM's to data frame

data_frame = sorted(list(data_frame1))
print("DATA FRAME", data_frame)

data_frame_string = reduce(
    lambda acc, cur: f"{acc}+eq(n\,{cur})", data_frame[1:], f"eq(n\,{data_frame[0]})"
)


for cam_idx in range(n_cameras):  # n_cameras
    cam_name = f"Camera{cam_idx+1}"
    input_path = Path(project_dir, "videos", cam_name, "with-frames.mp4")
    output_path = Path(project_dir, "frames_png", f"cam{cam_idx}_%d.png")
    ffmpeg_string = f"ffmpeg -i {input_path} -vf select='{data_frame_string}' -vsync 0 -frame_pts 1 {output_path}"
    print("FFMPEG STRING: ", ffmpeg_string)
    output = subprocess.check_output(ffmpeg_string, shell=True, text=True)
    print("OUTPUT")


# # DANNCE FILE
# # dannce_file = "/Users/caxon/olveczky/dannce_data/unit test alone/export/RAT23_Label3D_dannce.mat"

# mat = loadmat(dannce_file)

# data_frame = mat["labelData"][0, 0]["data_frame"][0, 0]

# data_frame = list(data_frame.squeeze())
