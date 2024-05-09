import scipy.io as sio
import numpy as np
import os
import cv2
import glob

# Define the directory where the files are stored
calib_path = 'G:/Videos/6cam/jn187/2024_05_03_mice_test/calib_after/'
base_path = 'G:/Videos/6cam/jn187/2024_05_03_mice_test/240229V1left'
output_file = '240503_calib_after_label3d_dannce.mat'

# Prepare a dictionary to hold all the data
label3d_dannce = {'camnames': [], 'params': [], 'sync': []}

# List all .mat files in the directory
input_files = glob.glob(os.path.join(calib_path, '*.mat')) #, 'out/' 'pyxy3d_noT/'
print(input_files)
print(os.path.join(calib_path, '*.mat'))
print(f"Found {len(input_files)} files.")
if len(input_files) > 6:
    print("Found not only 6 camera parameter files, but more. Go and move the extraneous files elsewhere.")

# video_path = 'G:/Videos/6cam/jn187/2024_04_29_chris_validationfor27_mir/videos/Camera1/0.mp4'
# Prepare the sync dictionary by accessing a video file
video_path = os.path.join(base_path, "videos/",  "Camera1/", "0.mp4") #extrinsic
cap = cv2.VideoCapture(video_path)
if not cap.isOpened():
    print("Error opening video file.")
else:
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    print("Frame count:", frame_count)
    cap.release()

    sync = {
        "data_2d": np.zeros((frame_count, 44)),
        "data_3d": np.zeros((frame_count, 66)),
        "data_frame": np.arange(1, frame_count + 1, dtype=np.float64),
        "data_sampleID": np.arange(1, frame_count + 1, dtype=np.float64)
    }

    # Process each input file
    for file_path in input_files:
        file_name = os.path.basename(file_path)
        data = sio.loadmat(file_path)

        # Prepare the parameters dictionary
        camera_params = {
            'K': data['K'].T,
            'RDistort': data['RDistort'],
            'TDistort': data['TDistort'],
            'r': data['r'].T,
            't': data['t']
        }

        # Extract camera name from file name
        cam_name = f"Camera{file_name.split('_')[1].lstrip('cam')}"

        # Append the camera name and parameters to the lists
        label3d_dannce['camnames'].append(cam_name)
        label3d_dannce['params'].append(camera_params)
        label3d_dannce['sync'].append(sync)
        print(f'generated {file_path}')

    # Ensure the correct format for camnames, params, and sync
    label3d_dannce['camnames'] = np.array([label3d_dannce['camnames']], dtype='O')
    label3d_dannce['params'] = np.array(label3d_dannce['params'], dtype='O').reshape(-1, 1)
    label3d_dannce['sync'] = np.array(label3d_dannce['sync'], dtype='O').reshape(-1, 1)

    # Save the converted data to a new .mat file
    output_full_path = os.path.join(base_path, output_file) #'out/', pyxy3d_noT
    # output_full_path = os.path.join('G:/Videos/6cam/jn187/2024_04_29_chris_validationfor27_mir', output_file)
    sio.savemat(output_full_path, label3d_dannce)
    print(f"Data saved to {output_full_path}")


