# NewsDANNCE: DANNCE and Utilities

## Calibration

GUI to generate camera parameters for use in Label3D and DANNCE.

Steps to run:

1. create environment (required only for initial setup or version upgrade)
    `mamba env create -f ./src/calibration/environment.yml`
2. install caldannce (required only for initial setup or version upgrade)
    `cd src/calibration && pip install --force-reinstall .`
3. activate environment
    `mamba activate dannce-dev`
4. start gui with the command 
    `python -m caldannce.gui`

### Calibration Page

Select the following directories:
**Intrinsics Directory**: Folder containing sub-folders for each camera. Each folder contains multiple image files (tiff/png/bmp) where each file is a picture of the calibration target from that camera. You can use intrinsics from a previous calibration if the camera lense/focus/etc. has not been modified.
**Extrinsics Directory**: Folder containing sub-folders for each camera. Each folder contains a single image file (tiff/png/bmp) or video (mp4) of the calibration target.
**Parameter Output Directory**: Folder where camera parameters will be placed after generation. This folder will be created if it does not exist.

Calibration Target Options:
**Rows**: Number of verticies in a row of the chessboard calibration target. This is `(# of squares in a row) - 1`.
**Columns**: Number of internal verticies in a column of the chessboard target. This is `(# of squares in a column) - 1`.
**Square Size**: Length of each square on the chessboard calibration target, measured in mm.

Other options:
**Extrinsincs Format**: Specify the filetype of the extrinsincs media. It can either be a single image file per camera folder (tiff/png/bmp), or a video recording (mp4) from each camera folder. If extrinsics format is a video, the first frame will be used for calibration.

Once all options are filled in, click "Run Calibration". This will take between 10 seconds and 5 minutes, depending on the number of images and cameras. The progress bar will increase for every camera processed. When GUI goes to the next page, the calibration step is done and parameters will be writeen to the output directory.

### Calibration Results Page

This page contains logs for debugging and calibration results. Reprejection error is measured in pixels.

### Validation Page

This page lets you validate the calibration parameters you have generated. For each camera tab, click "Select Image for Camera" to load an image of the same scene. Alternatively click "Load All" and select a folder containing one subfolder per camera, where each subfolder contains an image file. Images loaded will be undistorted to remove lens distortion using intrinsics parameters.

For each camera, select a keypoint, which will show up as a red dot. Clicks on the image without zoom/pan selected will create or replace a keypoint. You can zoom/pan to choose a more precise point. For each camera, the keypoint you select should represent the same point in 3D space. Clicking again after selecting a keypoint will move the keypoint to the new coordinates clicked.

Once you have selected 1x keypoint per image, you can click "Run Validation" which will triangulate the world point and re-project the point onto each camera view. 

After running validation, the results page will show the average distance between the selected point and the reprojected point for each camera, measured in pixels.

If you click through the camera tabs, you can see the location of the reprojected point as a blue dot. You can select different points and click "Run Validation" again to triangulate a new point.


## Overview

Conda env setup

1. install conda/mamba/micromamba, etc.

```
conda create --name sdannce311 python=3.11
conda activate sdannce311
conda install pytorch torchvision torchaudio pytorch-cuda=12.1 -c pytorch -c nvidia
pip install setuptools

```

## Developer Setup

VSCode recommended.

Recommended vscode extensions:
* Ruff python linter extension: [Link](https://marketplace.visualstudio.com/items?itemName=charliermarsh.ruff)



## Configure git for this repo

Ignore formatting commits when assigning git blame:

`git config --local blame.ignoreRevsFile .git-blame-ignore-revs`

# Testing

Please run the full pytest before submitting a PR:

currently the best command is:

```
py.test --ignore=tests/dannce --ignore=docs  --ignore=src
```

There should be no errors.
