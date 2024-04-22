#!/bin/bash

set -e -x

base_folder='/Users/caxon/olveczky/dannce_data/cal_benchmark'

~/miniforge3/envs/dannce-dev/bin/python -m src.calibration.new.calibrate -v -r 6 -c 9 -p "$base_folder" -s 23 -o "$base_folder/out" 