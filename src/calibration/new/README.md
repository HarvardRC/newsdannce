# New Calibration (WIP)

New calibration for `newsdannce` repo

Idea: single canonical calibration pipeline

Goals:
- remove dependency on Matlab
- robust, accurate calibration
- easy to set up
- well documented 

## Calibration GUI

First make sure the proper conda environemtn is activated

E.g. `conda activate dannce-dev`

Launch with `python -m src.calibration.new.gui`


## SETUP

1. install conda/mamba (I prefer mamba)
2. create conda environment
    `conda env create -f ./src/calibration/new/environment.yml`
3. activate environment
   `conda activate dannce-dev`

   ...



## Calibration CLI

You can run the calibration pipeline directly as a python module (argparse)
```
python -m src.calibration.new.calibrate -p "~/olveczky/dannce_data/setupCal11_010324" -r 6 -c 9 -s 23 -o "~/olveczky/dannce_data/setupCal11_010324/calibration_export"
```

## Pytest (WIP)

`python -m pytest src/calibration/new`
