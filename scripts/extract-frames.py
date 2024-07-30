import numpy as np
from scipy.io import loadmat, savemat
from functools import reduce
import subprocess
import os
from pathlib import Path
import sys
from pprint import pp
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-c", "--camera_idx", type=int, required=True)
args = parser.parse_args()

sole_camera = args.camera_idx

# COM FILE
dannce_file1 = (
    "/Users/caxon/olveczky/dannce_data/data-m7/OLD/RAT23_Label3D_dannce_old.mat"
)


project_dir = "/Users/caxon/olveczky/dannce_data/data-m7"

os.chdir(project_dir)

videos_dir = Path(project_dir, "videos")

n_cameras = 6

mat1 = loadmat(dannce_file1)

data_frame1 = set(mat1["labelData"][0, 0]["data_frame"][0, 0].squeeze())

data_frame1 = sorted(list(data_frame1))

diff = []
for i in range(1, len(data_frame1)):
    diff.append(data_frame1[i] - data_frame1[i - 1])
diff.append("-")

for i in range(len(data_frame1)):
    print(f"{data_frame1[i]:05d} | {diff[i]}")


data_frame = sorted(list(data_frame1))

# additional frames # INC[ 70000 - (71000 - 57) )EXC
extend_ids = [i for i in range(70_000, 71_000 - len(data_frame))]
data_frame.extend(extend_ids)

data_frame_string = reduce(
    lambda acc, cur: f"{acc}+eq(n\,{cur})", data_frame[1:], f"eq(n\,{data_frame[0]})"
)


for cam_idx in [sole_camera]:  # n_cameras
    cam_name = f"Camera{cam_idx+1}"
    input_path = Path(project_dir, "videos", f"cam{cam_idx+1}.mp4")
    output_path = Path(project_dir, "frames_png", f"cam{cam_idx}_%d.png")
    ffmpeg_string = f"ffmpeg -i {input_path} -vf select='{data_frame_string}' -vsync 0 -frame_pts 1 {output_path}"
    output = subprocess.check_output(ffmpeg_string, shell=True, text=True)
    print("DONE")


# # DANNCE FILE
# # dannce_file = "/Users/caxon/olveczky/dannce_data/unit test alone/export/RAT23_Label3D_dannce.mat"

# mat = loadmat(dannce_file)

# data_frame = mat["labelData"][0, 0]["data_frame"][0, 0]

# data_frame = list(data_frame.squeeze())
