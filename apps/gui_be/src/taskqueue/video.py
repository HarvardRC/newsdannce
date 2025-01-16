from dataclasses import dataclass
from pathlib import Path
import re
import subprocess
import shutil
from typing import Literal
from app.utils.helpers import make_resource_folder_name
from app.utils.video_folders import process_label_mat_file
from app.core.config import settings
from caldannce.calibration_data import CameraParams
import json
import time

import logging as logger

from app.utils.dannce_mat_processing import MatFileInfo
from app.core.db import TABLE_PREDICTION, TABLE_VIDEO_FOLDER, get_db_context
from app.utils.video_processing import get_video_metadata

# from taskqueue.celery import celery_app
from taskqueue.celery import celery_app

logger.basicConfig(level=logger.INFO)

@celery_app.task
def dummy_task_me():
    time.sleep(5)
    return {"success": "abcdefz"}

@celery_app.task
def import_video_folder_worker(video_folder_path: str| Path):
    start = time.time()
    video_folder_path_src = Path(video_folder_path)

    #0. check if video has already been imported and added to db
    if _check_video_folder_already_imported(video_folder_path_src):
        logger.warning("Video folder has already been imported and added to db")
        raise Exception("Video folder has already been imported")

    #1. create a new folder for video_folder
    logger.info(f"Importing video folder: {video_folder_path_src}")
    video_folder_path_dest =Path(settings.VIDEO_FOLDERS_FOLDER , make_resource_folder_name())
    video_folder_path_dest.mkdir(mode=0o777,parents=True, exist_ok=False)
    logger.info(f"Created new dest folder: {video_folder_path_dest}")
    video_folder_path_dest.joinpath("metadata.txt").write_text(f"src: {video_folder_path_src}")
    video_metadata = get_video_metadata(video_folder_path_src)

    #2. copy and reencode video files
    _copy_reencode_video_folder(video_folder_path_src, video_folder_path_dest)

    #3. identify calibration parameters and any label3d files
    ret = _identify_copy_calibration_params(video_folder_path_src, video_folder_path_dest)
    params = ret['params']
    dannce_label_file = ret['dannce_label_file']
    com_label_file = ret['com_label_file']

    #4. write video folder to database
    video_folder_id = _write_video_folder_to_db(
        video_folder_path_src,
        video_folder_path_dest,
        com_label_file,
        dannce_label_file,
        params,
        video_metadata
    )

    #5. identify any predection files
    predictions = _identify_and_copy_prediction_files(video_folder_path_src)

    #6. write predictions to database
    prediction_ids = _write_predictions_to_db(predictions, video_folder_id)

    ellapsed_seconds = time.time() - start
    logger.info(f"Importing video took {ellapsed_seconds} s")
    return {"success": True, "video_folder_id": video_folder_id, "prediction_ids": prediction_ids}

# video tasks:
# 1. clone video and reencode
def _copy_reencode_video_folder(src: Path, dest: Path):
    """For each video folder:
    1. copy the video into the instance folder
    2. (simulatneous) re-save the video with fast-start enabled
    """
    src_path = Path(src)
    dest_path = Path(dest)

    # 1. check if fast-start is enabled
    vid0= next(_enumerate_video_files(src_path, dest_path))[0]
    if _check_faststart_flag(vid0):
        COPY_MODE="FFMPEG"
    else:
        COPY_MODE="OS"

    logger.info(f"Copying videos from {src_path} to {dest_path} using {COPY_MODE}")
    for i, [src_file, dest_file] in enumerate(_enumerate_video_files(src_path, dest_path)):
        dest_file.parent.mkdir(mode=0o777, parents=True, exist_ok=True)
        if COPY_MODE == "FFMPEG":
            output = subprocess.run(
                [
                    "ffmpeg",
                    "-i",
                    str(src_file),
                    "-c",
                    "copy",
                    "-movflags",
                    "+faststart",
                    "-abort_on",
                    "empty_output",
                    str(dest_file),
                ],
                capture_output=True,
                text=True,)
        else:
            # Use subprocess because these are big files and performance matters
            assert COPY_MODE=="OS"
            output = subprocess.run(
                [
                    "cp",
                    str(src_file),
                    str(dest_file),
                ],
                capture_output=True,
                text=True,)
        try:
            output.check_returncode()
        except subprocess.CalledProcessError:
            print(f"Error processing: {output.stderr}")
            raise Exception(f"Unable to process video file:{src_file}")
        logger.info(f"Copied file {i}")
    logger.info("Copied all video files")


