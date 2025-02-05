from dataclasses import dataclass
import json
import sqlite3
import traceback

from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app.models import (
    ImportVideoFoldersModel,
)
from app.core.db import TABLE_PREDICTION, TABLE_VIDEO_FOLDER
from pathlib import Path

from app.utils.dannce_mat_processing import process_label_mat_file
from caldannce.calibration_data import CameraParams

from app.utils.predictions import get_prediction_filename
from app.utils.video_processing import (
    get_video_metadata,
)

from app.core.config import settings
from app.base_logger import logger

@dataclass
class VideoFolderComData:
    path: str
    com_labels_file: str


@dataclass
class VideoFolderDannceData:
    path: str
    dannce_labels_file: str


class ComExpEntry(BaseModel):
    label3d_file: Path


class DannceExpEntry(BaseModel):
    label3d_file: Path
    com_file: Path


def get_video_folders_for_com(
    conn: sqlite3.Connection, video_folder_ids: list[int]
) -> list[ComExpEntry]:
    question_string = ",".join(["?"] * len(video_folder_ids))
    rows = conn.execute(
        f"SELECT path, com_labels_file FROM {TABLE_VIDEO_FOLDER} WHERE id IN ({question_string})",
        video_folder_ids,
    ).fetchall()

    if len(rows) < len(video_folder_ids):
        raise Exception("Did not return all video folders requested for coms")
    rows = [dict(row) for row in rows]

    for row in rows:
        logger.info(f"ROW IS {row}")

    rows = [
        ComExpEntry(label3d_file=Path(settings.VIDEO_FOLDERS_FOLDER_EXTERNAL, row["path"], row["com_labels_file"]))
        for row in rows
    ]

    return rows


def get_video_folders_for_dannce(
    conn: sqlite3.Connection, video_folder_ids: list[int]
) -> list[ComExpEntry]:
    question_string = ",".join(["?"] * len(video_folder_ids))
    rows = conn.execute(
        f"""
SELECT
    t1.path,
    t1.dannce_labels_file,
    t2.path AS com_pred_path
FROM {TABLE_VIDEO_FOLDER} t1
LEFT JOIN {TABLE_PREDICTION} t2
    ON t2.id = t1.current_com_prediction
WHERE
    t1.id IN ({question_string})
""",
        video_folder_ids,
    ).fetchall()

    if len(rows) < len(video_folder_ids):
        raise Exception("Did not return all video folders requested for coms")
    rows = [dict(row) for row in rows]

    for row in rows:
        logger.info(f"ROW IS {row}")

    rows = [
        DannceExpEntry(
            label3d_file=Path(settings.VIDEO_FOLDERS_FOLDER_EXTERNAL, row["path"], row["dannce_labels_file"]),
            com_file=Path(settings.PREDICTIONS_FOLDER_EXTERNAL, row["com_pred_path"], get_prediction_filename('COM', row["com_pred_path"])),
        )
        for row in rows
    ]

    return rows


def get_video_folder_path(conn: sqlite3.Connection, video_folder_id: int) -> list[Path]:
    row = conn.execute(
        f"SELECT path from {TABLE_VIDEO_FOLDER} WHERE id=?", (video_folder_id,)
    ).fetchone()
    if not row:
        raise HTTPException(400, f"Video folder for id {id} not found")
    path = Path(row["path"])
    return path


# TODO: FINISH THIS!!! GET COM FILE FOR A DANNCE PREDICTION RUN GIVEN VIDEO FOLDER ID
# use latest COM generation for this purpose
def get_com_file_path(conn: sqlite3.Connection, video_folder_id: int) -> Path:
    row = conn.execute(
        f"SELECT t2.path AS path FROM {TABLE_VIDEO_FOLDER} t1 LEFT JOIN {TABLE_PREDICTION} t2 ON t1.current_com_prediction = t2.id  WHERE t1.id = ?",
        (video_folder_id,),
    ).fetchone()
    if not row:
        raise HTTPException(400, f"Video folder for id {id} not found")
    path = Path(row["path"])
    path = path.joinpath("com3d.mat")
    return path


