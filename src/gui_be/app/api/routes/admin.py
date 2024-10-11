"""Admin operations E.g. create database, set fake data"""

from pathlib import Path
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from dataclasses import asdict, dataclass
import sqlite3

from app.api.deps import SessionDep
from app.core.db import (
    TABLE_PREDICTION,
    TABLE_VIDEO_FOLDER,
    init_db,
    populate_db,
    populate_real_data,
)
from app.utils.dannce_mat_processing import process_label_mat_file

router = APIRouter()


@router.post("/init-db")
def route_init_db():
    init_db()
    return {"message": "done"}


@router.post("/populate-db")
def route_populate_db():
    init_db()
    populate_db()
    return {"message": "done"}


@router.post("/load-real-data")
def route_load_real_data():
    # init_db()
    populate_real_data()
    return {"message": "done"}


class MirrorDataFolderModel(BaseModel):
    paths: list[str]


def extract_keys_dataclass(x: dataclass, keys_list: list[str]) -> dict:
    return None if x is None else {k: asdict(x)[k] for k in keys_list}


@router.post("/mirror-data-folders")
def mirror_data_folder(session: SessionDep, data: MirrorDataFolderModel):
    """Given a set of data folders on the cluster, create db entries to mirror each folder
    E.g. video_folder, prediction"""

    video_folder_ids = []
    prediction_ids = []

    curr = session.cursor()
    curr.execute("BEGIN")
    try:
        # loop over video folders
        for p in data.paths:
            print("P IS ", p)
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
                curr.execute(
                    f"INSERT INTO {TABLE_PREDICTION} (mode, path, name, status, video_folder) VALUES (?,?,?,?)",
                    (
                        pred[0],
                        str(Path(base_path, pred[0], pred[1])),
                        pred[1],
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