def _check_faststart_flag(video_file: str | Path):
    """Test if a video has the faststart flag (i.e. ready for web streaming)
    If not, you may want to run process_video_folder_faststart"""
    # ffmpeg -v trace -i "%%i" NUL 2>&1 | grep -m 1 -o -e "type:'mdat'" -e "type:'moov'"
    vid0 = Path(video_file)
    if not vid0.exists():
        raise Exception("Video file does not exist or is not mounted properly")

    output = subprocess.run(
        (
            "ffmpeg",
            "-v",
            "trace",
            "-i",
            str(vid0),
        ),
        capture_output=True,
        text=True,
    )
    match_mdat = re.search(r"type:'mdat'", output.stderr)
    match_moov = re.search(r"type:'moov'", output.stderr)
    if not match_mdat and not match_moov:
        raise Exception(
            f"Video file does not have expected H.264 Atoms: file={str(vid0)}"
        )
    if match_mdat.span()[0] < match_moov.span()[0]:
        # mdat before moov: not web ready
        return False
    else:
        # moov before mdat: is web ready
        return True


def _enumerate_video_files(src_video_folder_path: Path, dest_video_folder_path: Path):
    """Return a generator which enumerates all video files to copy.
    Each yield returns a tuple with: [src: Path, dest: Path]"""
    metadata = get_video_metadata(src_video_folder_path)
    camnames = metadata.camera_names
    for camname in camnames:
        src_path = src_video_folder_path.joinpath("videos", camname, "0.mp4")
        dest_path = dest_video_folder_path.joinpath("videos", camname, "0.mp4")
        yield (src_path, dest_path)
    return


@dataclass
class IdentifyCalibrationParamsReturn:
    params: list[CameraParams]
    dannce_label_file: Path
    com_label_file: Path


def _identify_copy_calibration_params(video_folder_path_src:Path, video_folder_path_dest:Path) -> IdentifyCalibrationParamsReturn:
    # find any com_label_files (X_dannce.mat)
    # find any dannce_label_files (X_dannce.mat)
    # find any tmp_dannce.mat files

    com_label_files_info:list[MatFileInfo] = []
    dannce_label_files_info:list[MatFileInfo] = []
    tmp_files:list[MatFileInfo] = []

    for path in video_folder_path_src.glob("*dannce.mat"):
        info = process_label_mat_file(path)
        if path.name=="tmp_dannce.mat" or path.name=="temp_dannce.mat":
            tmp_files.append(path)
        elif info.is_com:
            com_label_files_info.append(info)
        else:  # dannce file
            dannce_label_files_info.append(info)

    latest_com_label = max(com_label_files_info, key=lambda x: x.timestamp, default=None)

    latest_dannce_label = max(dannce_label_files_info, key=lambda x: x.timestamp, default=None)

    # 4. copy dannce.mat files to the new directory
    if latest_com_label:
        shutil.copy2(latest_com_label.path, video_folder_path_dest)
    if latest_dannce_label:
        shutil.copy2(latest_dannce_label.path, video_folder_path_dest)

    # find calibration parameters by trying, in order:
    # 1. dannce label dannce.mat files
    # 2. com label dannce.mat files
    # 3. calibration folder
    # 4. tmp_dannce.mat files

    params = None

    if latest_dannce_label:
        logger.info(f"Using params from DANNCE labels file: {latest_dannce_label.filename}")
        params = CameraParams.load_list_from_dannce_mat_file(latest_dannce_label.path)

    if not params and latest_com_label:
        logger.info(f"Using params from COM labels file: {latest_com_label.filename}")
        params = CameraParams.load_list_from_dannce_mat_file(latest_com_label.path)

    if not params:
        logger.info("Using params from calibration folder")
        calib_folder = Path(video_folder_path_src, "calibration")
        if calib_folder.is_dir():
            try:
                params = CameraParams.load_list_from_hires_folder(calib_folder)
            except Exception:
                pass

    if not params and len(tmp_files) > 1:
        logger.info(f"Using params from tmp_dannce.mat: {tmp_files[0]}")
        params = CameraParams.load_list_from_dannce_mat_file(tmp_files[0])

    if not params:
        raise Exception(f"Unable to locate params for video folder: {str(video_folder_path_src)}")

    params_jsonable = [p.as_dict() for p in params]

    return {
        "params": params_jsonable,
        "com_label_file": Path(latest_com_label.filename) if latest_com_label else None,
        "dannce_label_file": Path(latest_dannce_label.filename) if latest_dannce_label else None,
    }

@dataclass
class PredictionInfo:
    mode:Literal["DANNCE","COM"]
    src_file: str
    src_name: str
    dest_folder_name: Path
    file_created_time: int

