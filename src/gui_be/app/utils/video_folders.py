from dataclasses import dataclass
import sqlite3

from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app.api.routes.video_folder import ImportVideoFoldersModel
from app.core.db import TABLE_PREDICTION, TABLE_VIDEO_FOLDER
from pathlib import Path

from app.utils.dannce_mat_processing import process_label_mat_file


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
        print("ROW IS ", row)

    rows = [
        ComExpEntry(label3d_file=Path(row["path"], row["com_labels_file"]))
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


def import_video_folders_from_paths(
    conn: sqlite3.Connection, data: ImportVideoFoldersModel
):
    """Given a set of data folders on the cluster, create db entries to mirror each folder
    E.g. video_folder, prediction"""

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

            # If we still haven't found a dannce.mat file, then we check tmp_dannce.mat for calibration
            # try:
            #     params =

            curr.execute(
                f"""INSERT INTO {TABLE_VIDEO_FOLDER} (name, path, com_labels_file, dannce_labels_file) VALUES (?,?,?,?)""",
                (
                    base_path.name,
                    str(base_path.resolve()),
                    com_data_file.filename if com_data_file else None,
                    dannce_data_file.filename if dannce_data_file else None,
                ),
            )
            video_folder_id = curr.lastrowid
            video_folder_ids.append(video_folder_id)

            predictions = []
            for path in base_path.glob("DANNCE/*/save_data_AVG.mat"):
                predictions.append(
                    (
                        "DANNCE",
                        path.parent.name,
                    )
                )
            for path in base_path.glob("COM/*/com3d.mat"):
                predictions.append(
                    (
                        "COM",
                        path.parent.name,
                    )
                )

            for pred in predictions:
                pred_name = f"{pred[1]} (imported)"
                pred_mode = pred[0]
                pred_path = str(Path(base_path, pred[0], pred[1]))
                curr.execute(
                    f"INSERT INTO {TABLE_PREDICTION} (mode, path, name, status, video_folder) VALUES (?,?,?,?,?)",
                    (
                        pred_mode,
                        pred_path,
                        pred_name,
                        "COMPLETED",
                        video_folder_id,
                    ),
                )
                prediction_ids.append(curr.lastrowid)

    except sqlite3.IntegrityError as e:
        print("SQL ERROR", e)
        return JSONResponse(
            content={
                "status": "failed",
                "message": "SQL Integrity Error - perhaps one of the paths is not unique?",
            },
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    except Exception as e:
        print("ERROR: ", e)
        curr.execute("ROLLBACK")
        raise HTTPException(
            status_code=400,
            detail="SQLITE3 Error. Transaction rolled back",
        )

    curr.execute("COMMIT")
    return {
        "Message": "Success",
        "video_folder_ids": video_folder_ids,
        "prediction_ids": prediction_ids,
    }
