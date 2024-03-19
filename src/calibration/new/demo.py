from .calibrate import do_calibrate

do_calibrate(
    project_dir="/Users/caxon/olveczky/dannce_data/calibration benchmark",
    rows=6,
    cols=9,
    square_size_mm=23,
    save_rpe=True,
    convert_to_matlab=False,
)