def _identify_and_copy_prediction_files(src_video_folder_path: Path) -> list[PredictionInfo]:
    predictions: list = []

    dannce_data_paths = src_video_folder_path.glob("DANNCE/*/save_data_AVG.mat")
    for src_path in dannce_data_paths:
        src_folder_name = src_path.parent.name
        dest_folder_name = f"DANNCE_{make_resource_folder_name()}"
        dest_folder_path = settings.PREDICTIONS_FOLDER.joinpath(dest_folder_name)
        dest_folder_path.mkdir()

        shutil.copy2(src_path, dest_folder_path)
        dest_folder_path.joinpath("metadata.txt").write_text(f"src: {str(src_path)}\n")

        predictions.append(
            PredictionInfo(
                mode="DANNCE",
                src_file=str(src_path),
                src_name=src_folder_name,  # Name of containing folder
                dest_folder_name=dest_folder_name,
                file_created_time=int(
                    src_path.stat().st_mtime
                ),  # (estimated) creation time of the prediction
            )
        )

    com_data_paths = src_video_folder_path.glob("COM/*/com3d.mat")
    for src_path in com_data_paths:
        src_folder_name = src_path.parent.name
        dest_folder_name = f"COM_{make_resource_folder_name()}"
        dest_folder_path = settings.PREDICTIONS_FOLDER.joinpath(dest_folder_name)
        dest_folder_path.mkdir()

        shutil.copy2(src_path, dest_folder_path)
        dest_folder_path.joinpath("metadata.txt").write_text(f"src: {str(src_path)}\n")

        predictions.append(
            PredictionInfo(
                mode="COM",
                src_file=str(src_path),
                src_name=src_folder_name,  # Name of containing folder
                dest_folder_name=dest_folder_name,
                file_created_time=int(
                    src_path.stat().st_mtime
                ),  # (estimated) creation time of the prediction
            )
        )

    return predictions


def _write_video_folder_to_db(
        video_folder_path_src,
        video_folder_path_dest,
        com_data_file,
        dannce_data_file,
        params_jsonable,
        video_metadata
    ):
    with get_db_context() as conn:
        curr = conn.cursor()
        curr.execute("BEGIN")
        curr.execute(f"""
INSERT INTO {TABLE_VIDEO_FOLDER}
    (
        name,
        path,
        src_path,
        com_labels_file,
        dannce_labels_file,
        calibration_params,
        camera_names,
        n_cameras,
        n_animals,
        n_frames,
        duration_s,
        fps
    )
    VALUES
    (?,?,?, ?,?,?, ?,?,?, ?,?,?)
""", (
    (
        video_folder_path_src.name, #name
        str(video_folder_path_dest.name), #path
        str(video_folder_path_src), #src_path
        str(com_data_file), #com_labels_data (may be None)
        str(dannce_data_file), #dannce_labels_data (may be None)
        json.dumps(params_jsonable), #calibration_params
        json.dumps(video_metadata.camera_names), #camera_names
        video_metadata.n_cameras, #n_cameras
        1,  #n_animals # TODO: support different #'s of animals
        video_metadata.n_frames, #n_frames
        video_metadata.duration_s, #duration_s
        video_metadata.fps, #fps
     )
))
        curr.execute("COMMIT")
        video_folder_id = curr.lastrowid
        logger.info(f"INSERTED VIDEO FOLDER WITH ID {video_folder_id}")
        return video_folder_id


def _write_predictions_to_db(
    predictions: list[PredictionInfo],
    video_folder_id: int
):
    prediction_ids = []
    with get_db_context() as conn:
        curr = conn.cursor()
        curr.execute("BEGIN")

        for pred in predictions:
            pred_mode = pred.mode
            pred_path = str(pred.dest_folder_name)
            pred_src_path = str(pred.src_file)
            pred_name = f"{pred.src_name} (imported)"
            pred_status = 'COMPLETED'
            pred_video_folder = video_folder_id
            pred_created_at = pred.file_created_time

            print(pred_mode)
            print(pred_path)
            print(pred_src_path)
            print(pred_name)
            print(pred_status)
            print(pred_video_folder)
            print(pred_created_at)

            curr.execute(
f"""
INSERT INTO {TABLE_PREDICTION}
    (
        mode,
        path,
        src_path,
        name,
        status,
        video_folder,
        created_at
    )
    VALUES
    (?,?,?, ?,?,?, ?)
""", (
    pred_mode,
    pred_path,
    pred_src_path,
    pred_name,
    pred_status,
    pred_video_folder,
    pred_created_at
))
            prediction_id = curr.lastrowid
            prediction_ids.append(prediction_id)
            logger.info(f"Inserted prediction with id: {prediction_id}")

        curr.execute("COMMIT")
        logger.info(f"Done inserting {len(predictions)} predictions to db (+commit)")

    return prediction_ids


def _check_video_folder_already_imported(video_folder_path_src: Path):
    with get_db_context() as db:
        row = db.execute(
            f"""
SELECT id FROM {TABLE_VIDEO_FOLDER}
WHERE src_path=?
""",
    (
        str(video_folder_path_src),
    )).fetchone()
        if row:
            return True
        else:
            return False
