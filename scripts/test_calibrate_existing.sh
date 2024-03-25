#!/bin/bash

set -e -x

base_folder='/Users/caxon/olveczky/dannce_data/2024-03-22_extrinsics_tests/project_folder'

intrinsics_dir='/Users/caxon/olveczky/dannce_data/setupCal11_010324/out_cv2'

~/miniforge3/envs/dannce-dev/bin/python -m src.calibration.new.calibrate -v -r 6 -c 9 -p "$base_folder" -s 23 --intrinsics-dir $intrinsics_dir -o "$base_folder/recompute" | tee ./out/test_calibrate_existing-log.out
