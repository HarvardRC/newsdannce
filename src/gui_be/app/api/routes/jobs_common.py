"""Routes common to all job types (inc. train/predict)"""

# from typing import Any
from pathlib import Path
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from app.api.deps import SessionDep
from app.core.db import TABLE_SLURM_JOB
from app.utils.job import get_nonfinal_job_ids, update_jobs_by_ids
from app.utils.metadata import get_last_jobs_refresh


router = APIRouter()


@router.post("/update-live-jobs")
def update_live_jobs(conn: SessionDep):
    live_jobs = get_nonfinal_job_ids(conn)
    jobs_updated = update_jobs_by_ids(conn=conn, job_list=live_jobs)

    return {"live": live_jobs, "jobs_updated": jobs_updated}


@router.get("/refresh-timestamp")
def get_last_jobs_refresh_route(conn: SessionDep):
    """Update all jobs which are not in a final state (e.g. FAILED, COMPLETED, etc.)"""
    last_update_timestamp = get_last_jobs_refresh(conn)
    return last_update_timestamp


@router.get("/get_log/{slurm_job_id}")
def get_job_log(slurm_job_id: int, conn: SessionDep):
    # slurm_job_id_int = int(slurm_job_id)
    row = conn.execute(
        f"SELECT stdout_file FROM {TABLE_SLURM_JOB} WHERE slurm_job_id=?",
        (slurm_job_id,),
    ).fetchone()

    if not row:
        raise HTTPException(status_code=404)

    stdout_file = row["stdout_file"]
    stdout_file = stdout_file.replace("%j", str(slurm_job_id))
    p = Path(stdout_file)
    if not p.exists():
        raise HTTPException(
            status_code=400, detail=f"Stdout file is {stdout_file} but unable to access"
        )
    return FileResponse(p)
