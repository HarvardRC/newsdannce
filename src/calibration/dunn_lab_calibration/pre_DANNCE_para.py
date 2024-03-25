import os
import toml
import numpy as np
from scipy.io import savemat
from calibration.dunn_lab_calibration.read_pyxy3d_config import (
    Camera,
    CameraParameters,
)
import cv2

camera_parameters = CameraParameters(pyxy_config_path="./config.toml")
camera_parameters.get_parameters()

# export the camera parameters to a .mat file
# initialize the dictionary
label3d_dannce = {
    "camnames": [],  # 1x6 cell array
    "sync": [list() for i in range(6)],  # 6x1 cell array
    "params": [list() for i in range(6)],
}  # 6x1 cell array with camera parameters

# prepare the data for dannce
for i in range(6):
    key = f"cam_{i}"
    label3d_dannce["camnames"].append(f"Camera{i+1}")  # input the camera names
    params_single_cam = dict()  # input the camera parameters
    params_single_cam["K"] = np.array(camera_parameters.cameras[key].cam_matrix).T
    params_single_cam["RDistort"] = np.array(
        [
            camera_parameters.cameras[key].dist[0],
            camera_parameters.cameras[key].dist[1],
            camera_parameters.cameras[key].dist[4],
        ]
    )
    params_single_cam["TDistort"] = np.array(
        [camera_parameters.cameras[key].dist[2], camera_parameters.cameras[key].dist[3]]
    )
    rmtx = cv2.Rodrigues(np.array(camera_parameters.cameras[key].rvec))
    params_single_cam["r"] = rmtx[0].T
    params_single_cam["t"] = np.array(camera_parameters.cameras[key].tvec)
    label3d_dannce["params"][i].append(params_single_cam)

# save the camera names
label3d_dannce["camnames"] = np.array(label3d_dannce["camnames"], dtype=object)

# prepare the sync array
# find our the number of frames in the video
video_path = os.path.join(os.getcwd(), "videos", "Camera1", "0.mp4")
cap = cv2.VideoCapture(video_path)
frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
cap.release()
# prepare the sync array
sync = dict()
sync["data_2d"] = np.zeros((frame_count, 44))
sync["data_3d"] = np.zeros((frame_count, 66))
sync["data_frame"] = np.arange(1, frame_count + 1)
sync["data_sampleID"] = np.arange(1, frame_count + 1)
for i in range(6):
    label3d_dannce["sync"][i].append(sync)

savemat("label3d_dannce.mat", label3d_dannce)
#
