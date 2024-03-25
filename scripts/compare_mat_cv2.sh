#!/bin/bash

VIDEO_PATH="/Users/caxon/olveczky/dannce_data/2024-03-22_extrinsics_tests/2024-03-22_extrinsics_benchmark_noshield/Camera1/corner1-lowlight.mp4"
MATLAB_HIRES="/Users/caxon/hires_cam1_matlab.mat"
CV2_HIRES="/Users/caxon/olveczky/dannce_data/setupCal11_010324/out_cv2/hires_cam1_params.mat"

python -m src.calibration.new.vs_matlab -o ./out/comp1 -v $VIDEO_PATH -m $MATLAB_HIRES -c $CV2_HIRES
