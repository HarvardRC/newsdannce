import argparse
from pathlib import Path
import shutil


COM_CONFIG_BASE = "./src/dannce_gui/templates/com_config_base.yaml"
DANNCE_CONFIG_BASE = "./src/dannce_gui/templates/dannce_config_base.yaml"
IO_BASE = "./src/dannce_gui/templates/io_base.yaml"

# directory structure:
# --------------------
# $base_dir/
#   configs/
#     dannce_config.yaml
#     com_config.yaml
#   calibration/
#     hires_cam1_params.mat
#     hires_cam2_params.mat
#     [...]
#   videos/
#     Camera1/
#        0.mp4
#     Camera2/
#        0.mp4
#     [...]
#   SDANNCE/
#     predict01/
#     train01/
#   COM/
#     predict01/
#     train01/
#   io.yaml
#   Label3D_dannce.mat


def make_project(base_dir: str):
    base_dir = Path(base_dir)

    # delete and re-create the directory if it already exists
    shutil.rmtree(base_dir)

    configs_dir = Path(base_dir, "configs")
    calibration_dir = Path(base_dir, "calibration")
    videos_dir = Path(base_dir, "videos")
    io_yaml_file = Path(base_dir, "io.yaml")
    label3d_file = Path(base_dir, "label3d_dannce.mat")
    dannce_config_yaml = Path(configs_dir, "dannce_config.yaml")
    com_config_yaml = Path(configs_dir, "com_config.yaml")

    # make directories
    base_dir.mkdir(exist_ok=True, mode=0o770)
    configs_dir.mkdir(mode=0o770)
    calibration_dir.mkdir(mode=0o770)
    videos_dir.mkdir(mode=0o770)

    # make files
    io_yaml_file.touch(mode=0o770)
    label3d_file.touch(mode=0o770)
    dannce_config_yaml.touch(mode=0o770)
    com_config_yaml.touch(mode=0o770)

    shutil.copy(COM_CONFIG_BASE, com_config_yaml)
    shutil.copy(DANNCE_CONFIG_BASE, dannce_config_yaml)
    shutil.copy(IO_BASE, io_yaml_file)

    print("base dir", base_dir)


if __name__ == "__main__":
    print("Hello world")
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-d", "--base-dir", help="Base directory (relative to current dir)"
    )

    args = parser.parse_args()

    make_project(base_dir=args.base_dir)
