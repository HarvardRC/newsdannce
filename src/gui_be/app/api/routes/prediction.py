from fastapi import APIRouter, HTTPException
from pathlib import Path

from app.api.deps import SessionDep
from app.core.db import TABLE_PREDICTION, TABLE_VIDEO_FOLDER
from app.models import MakePredictionPreviewModel
from app.utils.video import get_one_frame
from app.core.config import settings

router = APIRouter()


@router.post("/{id_str}/make_preview")
def make_preview_route(
    session: SessionDep, data: MakePredictionPreviewModel, id_str: str
):
    if len(data.frames) > 10 or len(data.frames) < 1:
        raise HTTPException(400, "Can fetch between 1-10 frames for preview")
    id = int(id_str)
    row = session.execute(
        f"""
SELECT
    t1.path AS prediction_path,
    t1.video_folder AS video_folder_id,
    t2.path AS video_folder_path
FROM {TABLE_PREDICTION} t1
    LEFT JOIN {TABLE_VIDEO_FOLDER} t2
        ON t1.video_folder = t2.id
WHERE t1.id=?
""",
        (id,),
    ).fetchone()
    row = dict(row)

    prediction_path = row["prediction_path"]
    video_folder_id = row["video_folder_id"]
    video_folder_path = row["video_folder_path"]

    frame_info = {}

    for f in data.frames:
        frame_image_file = get_one_frame(
            Path(video_folder_path, "videos", data.camera_name, "0.mp4"), f
        )
        frame_info[f] = {
            "name": frame_image_file,
            "static_url": f"{settings.STATIC_URL}/{frame_image_file}",
        }
    return frame_info
    # return {
    #     "prediction_path": row["prediction_path"],
    #     "video_folder_id": row["video_folder_id"],
    #     "video_folder_path": row["video_folder_path"],
    # }


@router.get("/list")
def list_all_predictions(session: SessionDep):
    rows = session.execute(
        f"""
SELECT
    id as prediction_id,
    name as prediction_name,
    path as prediction_path,
    status,
    video_folder as video_folder_id,
    mode,
    created_at
FROM {TABLE_PREDICTION}"""
    ).fetchall()
    rows = [dict(x) for x in rows]
    return rows


@router.get("/{id}")
def get_prediction_details_route(id: str, session: SessionDep):
    id_int = int(id)
    row = session.execute(
        f"""
SELECT
    id AS prediction_id,
    name AS prediction_name,
    path AS prediction_path,
    status AS prediction_status,
    video_folder AS video_folder_id,
    mode AS mode,
    created_at
FROM {TABLE_PREDICTION}
WHERE id=?
""",
        (id_int,),
    ).fetchone()
    if not row:
        raise HTTPException(404)
    row = dict(row)
    return row
