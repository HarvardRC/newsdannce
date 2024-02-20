# Common Utils across dannce functions E.g. dealing with DANNCE file structure, etc.
# specifically for dannce project file paths

import os
import re
from dataclasses import dataclass
from functools import reduce
from glob import iglob
from scipy.io import savemat
from src.calibration.new.calibration_data import CalibrationData


INTRINSICS_IMAGE_EXTENSIONS = [".tiff", ".tif", ".jpeg", ".jpg", ".png"]
"""Possible file extensions for intrinsics calibration images"""
FILENAME_CHARACTER_CLASS = r"[\w\-\. ]"
"""Regex character class representing valid filenames"""


@dataclass(frozen=True)
class CameraFilesSingle:
    """Keep track of camera name and paths to extrinsics calibration video & intrinsics calibration images"""

    camera_name: str
    extrinsics_video_path: str
    intrinsics_image_paths: list[str]
    n_images_intrinsics: int


@dataclass(frozen=True)
class CalibrationPathsData:
    """Keeps track of calibration file paths for all cameras"""

    n_cameras: int
    extrinsics_dir: str
    intrinsics_dir: str
    project_dir: str
    """Base project directory"""
    # data directories per camera (camera idx is corresponding idx in list)
    camera_files: list[CameraFilesSingle]


# example: project_dir='/Users/caxon/olveczky/dannce_data/setupCal11_010324'
def get_calibration_paths(project_dir: str):
    """
    Given a project directory, return a list of:
    - n_cameras
    - extrinsics_folder [str]
    - intrinsics_folder [str]
    - for each camera [list<str>]
        - intrinsics chessboard picture paths [list<str>]
        - extrinsics video file [str]

    # example project structure
    /$dannce-project-folder
        /calibration
            /extrinsics
                /Camera1
                    /0.mp4
                /Camera2
                    /0.mp4
                ...
            /intrinsics
                /Camera1
                    /file1.tiff
                    /file2.tiff
                    ...
                /Camera2
                    /file1.tiff
                    /file2.tiff
                    ...
                ...
            /parameters (output)
                /hires_cam1_params.mat
                /hires_cam2_params.mat
                ...
        /labeling
            ...
        /videos
            ...
    """
    extrinsics_dir = get_extrinsics_dir(project_dir=project_dir)
    intrinsics_dir = get_intrinsics_dir(project_dir=project_dir)
    camera_names = get_camera_names(extrinsics_dir=extrinsics_dir)
    extrinsics_video_paths = get_extrinsics_video_paths(
        extrinsics_dir=extrinsics_dir, camera_names=camera_names
    )
    intrinsics_image_paths = get_intrinsics_image_paths(
        intrinsics_dir=intrinsics_dir, camera_names=camera_names
    )

    extrinsics_simplified = list(map(lambda x: x["full_path"], extrinsics_video_paths))
    intrinsics_simplified = list(map(lambda x: x["full_paths"], intrinsics_image_paths))

    # double check that # of cameras is consistent
    if not (
        len(camera_names) == len(extrinsics_video_paths) == len(intrinsics_image_paths)
    ):
        raise Exception(
            "Number of cameras is not consistent across intrinsics and extrinsics calibration data folders."
            + f" Extrinsics={len(extrinsics_video_paths)} and Intrinsics={len(intrinsics_image_paths)}"
        )

    n_cameras = len(camera_names)

    camera_files = []

    for camera_idx in range(n_cameras):
        camera_files.append(
            CameraFilesSingle(
                camera_name=camera_names[camera_idx],
                extrinsics_video_path=extrinsics_simplified[camera_idx],
                intrinsics_image_paths=intrinsics_simplified[camera_idx],
                n_images_intrinsics=len(intrinsics_simplified[camera_idx]),
            )
        )

    calibration_paths_data = CalibrationPathsData(
        n_cameras=n_cameras,
        extrinsics_dir=extrinsics_dir,
        intrinsics_dir=intrinsics_dir,
        camera_files=camera_files,
        project_dir=project_dir,
    )

    return calibration_paths_data


