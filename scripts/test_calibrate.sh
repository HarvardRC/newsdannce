#!/bin/bash

base_folder='~/olveczky/dannce_data/setupCal11_010324'

~/miniforge3/envs/dannce-dev/bin/python -m src.calibration.new.calibrate -v --matlab-intrinsics -r 6 -c 9 -p "$base_folder" -s 23 -o "$base_folder/out_24_03_19a"
