# from sqlite3 import Connection
# from typing import Any, Annotated
from typing import Any
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import FileResponse
from app.api.deps import SessionDep
from app.core.db import (
    TABLE_PREDICT_JOB,
    TABLE_SLURM_JOB,
    TABLE_VIDEO_FOLDER,
)
from app.models import CreateVideoFolderModel

from app.utils.dannce_mat_processing import (
    get_labeled_data_in_dir,
    get_predicted_data_in_dir,
)


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


@router.get("/{id}/video")
async def stream_video(id: int, session: SessionDep, request: Request) -> Any:
    row = session.execute(
        f"SELECT path FROM {TABLE_VIDEO_FOLDER} WHERE ID=?", (id,)
    ).fetchone()
    if not row:
        raise HTTPException(status_code=404)

    # video_path = Path(row["path"], "videos", "Camera1", "0.mp4")

    video_path = "/n/olveczky_lab_tier1/Lab/dannce_rig2/data/M1-M7_photometry/Alone/Day1_wk2/240624_135840_M4/stats_com_predict.log"

    #
    # return HTTPResponse
    return FileResponse(path=video_path)


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
