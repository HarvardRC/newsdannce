from functools import reduce
from pathlib import Path
import sqlite3
from typing import Any
from fastapi import APIRouter, BackgroundTasks, HTTPException
import uuid


from app.api.deps import SessionDep
from app.core.db import (
    TABLE_RUNTIME,
    TABLE_SLURM_JOB,
    TABLE_TRAIN_JOB,
    TABLE_TRAIN_JOB_VIDEO_FOLDER,
    TABLE_VIDEO_FOLDER,
    TABLE_WEIGHTS,
)
from app.models import TrainJobSubmitComModel, TrainJobSubmitDannceModel
from app.utils.job import (
    bg_submit_com_train_job,
    bg_submit_dannce_train_job,
)
from app.core.config import settings
from app.utils.make_io_yaml import config_com_train, config_dannce_train

router = APIRouter()


@router.post("/submit_com")
def train_job_submit_com(
    session: SessionDep, data: TrainJobSubmitComModel, background_tasks: BackgroundTasks
):
    m = config_com_train(session, data)

    cfg_json = m.to_json_string()

    config_file = Path(
        settings.CONFIGS_FOLDER, f"train_com_config_{uuid.uuid4().hex}.yaml"
    )

    """Submit a train job: this also creates train_job:video_folder relations"""
    curr = session.cursor()
    curr.execute("BEGIN")
    try:
        weights_path = str(m.com_train_dir)
        weights_name = data.output_model_name
        curr.execute(
            f"INSERT INTO {TABLE_WEIGHTS} (path, name, status, mode) VALUES (?,?,?,?)",
            (weights_path, weights_name, "PENDING", "COM"),
        )
        weights_id = curr.lastrowid
        # first insert the train job
        curr.execute(
            f"INSERT INTO {TABLE_TRAIN_JOB} (name, weights, runtime, config) VALUES (?,?,?,?)",
            (data.name, weights_id, data.runtime_id, cfg_json),
        )

        train_job_id = curr.lastrowid
        sql_tuples = [(train_job_id, x) for x in data.video_folder_ids]
        #  insert all table_train_job_video pairs
        curr.executemany(
            f"INSERT INTO {TABLE_TRAIN_JOB_VIDEO_FOLDER} (train_job, video_folder) VALUES (?,?)",
            sql_tuples,
        )
        curr.execute("COMMIT")

    except sqlite3.Error as e:
        print("ERROR: ", e)
        curr.execute("ROLLBACK")
        raise HTTPException(
            status_code=400,
            detail="SQLITE3 Error. Transaction rolled back. Perhaps there is already a model with modelname?",
        )

    background_tasks.add_task(
        bg_submit_com_train_job,
        m,
        data.runtime_id,
        train_job_id,
        weights_id,
        config_file,
    )

    return {
        "train_job_id": train_job_id,
        "weights_id": weights_id,
        "config_file_path": config_file,
        "message": "submitting train COM job to slurm in background",
    }


@router.post("/submit_dannce")
def train_job_submit_dannce(
    session: SessionDep,
    data: TrainJobSubmitDannceModel,
    background_tasks: BackgroundTasks,
):
    m = config_dannce_train(session, data)

    cfg_json = m.to_json_string()

    config_file = Path(
        settings.CONFIGS_FOLDER, f"train_dannce_config_{uuid.uuid4().hex}.yaml"
    )

    """Submit a train job: this also creates train_job:video_folder relations"""
    curr = session.cursor()
    curr.execute("BEGIN")
    try:
        weights_path = str(m.dannce_train_dir)
        weights_name = data.output_model_name
        curr.execute(
            f"INSERT INTO {TABLE_WEIGHTS} (path, name, status, mode) VALUES (?,?,?,?)",
            (weights_path, weights_name, "PENDING", "DANNCE"),
        )
        weights_id = curr.lastrowid
        # first insert the train job
        curr.execute(
            f"INSERT INTO {TABLE_TRAIN_JOB} (name, weights, runtime, config) VALUES (?,?,?,?)",
            (data.name, weights_id, data.runtime_id, cfg_json),
        )

        train_job_id = curr.lastrowid
        sql_tuples = [(train_job_id, x) for x in data.video_folder_ids]
        #  insert all table_train_job_video pairs
        curr.executemany(
            f"INSERT INTO {TABLE_TRAIN_JOB_VIDEO_FOLDER} (train_job, video_folder) VALUES (?,?)",
            sql_tuples,
        )
        curr.execute("COMMIT")

    except sqlite3.Error as e:
        print("ERROR: ", e)
        curr.execute("ROLLBACK")
        raise HTTPException(
            status_code=400,
            detail="SQLITE3 Error. Transaction rolled back. Perhaps there is already a model with modelname?",
        )

    background_tasks.add_task(
        bg_submit_dannce_train_job,
        m,
        data.runtime_id,
        train_job_id,
        weights_id,
        config_file,
    )

    return {
        "train_job_id": train_job_id,
        "weights_id": weights_id,
        "config_file_path": config_file,
        "message": "submitting train DANNCE job to slurm in background",
    }


