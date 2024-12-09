#!/bin/bash

# run as ./benchmarking/reinstall_caldannce.sh
module load Mambaforge
conda activate dannce-dev
pip uninstall -y caldannce

# run in a subshell
( cd src/calibration && pip install --force-reinstall . )

echo "Creating import.log" 

python -X importtime benchmarking/import_caldannce.py 2> benchmarking/import.log

