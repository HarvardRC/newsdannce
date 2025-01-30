"""Routes common to all job types (inc. train/predict)
/jobs_common
"""

# from typing import Any
from pathlib import Path
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from app.api.deps import SessionDep
from app.core.db import TABLE_GPU_JOB
from app.utils.job import refresh_job_list
from app.core.config import settings

router = APIRouter()


@router.post("/update_live_jobs")
def update_live_jobs(conn: SessionDep):
    data = refresh_job_list(conn)

    live_jobs = data.live_jobs
    jobs_updated = data.jobs_updated

    return {"live": live_jobs, "jobs_updated": jobs_updated}


@router.get("/get_log/{gpu_job_id}")
def get_job_log(conn: SessionDep, gpu_job_id: int, ):
    row = conn.execute(
        f"SELECT log_path FROM {TABLE_GPU_JOB} WHERE id = ?",
        (gpu_job_id,),
    ).fetchone()

    if not row:
        raise HTTPException(status_code=500)

    row = dict(row)
    log_path = row['log_path']
    p = Path(settings.JOB_LOGS_FOLDER, log_path)

    if not p.exists():
        raise HTTPException(
            status_code=400, detail=f"Log file is {p}, but file does not exist"
        )

    return FileResponse(p)