@router.get("/list")
def list_all_train_jobs(session: SessionDep):
    rows = session.execute(f"""
SELECT
    t1.id as train_job_id,
    t1.name as train_job_name,
    t1.created_at as created_at,
    t1.weights as weights_id,
    t1.slurm_job as slurm_job_id,
    t1.runtime as runtime_id,
    t2.name as weights_name,
    t2.path as weights_path,
    t2.mode as mode,
    t3.status as status,
    t3.stdout_file as stdout_file
FROM {TABLE_TRAIN_JOB} t1
    LEFT JOIN {TABLE_WEIGHTS} t2
        ON t1.weights=t2.id
    LEFT JOIN {TABLE_SLURM_JOB} t3
        ON t1.slurm_job=t3.slurm_job_id """).fetchall()
    rows = [dict(x) for x in rows]

    for row in rows:
        if row["stdout_file"] is not None:
            row["stdout_file"] = row["stdout_file"].replace(
                "%j", str(row["slurm_job_id"])
            )
    return rows


@router.get("/{id}")
def get_job(id: int, session: SessionDep) -> Any:
    row = session.execute(
        f"""
SELECT
    t1.name,
    t1.config,
    t1.runtime as runtime_id,
    t1.weights as weights_id,
    t1.slurm_job as slurm_job_id,
    t2.mode,
    t2.path as weights_path,
    t2.name as weights_name,
    t2.status as weights_status,
    t3.name as runtime_name,
    t4.status as slurm_job_status,
    t4.stdout_file as stdout_file
FROM
    {TABLE_TRAIN_JOB} t1
    LEFT JOIN {TABLE_WEIGHTS} t2
        ON t1.weights=t2.id
    LEFT JOIN {TABLE_RUNTIME} t3
        ON t1.runtime=t3.id
    LEFT JOIN {TABLE_SLURM_JOB} t4
        ON t1.slurm_job=t4.slurm_job_id
WHERE
    t1.id=?""",
        (id,),
    ).fetchone()
    if not row:
        raise HTTPException(status_code=404)

    row = dict(row)

    # Get linked video folders
    rows = session.execute(
        f"""
SELECT
    t3.path as video_folder_path,
    t3.name as video_folder_name,
    t3.id as video_folder_id
FROM
    {TABLE_TRAIN_JOB} t1
    LEFT JOIN {TABLE_TRAIN_JOB_VIDEO_FOLDER} t2
        ON t1.id = t2.train_job
    LEFT JOIN {TABLE_VIDEO_FOLDER} t3
        ON t2.video_folder = t3.id
WHERE t1.id=?;
""",
        (id,),
    ).fetchall()

    rows = [dict(x) for x in rows]

    def reduce_video_folders(acc: list, cur):
        acc.append(
            {
                "id": cur["video_folder_id"],
                "name": cur["video_folder_name"],
                "path": cur["video_folder_path"],
            }
        )
        return acc

    video_folders = reduce(reduce_video_folders, rows, [])

    if row["stdout_file"]:
        stdout_file = row["stdout_file"].replace("%j", str(row["slurm_job_id"]))
    else:
        stdout_file = None

    data = {
        "name": row["name"],
        "weights_id": row["weights_id"],
        "weights_path": row["weights_path"],
        "weights_status": row["weights_status"],
        "config": row["config"],
        "mode": row["mode"],
        "video_folders": video_folders,
        "runtime_id": row["runtime_id"],
        "runtime_name": row["runtime_name"],
        "slurm_job_id": row["slurm_job_id"],
        "slurm_job_status": row["slurm_job_status"],
        "stdout_file": stdout_file,
    }
    return data
