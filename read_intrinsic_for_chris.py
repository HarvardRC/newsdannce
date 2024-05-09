import os
import sys
import toml
import numpy as np
from scipy.io import savemat
from read_pyxy3d_condfig import Camera, CameraParameters
import cv2

global SCALE_FACTOR
SCALE_FACTOR = 1000

camera_parameters = CameraParameters(path="G:\\Videos\\6cam\\jn187\\2024_04_26_chris_test_mir_intrinsic\\pyxy3d\\best_intrinsics_uselessextrinsics.toml")
camera_parameters.get_parameters()
# toml_path = 'G:\\Videos\\6cam\\jn187\\2024_04_26_chris_test_mir_intrinsic\\pyxy3d\\best_intrinsics.toml'

# def get_parameters(toml_path):
#         with open(toml_path, 'r') as f:
#             config = toml.load(f)

#         n_cams = 0
#         for i in config.keys():
#             if i.startswith('cam'):
#                 n_cams += 1
#                 cam = dict()
#                 cam.cam_matrix = config[i]['matrix']
#                 cam.dist = config[i]['distortions']
#                 # cam.rvec = config[i]['rotation']
#                 # cam.tvec = config[i]['translation']
#                 # cam.exposure = config[i]['exposure']
#                 # cam.resolution = config[i]['verified_resolutions'][0]
#                 # self.cameras[i] = cam

#         print(f"Found {n_cams} cameras")
#         print("Camera amount is ", Camera.amount)
#         return 


# export the camera parameters to a .mat file
# initialize the dictionary
# label3d_dannce = {"camnames": np.zeros(6, dtype=object), # 1x6 cell array
#                 #   "sync": [list() for i in range(6)],    # 6x1 cell array
#                   "params": [list() for i in range(6)]} # 6x1 cell array with camera parameters

# prepare the data for dannce
for i in range(6):
    key = f"cam_{i}"
    
    # label3d_dannce["camnames"][i] = f"Camera{i+1}" # input the camera names
    params_single_cam = dict() # input the camera parameters
    params_single_cam["K"] = np.array(camera_parameters.cameras[key].cam_matrix)# .T 
    params_single_cam["RDistort"] = np.array([camera_parameters.cameras[key].dist[0],
                                     camera_parameters.cameras[key].dist[1],
                                     camera_parameters.cameras[key].dist[4]])
    params_single_cam["TDistort"] = np.array([camera_parameters.cameras[key].dist[2],
                                     camera_parameters.cameras[key].dist[3]])
    # rmtx = cv2.Rodrigues(np.array(camera_parameters.cameras[key].rvec))
    # params_single_cam["r"] = rmtx[0].T
    # params_single_cam["t"] = SCALE_FACTOR*np.array(camera_parameters.cameras[key].tvec)
    # label3d_dannce["params"][i].append(params_single_cam)
    savemat(f"G:/Videos/6cam/jn187/2024_04_26_chris_test_mir_intrinsic/pyxy3d/hires_cam{i+1}_params.mat", params_single_cam)

# prepare the sync array
# find our the number of frames in the video
# video_path = os.path.join(os.getcwd(), "videos", "Camera1", "0.mp4")
# cap = cv2.VideoCapture(video_path)
# frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
# print("frame_count",frame_count)
# cap.release()
# # prepare the sync array
# sync = dict()
# sync["data_2d"] = np.zeros((frame_count, 44))
# # print('data_2d',sync["data_2d"] )
# sync["data_3d"] = np.zeros((frame_count, 66))
# sync["data_frame"] = np.arange(1, frame_count+1, dtype=np.float64) #the two variables need doubles
# sync["data_sampleID"] = np.arange(1, frame_count+1, dtype=np.float64)
# # print('sampleID',sync["data_sampleID"] )
# for i in range(6):
#     label3d_dannce["sync"][i].append(sync)

# savemat("/hpc/group/tdunn/lq53/dannce_model_test_240118/new_cal/t_py_mm_label3d_dannce.mat", label3d_dannce)