def import_video_folders_from_paths(
    conn: sqlite3.Connection, data: ImportVideoFoldersModel
):
    """Given a set of data folders on the cluster, create db entries to mirror each folder
    E.g. video_folder, prediction

    Currently: preferred way to import video folders
    """

    video_folder_ids = []
    prediction_ids = []

    curr = conn.cursor()
    curr.execute("BEGIN")
    try:
        # loop over video folders
        for p in data.paths:
            base_path = Path(p)
            if not base_path.is_dir():
                raise Exception(f"Base path does not exist: {base_path}")
            com_data_file = None
            dannce_data_file = None

            for path in base_path.glob("*dannce.mat"):
                info = process_label_mat_file(path)
                if not info:
                    continue
                # go through all files and pick the recent COM and DANNCE file
                if info.is_com:
                    if not com_data_file:
                        com_data_file = info
                    else:
                        if com_data_file.timestamp < info.timestamp:
                            com_data_file = info
                else:  # dannce file
                    if not dannce_data_file:
                        dannce_data_file = info
                    else:
                        if dannce_data_file.timestamp < info.timestamp:
                            dannce_data_file = info

            # CameraParams[] in order
            params = None
            if dannce_data_file:
                params = CameraParams.load_list_from_dannce_mat_file(
                    dannce_data_file.path
                )
            elif com_data_file:
                params = CameraParams.load_list_from_dannce_mat_file(com_data_file.path)
            else:
                calib_folder_maybe = Path(base_path, "calibration")
                try:
                    params = CameraParams.load_list_from_hires_folder(
                        calib_folder_maybe
                    )
                except Exception:
                    logger.warning(f"{traceback.format_exc()}")
                    tmp_dannce_maybe_1 = Path(base_path, "tmp_dannce.mat")
                    if tmp_dannce_maybe_1.exists():
                        params = CameraParams.load_list_from_dannce_mat_file(
                            tmp_dannce_maybe_1
                        )
                    else:
                        tmp_dannce_maybe_2 = Path(base_path, "temp_dannce.mat")
                        if tmp_dannce_maybe_1.exists():
                            params = CameraParams.load_list_from_dannce_mat_file(
                                tmp_dannce_maybe_2
                            )
            if not params:
                raise Exception(
                    f"Unable to find calibration params for this folder: {str(base_path)}"
                )

            params_jsonable = [p.as_dict() for p in params]

            video_metadata = get_video_metadata(base_path)

            # check first video if it's web-ready
            # faststart = check_faststart_flag(
            #     base_path.joinpath("videos", video_metadata.camera_names[0], "0.mp4")
            # )
            # if not faststart:
            #     process_video_folder_faststart(
            #         video_folder_path=base_path,
            #         camera_names=video_metadata.camera_names,
            #     )
            curr.execute(
                f"""
INSERT INTO {TABLE_VIDEO_FOLDER}
    (
        name, path, com_labels_file,
        dannce_labels_file, calibration_params, camera_names,
        n_cameras, n_animals, n_frames,
        duration_s, fps
    )
VALUES
    (?,?,?,
    ?,?,?,
    ?,?,?,
    ?,?)""",
                (
                    base_path.name,
                    str(base_path.resolve()),
                    com_data_file.filename if com_data_file else None,
                    dannce_data_file.filename if dannce_data_file else None,
                    json.dumps(params_jsonable),
                    json.dumps(video_metadata.camera_names),
                    video_metadata.n_cameras,
                    1,  # TODO: support different #'s of animals
                    video_metadata.n_frames,
                    video_metadata.duration_s,
                    video_metadata.fps,
                ),
            )
            video_folder_id = curr.lastrowid
            video_folder_ids.append(video_folder_id)

            # Try to load all predictions from the ./DANNCE folder and ./COM folder
            # Attempt to set the created_at timestamp based on the file edit time (not perfect)

            predictions: list = []
            dannce_data_paths = base_path.glob("DANNCE/*/save_data_AVG0.mat")
            for path in dannce_data_paths:
                predictions.append(
                    (
                        "DANNCE",  # Mode (COM/DANNCE)
                        path.parent.name,  # Name of containing folder
                        int(
                            path.stat().st_mtime
                        ),  # (estimated) creation time of the prediction
                    )
                )

            # com_data_paths = sorted(
            #     com_data_paths, key=lambda x: x.stat().st_mtime, reverse=True
            # )
            com_data_paths = base_path.glob("COM/*/com3d.mat")
            for path in com_data_paths:
                predictions.append(
                    (
                        "COM",  # Mode (COM/DANNCE)
                        path.parent.name,  # Name of containing folder,
                        int(
                            path.stat().st_mtime
                        ),  # (estimated) creation time of the prediction
                    )
                )

            latest_com_pred = (-1, None)  # timestamp, Id
            for pred in predictions:
                pred_name = f"{pred[1]} (imported)"
                pred_mode = pred[0]
                pred_path = str(Path(base_path, pred[0], pred[1]))
                pred_time = pred[2]
                filename = get_prediction_filename(pred_mode, pred_path)
                curr.execute(
                    f"INSERT INTO {TABLE_PREDICTION} (mode, path, name, status, video_folder, filename, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (
                        pred_mode,
                        pred_path,
                        pred_name,
                        "COMPLETED",
                        video_folder_id,
                        filename,
                        pred_time,
                    ),
                )
                prediction_ids.append(curr.lastrowid)

                # Track COM prediction created most recently
                if (pred_mode == "COM") and pred_time > latest_com_pred[0]:
                    latest_com_pred = (pred_time, curr.lastrowid)

            logger.info(f"VIDEO FOLDER ID: {video_folder_id}")
            logger.info(f"LATEST_COM_PRED: {latest_com_pred}")

            if latest_com_pred[1] is not None:


                curr.execute(
                    f"UPDATE {TABLE_VIDEO_FOLDER} SET current_com_prediction = ? WHERE id = ?",
                    (
                        latest_com_pred[1],
                        video_folder_id,
                    ),
                )

    except sqlite3.IntegrityError as e:
        logger.info(f"SQL ERROR: {e}")
        curr.execute("ROLLBACK")
        return JSONResponse(
            content={
                "status": "failed",
                "message": "SQL Integrity Error - perhaps one of the paths is not unique?",
            },
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    except Exception as e:
        logger.warn(f"ERROR: {e}")
        logger.info(f"TRACBACK: {traceback.format_exc()}")
        curr.execute("ROLLBACK")
        raise HTTPException(
            status_code=400,
            detail="Unable to add video data",
        )

    curr.execute("COMMIT")
    return {
        "Message": "Success",
        "video_folder_ids": video_folder_ids,
        "prediction_ids": prediction_ids,
    }

