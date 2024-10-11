from fastapi import APIRouter

from app.api.deps import SessionDep
from app.core.db import TABLE_PREDICTION

router = APIRouter()


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
