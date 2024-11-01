# from sqlite3 import Connection
# from typing import Any, Annotated
import logging
from pathlib import Path
from typing import Any
import uuid
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from app.api.deps import SessionDep
from app.core.db import (
    TABLE_PREDICT_JOB,
    TABLE_SLURM_JOB,
    TABLE_VIDEO_FOLDER,
)
from app.models import CreateVideoFolderModel, ImportVideoFoldersModel

from app.utils.dannce_mat_processing import (
    get_labeled_data_in_dir,
    get_predicted_data_in_dir,
)
from app.utils.video import get_one_frame
from app.utils.video_folders import import_video_folders_from_paths
from app.core.config import settings
import subprocess


router = APIRouter()


@router.get("/list")
def list_all_video_folder(session: SessionDep):
    rows = session.execute(f"SELECT * FROM {TABLE_VIDEO_FOLDER}").fetchall()
    rows = [dict(x) for x in rows]
    return rows


@router.post("/")
def create_video_folder(data: CreateVideoFolderModel, session: SessionDep) -> Any:
    curr = session.cursor()
    curr.execute(
        f"INSERT INTO {TABLE_VIDEO_FOLDER} (name, path) VALUES (?,?)",
        (data.name, data.path),
    )
    insert_id = curr.lastrowid
    session.commit()

    return {"id": insert_id}


@router.post("/import_from_paths")
def import_video_folders_route(session: SessionDep, data: ImportVideoFoldersModel):
    return import_video_folders_from_paths(session, data)


@router.get("/{id}/frame")
def get_frame_route(
    id: int, frame_index: int, camera_name: str, session: SessionDep
) -> Any:
    row = session.execute(
        f"SELECT * FROM {TABLE_VIDEO_FOLDER} WHERE ID=?", (id,)
    ).fetchone()
    if not row:
        raise HTTPException(status_code=404)

    row = dict(row)
    video_path = Path(row["path"], "videos", camera_name, "0.mp4")
    if not video_path.exists():
        return HTTPException(404, "Video does not exist")

    out_filename = f"frame_{id}_{frame_index}_{camera_name}-{uuid.uuid4().hex}.png"

    try:
        get_one_frame(
            video_path=video_path, frame_index=frame_index, output_name=out_filename
        )
    except BaseException as e:
        raise HTTPException(400, f"Unable to extract frame from video {e}")

    return FileResponse(out_filename, status_code=200)


@router.get("/{id}/preview")
def get_preview_route(id: int, camera_name: str, session: SessionDep) -> Any:
    row = session.execute(
        f"SELECT * FROM {TABLE_VIDEO_FOLDER} WHERE ID=?", (id,)
    ).fetchone()
    if not row:
        raise HTTPException(status_code=404)

    row = dict(row)
    video_path = Path(row["path"], "videos", camera_name, "0.mp4")
    if not video_path.exists():
        return HTTPException(404, "Video does not exist")

    out_filename = f"preview_{id}_{camera_name}-{uuid.uuid4().hex}.mp4"
    out_path = Path(settings.STATIC_TMP_FOLDER, out_filename).resolve()

    # 50 FPS = 0.02 Sec/Frame = 20ms/frame
    # timestamp = f"{frame_index*20}ms"
    max_time = "5s"

    # With FAST SEEKING
    output = subprocess.run(
        [
            "ffmpeg",
            "-ss",
            "00:00:00.00",
            "-i",
            str(video_path),
            "-an",  # disable audio processing
            "-t",
            max_time,
            "-abort_on",
            "empty_output",
            str(out_path),  # output path
        ],
        capture_output=True,
        text=True,
    )
    # ffmpeg -accurate_seek -ss 0.00 -i "/net/holy-nfsisilon/ifs/rc_labs/olveczky_lab_tier1/Lab/dannce_rig2/data/M1-M7_photometry/Alone/Day2_wk2/240625_143814_M5/videos/Camera1/0.mp4" -frames:v 1 instance_data/tmp/out

    logging.warning(f"SUB OUT:{output.stdout}")

    logging.warning(f"SUB ERR:{output.stderr}")

    # logging.warning(f"SUB CODE:{output.returncode}")
    try:
        output.check_returncode()
    except subprocess.CalledProcessError:
        raise HTTPException(
            400, "FFMPEG frame extraction failed. Perhaps the frame number is invalid?"
        )
    # return {"path": str(out_path)}
    return FileResponse(out_path, status_code=200)


@router.get("/{id}")
def get_job_details(id: int, session: SessionDep) -> Any:
    row = session.execute(
        f"SELECT * FROM {TABLE_VIDEO_FOLDER} WHERE ID=?", (id,)
    ).fetchone()
    if not row:
        raise HTTPException(status_code=404)

    row_dict = dict(row)

    label_data = get_labeled_data_in_dir(id, row_dict["path"])

    row_dict["label_files"] = label_data

    row_dict["prediction_data"] = get_predicted_data_in_dir(id, row_dict["path"])

    row_predict_job = session.execute(
        f"""
SELECT
    *
FROM
    {TABLE_PREDICT_JOB} t1
LEFT JOIN
    {TABLE_SLURM_JOB} t2
ON t1.slurm_job = t2.slurm_job_id
WHERE video_folder=?""",
        (id,),
    ).fetchmany()
    row_predict_job = [dict(x) for x in row_predict_job]

    row_dict["predict_jobs"] = row_predict_job
    return row_dict
