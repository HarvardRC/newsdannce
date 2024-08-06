# Common Utils across DANNCE functions E.g. dealing with DANNCE file structure, reading/writing to files, etc.
# specifically for DANNCE project file paths
import logging
import os
import re
from dataclasses import dataclass
from functools import reduce
from glob import iglob
from pathlib import Path

import git
from scipy.io import savemat

from src.calibration.calibration_data import CalibrationData

from .extrinsics import ExtrinsicsMediaFormat
from .intrinsics import IntrinsicsParams

IMAGE_EXTENSIONS = [".tiff", ".tif", ".jpeg", ".jpg", ".png"]
"""Possible file extensions for intrinsics calibration images"""
EXTRINSICS_EXTENSIONS = [".mp4", ".tiff", ".tif", ".jpeg", ".jpg", ".png"]

FILENAME_CHARACTER_CLASS = r"[\w\-\. ]"
"""Regex character class representing valid filenames"""

SEP = re.escape(os.path.sep)
"""Short alias for escaped os-specific seperator character (e.g. "\\\\" or "/")"""


def or_regex(alternative_list):
    """Helper function to define a regex which matches a list of alternative options.
    E.g. ["abc", "def"] => /(?:abc|def)/"""
    extensions_regex = (
        "(?:" + "|".join(list(map(lambda x: re.escape(x), alternative_list))) + ")"
    )
    return extensions_regex


@dataclass(frozen=True, slots=True, kw_only=True)
class CameraFilesSingle:
    """Keep track of camera name and paths to extrinsics calibration video & intrinsics calibration images"""

    camera_name: str
    extrinsics_media_path: str
    intrinsics_image_paths: list[str]
    n_images_intrinsics: int


@dataclass(frozen=True, slots=True, kw_only=True)
class CalibrationPathsData:
    """Keeps track of calibration file paths for all cameras"""

    n_cameras: int
    extrinsics_dir: str
    intrinsics_dir: str
    """Base project directory"""
    # data directories per camera (camera idx is corresponding idx in list)
    camera_files: list[CameraFilesSingle]


