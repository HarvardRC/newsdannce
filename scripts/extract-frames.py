import numpy as np
from scipy.io import loadmat, savemat
from functools import reduce
import shutil
import os
from pathlib import Path
import re

project_dir = "/Users/caxon/olveczky/dannce_data/unit_test_alone"

os.chdir(project_dir)


n_cameras = 6

for cam_idx in range(n_cameras):
    p = Path(project_dir, "frames_png")
    files = list(map(lambda x: str(x), p.glob(f"cam{cam_idx}_*.png")))

    frame_idxs = []
    for fname in files:
        m = re.search(rf".+?/cam{cam_idx}_(\d+).png", fname)
        frame_idxs.append([m.group(0), int(m.group(1))])

    frame_idxs.sort(key=lambda x: x[1])

    for i, frame_idx in enumerate(frame_idxs):
        source = Path(frame_idx[0])
        target = Path(project_dir, "frames_png", f"fixed_cam{cam_idx}_{i:03d}.png")
        shutil.copy(source, target)

print("DONE!")


# mat1 = loadmat(dannce_file1)
# mat2 = loadmat(dannce_file2)

# data_frame1 = set(mat1["labelData"][0, 0]["data_frame"][0, 0].squeeze())
# data_frame2 = set(mat2["labelData"][0, 0]["data_frame"][0, 0].squeeze())

# data_frame1.update(data_frame2)  # add COM's to data frame

# data_frame = sorted(list(data_frame1))
# print("DATA FRAME", data_frame)

# data_frame_string = reduce(
#     lambda acc, cur: f"{acc}+eq(n\,{cur})", data_frame[1:], f"eq(n\,{data_frame[0]})"
# )


# for cam_idx in range(n_cameras):  # n_cameras
#     cam_name = f"Camera{cam_idx+1}"
#     input_path = Path(project_dir, "videos", cam_name, "with-frames.mp4")
#     output_path = Path(project_dir, "frames_png", f"cam{cam_idx}_%d.png")
#     ffmpeg_string = f"ffmpeg -i {input_path} -vf select='{data_frame_string}' -vsync 0 -frame_pts 1 {output_path}"
#     print("FFMPEG STRING: ", ffmpeg_string)
#     output = subprocess.check_output(ffmpeg_string, shell=True, text=True)
#     print("OUTPUT")


# # # DANNCE FILE
# # # dannce_file = "/Users/caxon/olveczky/dannce_data/unit test alone/export/RAT23_Label3D_dannce.mat"

# # mat = loadmat(dannce_file)

# # data_frame = mat["labelData"][0, 0]["data_frame"][0, 0]

# # data_frame = list(data_frame.squeeze())