def get_extrinsics_dir(project_dir):
    """
    Possible paths for extrinsics folder:
        (?:/calibration)?/[Ee]xtrisics?
    """
    # strip trailing slashes if present
    project_dir = os.path.normpath(project_dir)
    all_files = list(iglob(os.path.join(project_dir, "**", "*"), recursive=True))
    all_dirs = [a for a in all_files if os.path.isdir(a)]
    search_re = f"{re.escape(project_dir)}(?:{os.path.sep}[Cc]alibration)?{os.path.sep}[Ee]xtrinsics?"
    r = re.compile(search_re)
    matching_paths = list(filter(r.fullmatch, all_dirs))
    return matching_paths[0]


def get_intrinsics_dir(project_dir):
    """
    Possible paths for intrinsics folder:
        (?:/calibration)?/[Ii]ntrinsics?
    """
    # strip trailing slashes if present
    project_dir = os.path.normpath(project_dir)
    all_files = list(iglob(os.path.join(project_dir, "**", "*"), recursive=True))
    all_dirs = [a for a in all_files if os.path.isdir(a)]
    search_re = f"{re.escape(project_dir)}(?:{os.path.sep}[Cc]alibration)?{os.path.sep}[Ii]ntrinsics?"
    r = re.compile(search_re)
    matching_paths = list(filter(r.fullmatch, all_dirs))
    return matching_paths[0]


# E.g. extrinsics_dir='/Users/caxon/olveczky/dannce_data/setupCal11_010324/extrinsic'
def get_camera_names(extrinsics_dir) -> list[str]:
    """
    Search the extrinsic folder for camera patterns and return the file names.
    Look for files with the format: /[Cc]amera/.+\.mp4, and extract the camera names.
    """
    # strip trailing slashes if present
    extrinsics_dir = os.path.normpath(extrinsics_dir)
    all_files = list(iglob(os.path.join(extrinsics_dir, "**", "*"), recursive=True))
    # all_dirs = [a for a in all_files if os.path.isdir(a)]
    search_re = (
        f"{re.escape(extrinsics_dir)}{os.path.sep}([Cc]amera.+?){os.path.sep}.+?\.mp4"
    )
    r = re.compile(search_re)
    matching_paths = filter(None, map(lambda x: r.fullmatch(x), all_files))
    camera_names = map(lambda x: x.groups(1)[0], matching_paths)
    camera_names_unique = sorted(set(camera_names))
    return camera_names_unique


def get_extrinsics_video_paths(extrinsics_dir: str, camera_names: list[dict]):
    """
    Camera_names is a list of camera folder names within extrinsics dir.
    See return list from :func:`get_camera_names()`.
    Search in the extrinsics directory and return a single file (e.g. `0.mp4`)
    Try the following paths, in order, until files are found:
    - $extrinsics_dir/$CAMERA_NAME/0.mp4
    - $extrinsics_dir/$CAMERA_NAME/*.mp4

    Return format:
    ```
    list[{
        "camera_name": str,
        "video_file_name": str,
        "full_path": str
    }]
    ```
    Note: return list is sorted by camera name alphabetically
    """
    extrinsics_dir = os.path.normpath(extrinsics_dir)
    # Note: don't recurse - assume first-level files
    all_files = list(iglob(os.path.join(extrinsics_dir, "**", "*"), recursive=True))
    # create regex to match any camera folder name
    camera_names_regex = "|".join(
        list(map(lambda x: f"(?:{re.escape(x)})", camera_names))
    )

    # FIRST: look for `0.mp4` file
    search_re_1 = f"{re.escape(extrinsics_dir)}{os.path.sep}({camera_names_regex}){os.path.sep}(0\.mp4)"
    r_1 = re.compile(search_re_1)
    matching_paths_1 = list(filter(None, map(lambda x: r_1.fullmatch(x), all_files)))

    if matching_paths_1:
        matches = matching_paths_1
    else:
        # OTHERWISE: look for `*.mp4` file
        search_re_2 = f"{re.escape(extrinsics_dir)}{os.path.sep}{camera_names_regex}{os.path.sep}{FILENAME_CHARACTER_CLASS}+?\.mp4"
        r_2 = re.compile(search_re_2)
        matching_paths_2 = list(
            filter(None, map(lambda x: r_2.fullmatch(x), all_files))
        )
        matches = matching_paths_2

    if not matches:
        print("Unable to find extrinsic video files paths")
        return []

    matches = list(
        map(
            lambda x: {
                "full_path": x.group(0),
                "camera_name": x.group(1),
                "video_file_name": x.group(2),
            },
            matches,
        )
    )
    matches.sort(key=lambda x: x["camera_name"])
    return matches
    # match.group(0) = full_path, match.group(1) = camera_name, match.group(2) =


