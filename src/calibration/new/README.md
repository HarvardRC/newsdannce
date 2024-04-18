# New Calibration (WIP)

New calibration for `newsdannce` repo

Idea: single canonical calibration pipeline

Goals:
- remove dependency on Matlab
- robust, accurate calibration
- easy to set up
- well documented 

## SETUP

1. install conda/mamba (I prefer mamba)
2. create environment
    `mamba env create -f ./src/calibration/new/environment.yml`


## LAUNCH CALIBRATION GUI

1. activate environment
    `mamba activate dannce-dev`
2. start gui with the command
    `python -m src.calibration.new.gui`


## GUI Documentation

GUI Options:
1. Project Directory: base folder for this experiment. Should contain two sub-folders at minimum: extrinsics and intrinsics
2. Output Directory: Folder to save output calibration files to. Typically located within the project directory. NOTE: this folder needs to exist. If it does not yet exist, you must create it before running calibration.
3. Use Existing Intrinsics: If this checkbox is enabled, use extrinsics from an existing directory instead of re-computing them. This is useful for cases where the intrinsics have not changed, but the extrinsics need to be re-computed with fresh data.
4. Intrinsics Directory: this is a directory containing an existing set of calibration files (e.g. hires_cam1_params.mat, hires_cam2_params.mat, etc.). When calibration, intrinsics will be loaded from the params files instead of computed from raw intrinsics data.
5. Calibration Object (Chessboard): Select the type of calibration object you're using. Options are: 

   * chessboard (simple black/white squares). 

   * April Tag [currently unsupported]: 2D barcodes (similar to QR codes) arranged in a grid with whitespace between each code. Very similar to ArUcOc but with a different code format.

   * ChAruCo [currently unsupported]: combination of chessboard and ArUco. 2D codes overlayed on a black/white chessboard. Most robust calibration method.

6. Internal Chessboard Rows: # of rows made by intersections in the chessboard. This is 1 - # height in black/white squares. E.g. if a chessboard with 10x10 squares would have 9x9 internal verticies.
7. Internal Chessboard Columns: # of columns made by intersections in the chessboard. This is 1 - # width in black/white squares.
8. Square Size (mm): length one chessboard square in mm.

After you click calibrate, it should take about 30 seconds to run. There should be a blue progress bar above the calibration button. The app will close automatically once it's finished, and you can check the python STDOUT for logs and calibration stats.

## Running without the GUI

You can run the calibration pipeline directly as a python module (argparse). This will not launch the GUI.

```
python -m src.calibration.new.calibrate -p "~/olveczky/dannce_data/setupCal11_010324" -r 6 -c 9 -s 23 -o "~/olveczky/dannce_data/setupCal11_010324/calibration_export"
```

## Pytest (WIP)

`python -m pytest src/calibration/new`