# example: project_dir='/Users/caxon/olveczky/dannce_data/setupCal11_010324'
def get_calibration_paths(
    intrinsics_dir: str,
    extrinsics_dir: str,
    extrinsics_format: ExtrinsicsMediaFormat,
):
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

    camera_names = get_camera_names(extrinsics_dir=extrinsics_dir)

    if extrinsics_format == ExtrinsicsMediaFormat.VIDEO:
        extrinsics_video_paths = get_extrinsics_video_paths(
            extrinsics_dir=extrinsics_dir, camera_names=camera_names
        )
    else:
        # Image format: ExtrinsicsMediaFormat.IMAGE
        extrinsics_video_paths = get_extrinsics_image_paths(
            extrinsics_dir=extrinsics_dir, camera_names=camera_names
        )

    extrinsics_simplified = list(map(lambda x: x["full_path"], extrinsics_video_paths))

    intrinsics_image_paths = get_intrinsics_image_paths(
        intrinsics_dir=intrinsics_dir, camera_names=camera_names
    )
    intrinsics_simplified = list(map(lambda x: x["full_paths"], intrinsics_image_paths))

    n_cameras = len(camera_names)

    camera_files = []

    for camera_idx in range(n_cameras):
        camera_files.append(
            CameraFilesSingle(
                camera_name=camera_names[camera_idx],
                extrinsics_media_path=extrinsics_simplified[camera_idx],
                intrinsics_image_paths=intrinsics_simplified[camera_idx],
                n_images_intrinsics=len(intrinsics_simplified[camera_idx]),
            )
        )

    calibration_paths_data = CalibrationPathsData(
        n_cameras=n_cameras,
        extrinsics_dir=extrinsics_dir,
        intrinsics_dir=intrinsics_dir,
        camera_files=camera_files,
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
    all_dirs = [x for x in all_files if os.path.isdir(x)]
    search_re = f"{re.escape(project_dir)}(?:{SEP}[Cc]alibration)?{SEP}[Ee]xtrinsics?"
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
    all_dirs = [x for x in all_files if os.path.isdir(x)]
    search_re = f"{re.escape(project_dir)}(?:{SEP}[Cc]alibration)?{SEP}[Ii]ntrinsics?"
    r = re.compile(search_re)
    matching_paths = list(filter(r.fullmatch, all_dirs))
    return matching_paths[0]


# E.g. extrinsics_dir='/Users/caxon/olveczky/dannce_data/setupCal11_010324/extrinsic'
def get_camera_names(extrinsics_dir) -> list[str]:
    """
    Search the extrinsic folder for camera patterns and return the file names.
    Look for files with the format: /[Cc]amera/.+\\.mp4, and extract the camera names.
    """
    # strip trailing slashes if present
    extrinsics_dir = os.path.normpath(extrinsics_dir)
    all_files = list(iglob(os.path.join(extrinsics_dir, "**", "*"), recursive=True))
    # all_dirs = [a for a in all_files if os.path.isdir(a)]
    extensions_regex = or_regex(EXTRINSICS_EXTENSIONS)

    search_re = (
        f"{re.escape(extrinsics_dir)}{SEP}([Cc]amera.+?){SEP}.+?(?:{extensions_regex})"
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
        "file_name": str,
        "full_path": str
    }]
    ```
    Note: return list is sorted by camera name alphabetically
    """
    extrinsics_dir = os.path.normpath(extrinsics_dir)
    # Note: don't recurse - assume first-level files
    all_files = list(iglob(os.path.join(extrinsics_dir, "**", "*"), recursive=True))
    # create regex to match any camera folder name
    camera_names_regex = or_regex(camera_names)

    # FIRST: look for `0.mp4` file
    search_re_1 = (
        f"{re.escape(extrinsics_dir)}{SEP}({camera_names_regex}){SEP}(0\\.mp4)"
    )
    r_1 = re.compile(search_re_1)
    matching_paths_1 = list(filter(None, map(lambda x: r_1.fullmatch(x), all_files)))

    if matching_paths_1:
        matches = matching_paths_1
    else:
        # OTHERWISE: look for `*.mp4` file
        search_re_2 = f"{re.escape(extrinsics_dir)}{SEP}{camera_names_regex}{SEP}{FILENAME_CHARACTER_CLASS}+?\\.mp4"
        r_2 = re.compile(search_re_2)
        matching_paths_2 = list(
            filter(None, map(lambda x: r_2.fullmatch(x), all_files))
        )
        matches = matching_paths_2

    if not matches:
        logging.warning("Unable to find extrinsic video files paths")
        return []

    matches = list(
        map(
            lambda x: {
                "full_path": x.group(0),
                "camera_name": x.group(1),
                "file_name": x.group(2),
            },
            matches,
        )
    )
    matches.sort(key=lambda x: x["camera_name"])
    return matches
    # match.group(0) = full_path, match.group(1) = camera_name, match.group(2) =


def get_extrinsics_image_paths(extrinsics_dir: str, camera_names: list[dict]):
    """
    Camera_names is a list of camera folder names within extrinsics dir.
    See return list from :func:`get_camera_names()`.
    Search in the extrinsics directory and return a single file (e.g. `0.png`)
    Try the following paths, in order, until files are found:
    - $extrinsics_dir/$CAMERA_NAME/0.png
    - $extrinsics_dir/$CAMERA_NAME/*.png

    Return format:
    ```
    list[{
        "camera_name": str,
        "file_name": str,
        "full_path": str
    }]
    ```
    Note: return list is sorted by camera name alphabetically
    """
    extrinsics_dir = os.path.normpath(extrinsics_dir)
    # Note: don't recurse - assume first-level files
    all_files = list(iglob(os.path.join(extrinsics_dir, "**", "*"), recursive=True))
    # create regex to match any camera folder name
    camera_names_regex = or_regex(camera_names)
    extensions_regex = or_regex(EXTRINSICS_EXTENSIONS)

    # FIRST: look for `0.png` file
    search_re_1 = f"{re.escape(extrinsics_dir)}{SEP}({camera_names_regex}){SEP}(0{extensions_regex})"
    r_1 = re.compile(search_re_1)
    matching_paths_1 = list(filter(None, map(lambda x: r_1.fullmatch(x), all_files)))

    if matching_paths_1:
        matches = matching_paths_1
    else:
        # OTHERWISE: look for `*.png` file
        search_re_2 = f"{re.escape(extrinsics_dir)}{SEP}{camera_names_regex}{SEP}{FILENAME_CHARACTER_CLASS}+?\\.png"
        r_2 = re.compile(search_re_2)
        matching_paths_2 = list(
            filter(None, map(lambda x: r_2.fullmatch(x), all_files))
        )
        matches = matching_paths_2

    if not matches:
        logging.warning("Unable to find extrinsic video files paths")
        return []

    matches = list(
        map(
            lambda x: {
                "full_path": x.group(0),
                "camera_name": x.group(1),
                "file_name": x.group(2),
            },
            matches,
        )
    )
    matches.sort(key=lambda x: x["camera_name"])
    return matches


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

    extensions_regex = or_regex(IMAGE_EXTENSIONS)
    camera_names_regex = or_regex(camera_names)

    search_re_1 = f"{re.escape(intrinsics_dir)}{SEP}({camera_names_regex}){SEP}({FILENAME_CHARACTER_CLASS}+?({extensions_regex}))"
    r_1 = re.compile(search_re_1)
    matching_paths_1 = list(filter(None, map(lambda x: r_1.fullmatch(x), all_files)))

    if matching_paths_1:
        matches = matching_paths_1
    else:
        search_re_2 = f"{re.escape(intrinsics_dir)}{SEP}({FILENAME_CHARACTER_CLASS}+){SEP}({FILENAME_CHARACTER_CLASS}+?({extensions_regex}))"
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
    def group_matches(acc_dict, cur_item):
        if cur_item["camera_name"] not in acc_dict:
            acc_dict[cur_item["camera_name"]] = []
        acc_dict[cur_item["camera_name"]].append(cur_item["full_path"])
        return acc_dict

    matches_dict = reduce(group_matches, matches, {})
    matches_grouped = list(
        map(
            lambda item: {"camera_name": item[0], "full_paths": sorted(item[1])},
            matches_dict.items(),
        )
    )

    # group matches by camera_idx and camera_name
    matches_grouped.sort(key=lambda x: x["camera_name"])
    return matches_grouped


# TODO: currently unused
def load_existing_intrinsics(
    existing_intrinsics_dir: str, n_cameras: int
) -> list[IntrinsicsParams]:
    """Load intrinsics specified by a directory containing hires_camX_params.mat files.
    Useful for re-calculating extrinsics with existing intrinsics"""

    logging.info(
        f"Loading intrinsics from params files in directory: {existing_intrinsics_dir}"
    )
    # verify that directory contains hires_cameraX_params.mat files:
    existing_intrinsics_dir = os.path.normpath(existing_intrinsics_dir)

    for cam_idx in range(n_cameras):
        target_filename = f"hires_cam{cam_idx+1}_params.mat"
        target_path = Path(existing_intrinsics_dir, target_filename)
        if not target_path.is_file():
            raise Exception(f"Expected intrinsics file is missing: {target_path}")


def write_calibration_params(
    calibration_data: CalibrationData,
    output_dir: str,
    disable_label3d_format: bool = False,
    include_calibration_json: bool = True,
) -> None:
    """Each calibration file contains the following information in a matlab struct:
    - K [3x3 double] (camera intrinsic transformation matrix)
    - RDistort [1x2 double] (camera rotational lens distortion)
    - TDistort [1x2 double] (camera translational lens distortion)
    - r [3x3 double] (camera pose position)
    - t [1x3 double] (camera pose translation

    ARGS:
    disable_label3d_format: if true, DO NOT convert the intrinsics matrix to matlab format, and transpose the intrinsics matrix (K) for compatibility with Label3D
    """
    os.makedirs(output_dir, exist_ok=True)

    for idx, camera_param in enumerate(calibration_data.camera_params):
        camera_name = f"cam{idx+1}"
        filename = os.path.join(output_dir, f"hires_{camera_name}_params.mat")

        k_modified = camera_param.camera_matrix.copy()
        rotation_matrix_modified = camera_param.rotation_matrix.copy()

        if not disable_label3d_format:
            # convert to matlab intrinsics format:
            # this means add 1 to fx, fy because matlab image origin is (1, 1)
            k_modified[0, 2] += 1
            k_modified[1, 2] += 1

            k_modified = k_modified.T
            rotation_matrix_modified = rotation_matrix_modified.T

        mdict = {
            "K": k_modified,
            "RDistort": camera_param.r_distort,
            "TDistort": camera_param.t_distort,
            "r": rotation_matrix_modified,
            "t": camera_param.translation_vector.reshape((1, 3)),
        }

        savemat(
            file_name=filename,
            mdict=mdict,
        )

        logging.info(f"Saved to: {filename}")

    if include_calibration_json:
        calibration_data.DEV_export_to_file(Path(output_dir, "calibration.json"))


def get_repo_commit_sha():
    try:
        repo = git.Repo()
    except git.InvalidGitRepositoryError:
        # unable to locate git repository - perhaps this package was
        # not installed as a local git repo.
        return "UNAVAILABLE"
    sha = repo.head.object.hexsha
    return sha


def get_verification_files(base_dir, camera_names):
    """Return a list of verification images from a folder: e.g.
    root-folder:
        /Camera1
            /0.png
        ...
        /Camera6
            /0.png
    """
    base_dir = Path(base_dir)
    assert base_dir.is_dir(), "base path must be a directory"

    dirnames = []
    for child in base_dir.iterdir():
        dirnames.append(child.name)

    assert set(dirnames) >= set(
        camera_names
    ), "base directory must have a subdirectory for each camera name"

    # general rules: match 1. png, 2.tiff, 3.j
    file_preference_order = [
        r"0\.png",
        r"0\.bmp",
        r"0\.(?:tiff|tif)",
        r"0\.(?:jpg|jpeg)",
        r"(?!\.).+\.png",
        r"(?!\.).+\.bmp",
        r"(?!\.).+\.(?:tiff|tif)",
        r"(?!\.).+?\.(?:jpg|jpeg)",
        r"0\.mp4",
        r"(?!\.).+\.mp4",
    ]

    def test_filenames(filenames):
        for r in file_preference_order:
            for filename in filenames:
                if re.fullmatch(r, filename):
                    return filename
        return None

    verification_files = []

    for camera_name in sorted(camera_names):
        # return the first filename match alphanumerically
        filenames = sorted([x.name for x in Path(base_dir, camera_name).iterdir()])
        match = test_filenames(filenames)
        if match is None:
            raise Exception(
                "Camera folders do not contain valid image files for verification"
            )
        fullpath = str(Path(base_dir, camera_name, match))
        verification_files.append(fullpath)

    return verification_files
