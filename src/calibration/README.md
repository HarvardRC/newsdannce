# Updated calibration scripts and direction for running intrinsic & extrinsic calibration

## Calibration subfolders

Look at README files in each subfolder for more info.

1. `bance_lab_calibration_untracked`: Calibration files from Acq1 & Acq2 machines in Bence's lab (not currently tracked on github)
   - **Intrinsic:** Matlab w. checkerboard
   - **Extrinsic:** opencv (python) w. checkerboard
2. `kyle_dannce2_calibration`: Kyle calibration files, based off original DANNCE calibration 
   - **Intrinsic:** Matlab w. checkboard
   - **Extrinsic:** Matlab w. 5-spire L-Frame 
3. `old_dannce_calibration`: Original DANNCE calibration
   - **Intrinsic:** Matlab w. checkboard
   - **Extrinsic:** Matlab w. L-frame?
4. `new_calibration`: Chris updates to calibration code - will be canonical calibration for newsdannce
   - **Under development**
   - Goals:
     - Remove dependency on matlab
     - Possibly: GUI
     - Better error messages
     - Return calibration accuracy




## Other calibration solutions (not included here)
- Junyu's GUI calibration based on Pyxy3d (WIP) ([link to repo](https://github.com/JohnNan123/pyxy3d_FLIR))
  - adapted specifically for FLIR FLEA3 camera - **wil not work with Basler cameras**
  - Both intrinsic & extrinsic
  - Includes ChArUco board generator
- Iris's custom calibration based on Matlab functions (link TBD)
- Tim's lab: Laser calibration? Link TBD