def get_intrinsics_image_paths(intrinsics_dir, camera_names):
    """
    Get file paths of intrinsics calibration images
    Try the following paths, in order:
     - $intrinsics_dir/$CAMERA_NAME/*($EXTENSION_REGEX)
     - $intrinsics_dir/*/*($EXTENSION_REGEX)
     e.g. $intrinsics_dir/Camera1/12.tiff

    Assumes that all image files are the same extension.

    Return format:
    ```
    list[{
        "camera_name": str,
        "full_paths": list[str]
    }]
    ```
    """
    intrinsics_dir = os.path.normpath(intrinsics_dir)
    all_files = list(iglob(os.path.join(intrinsics_dir, "**", "*"), recursive=True))
    # create regex to match any camera folder name
    extensions_regex = "|".join(
        list(map(lambda x: f"(?:{re.escape(x)})", INTRINSICS_IMAGE_EXTENSIONS))
    )
    camera_names_regex = "|".join(
        list(map(lambda x: f"(?:{re.escape(x)})", camera_names))
    )
    search_re_1 = f"{re.escape(intrinsics_dir)}{os.path.sep}({camera_names_regex}){os.path.sep}({FILENAME_CHARACTER_CLASS}+?({extensions_regex}))"
    r_1 = re.compile(search_re_1)
    matching_paths_1 = list(filter(None, map(lambda x: r_1.fullmatch(x), all_files)))

    if matching_paths_1:
        matches = matching_paths_1
    else:
        search_re_2 = f"{re.escape(intrinsics_dir)}{os.path.sep}({FILENAME_CHARACTER_CLASS}+){os.path.sep}({FILENAME_CHARACTER_CLASS}+?({extensions_regex}))"
        r_2 = re.compile(search_re_2)
        matching_paths_2 = list(
            filter(None, map(lambda x: r_2.fullmatch(x), all_files))
        )
        matches = matching_paths_2

    if not matches:
        raise Exception("Unable to find intrinsics image files paths")

    matches = list(
        map(
            lambda x: {
                "full_path": x.group(0),
                "camera_name": x.group(1),
                "file_name": x.group(2),
                "file_extension": x.group(3),
            },
            matches,
        )
    )

    # make sure all image files found are the same extension
    unique_extensions = set(map(lambda x: x["file_extension"], matches))
    if len(unique_extensions) > 1:
        raise Exception(
            f"Multiple image extensions found in intrinsics folder: {list(unique_extensions)}"
        )

    # group matches reduce function
    def group_matches(acc_dict, cur):
        if cur["camera_name"] not in acc_dict:
            acc_dict[cur["camera_name"]] = []
        acc_dict[cur["camera_name"]].append(cur["full_path"])
        return acc_dict

    matches_dict = reduce(group_matches, matches, {})
    matches_grouped = list(
        map(
            lambda item: {"camera_name": item[0], "full_paths": item[1]},
            matches_dict.items(),
        )
    )
    # group matches by camera_idx and camera_name
    matches_grouped.sort(key=lambda x: x["camera_name"])
    return matches_grouped


def write_calibration_params(
    calibration_data: CalibrationData, output_dir: str
) -> None:
    """Each calibration file contains the following information in a matlab struct:
    - K [3x3 double] (camera intrinsic transformation matrix)
    - RDistort [1x2 double] (camera rotational lens distortion)
    - TDistort [1x2 double] (camera translational lens distortion)
    - r [3x3 double] (camera pose position)
    - t [1x3 double] (camera pose translation
    """

    os.makedirs(output_dir, exist_ok=True)

    for idx, camera_param in enumerate(calibration_data.camera_params):
        camera_name = f"cam{idx+1}"
        filename = os.path.join(output_dir, f"hires_{camera_name}_params.mat")

        mdict = {
            "K": camera_param.camera_matrix.T,
            "RDistort": camera_param.r_distort,
            "TDistort": camera_param.t_distort,
            "r": camera_param.rotation_matrix,
            "t": camera_param.translation_vector.reshape((1, 3)),
        }

        savemat(
            file_name=filename,
            mdict=mdict,
        )

        print(f"Saved calibration data to filename: {filename}")
