#!/bin/bash

set -e -x

base_folder='/Users/caxon/olveczky/dannce_data/setupCal11_010324'

~/miniforge3/envs/dannce-dev/bin/python -m src.calibration.new.calibrate -v -r 6 -c 9 -p "$base_folder" -s 23 -o "$base_folder/out_cv2" | tee ./out/test_calibrate-log.out
