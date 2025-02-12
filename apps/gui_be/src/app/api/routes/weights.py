"""
/weights
"""

from pathlib import Path
from fastapi import APIRouter, HTTPException
from app.core.config import settings
from app.api.deps import SessionDep
from app.core.db import TABLE_WEIGHTS
from app.utils.weights import get_latest_checkpoint_filename

router = APIRouter()


@router.get("/list")
def list_all_weights(conn: SessionDep):
    rows = conn.execute(f"SELECT * FROM {TABLE_WEIGHTS}").fetchall()
    rows = [dict(x) for x in rows]
    return rows


@router.get("/{id}")
def get_weights_details_route(conn: SessionDep, id: str):
    id_int = int(id)
    row = conn.execute(
        f"""
SELECT
    name AS weights_name,
    path AS weights_path,
    status AS status,
    filename AS filename,
    mode AS mode,
    created_at
FROM {TABLE_WEIGHTS}
WHERE id=?
""",
        (id_int,),
    ).fetchone()
    if not row:
        raise HTTPException(404)

    row = dict(row)
    weights_name = row["weights_name"]
    weights_path = row["weights_path"]
    status = row["status"]
    mode = row["mode"]
    created_at = row["created_at"]

    if status == 'COMPLETED':
        weights_filename = get_latest_checkpoint_filename(weights_path)
        path_external = Path(settings.WEIGHTS_FOLDER_EXTERNAL, weights_path, weights_filename)
        path_internal = Path(settings.WEIGHTS_FOLDER, weights_path, weights_filename),
    else:
        weights_filename = None
        path_external = None
        path_internal = None

    return {
        "weights_path": row["weights_path"],
        "path_external": Path(
            settings.WEIGHTS_FOLDER_EXTERNAL, weights_path, weights_filename
        ),
        "path_internal": path_internal,
        "weights_name": weights_name,
        "status": status,
        "mode": mode,
        "created_at": created_at,
        "filename": row["filename"],
    }
