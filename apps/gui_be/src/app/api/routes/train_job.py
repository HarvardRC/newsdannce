"""
/train_job
"""

from functools import reduce
from pathlib import Path
import sqlite3
import traceback
from typing import Any
from fastapi import APIRouter, HTTPException

from app.api.deps import SessionDep
from app.core import db
from app.core.db import (
    TABLE_GPU_JOB,
    TABLE_RUNTIME,
    TABLE_TRAIN_JOB,
    TABLE_TRAIN_JOB_VIDEO_FOLDER,
    TABLE_VIDEO_FOLDER,
    TABLE_WEIGHTS,
)
from app.models import TrainJobSubmitComModel, TrainJobSubmitDannceModel
from app.core.config import settings
from app.utils.make_io_yaml import config_com_train, config_dannce_train
from app.base_logger import logger
import taskqueue.submit_job


router = APIRouter()


@router.post("/submit_com")
def train_job_submit_com(conn: SessionDep, user_data: TrainJobSubmitComModel):
    """Submit a train job: this also creates train_job:video_folder relations"""

    config_model = config_com_train(conn, user_data)

    config_path = config_model.META_config_path
    log_path = config_model.META_log_path
    weights_path = config_model.META_weights_path

    curr = conn.cursor()
    curr.execute("BEGIN")
    try:
        # create weight table entry
        weights_name = user_data.output_model_name
        curr.execute(
            f"INSERT INTO {TABLE_WEIGHTS} (path, name, status, mode) VALUES (?, ?, 'PENDING', 'COM')",
            (weights_path, weights_name),
        )
        weights_id = curr.lastrowid

        # create gpu_job table entry
        curr.execute(f"INSERT INTO {TABLE_GPU_JOB} (log_path) VALUES (?)", (log_path,))
        gpu_job_id = curr.lastrowid

        curr.execute(
            f"INSERT INTO {TABLE_TRAIN_JOB} (name, weights, runtime, config, gpu_job) VALUES (?, ?, ?, ?, ?)",
            (
                user_data.name,
                weights_id,
                user_data.runtime_id,
                config_model.to_json_string(),
                gpu_job_id,
            ),
        )
        train_job_id = curr.lastrowid

        #  insert all table_train_job_video pairs
        sql_tuples = [(train_job_id, x) for x in user_data.video_folder_ids]
        curr.executemany(
            f"INSERT INTO {TABLE_TRAIN_JOB_VIDEO_FOLDER} (train_job, video_folder) VALUES (?, ?)",
            sql_tuples,
        )

        # save config file to intance file system
        config_path_internal = Path(settings.CONFIGS_FOLDER, config_path)
        with open(config_path_internal, "wt") as f:
            yaml_config = config_model.to_yaml_string()
            f.write(yaml_config)

        curr.execute("COMMIT")

    except sqlite3.Error as e:
        logger.info(f"ERROR: {e}")
        logger.info(f"ERROR: {traceback.format_exc()}")
        curr.execute("ROLLBACK")
        raise HTTPException(
            status_code=400,
            detail="SQLITE3 Error. Transaction rolled back. Perhaps there is already a model with modelname?",
        )

    taskqueue.submit_job.submit_train_job.delay(
        mode="COM",
        train_job_id=train_job_id,
        job_name=user_data.name,
        log_path=log_path,
        config_path=config_path,
        runtime_id=user_data.runtime_id,
        cwd_folder_external_str=str(config_model.META_cwd),
    )

    return {
        "train_job_id": train_job_id,
        "weights_id": weights_id,
        "gpu_job_id": gpu_job_id,
        "config_file_path": config_path,
        "message": "submitting train COM job to slurm in background",
    }


@router.post("/submit_dannce")
def train_job_submit_dannce(conn: SessionDep, user_data: TrainJobSubmitDannceModel):
    """Submit a train job: this also creates train_job:video_folder relations"""

    config_model = config_dannce_train(conn, user_data)

    config_path = config_model.META_config_path
    weights_path = config_model.META_weights_path
    log_path = config_model.META_log_path

    curr = conn.cursor()
    curr.execute("BEGIN")
    try:
        # create weights entry
        weights_name = user_data.output_model_name
        curr.execute(
            f"INSERT INTO {TABLE_WEIGHTS} (path, name, status, mode) VALUES (?, ?, 'PENDING', 'DANNCE')",
            (weights_path, weights_name),
        )
        weights_id = curr.lastrowid

        # create gpu_job entry
        curr.execute(f"INSERT INTO {TABLE_GPU_JOB} (log_path) VALUES (?)", (log_path,))
        gpu_job_id = curr.lastrowid

        curr.execute(
            f"INSERT INTO {TABLE_TRAIN_JOB} (name, weights, gpu_job, runtime, config) VALUES (?, ?, ?, ?, ?)",
            (
                user_data.name,
                weights_id,
                gpu_job_id,
                user_data.runtime_id,
                config_model.to_json_string(),
            ),
        )
        train_job_id = curr.lastrowid

        #  insert all table_train_job_video pairs
        sql_tuples = [(train_job_id, x) for x in user_data.video_folder_ids]
        curr.executemany(
            f"INSERT INTO {TABLE_TRAIN_JOB_VIDEO_FOLDER} (train_job, video_folder) VALUES (?, ?)",
            sql_tuples,
        )
        curr.execute("COMMIT")

        # save config file to intance file system
        config_path_internal = Path(settings.CONFIGS_FOLDER, config_path)
        with open(config_path_internal, "wt") as f:
            yaml_config = config_model.to_yaml_string()
            f.write(yaml_config)

    except sqlite3.Error as e:
        logger.info(f"ERROR: {e}")
        logger.info(f"ERROR: {traceback.format_exc()}")
        curr.execute("ROLLBACK")
        raise HTTPException(
            status_code=400,
            detail="SQLITE3 Error. Transaction rolled back. Perhaps there is already a model with modelname?",
        )

    taskqueue.submit_job.submit_train_job.delay(
        mode="DANNCE",
        train_job_id=train_job_id,
        job_name=user_data.name,
        log_path=log_path,
        config_path=config_path,
        runtime_id=user_data.runtime_id,
        cwd_folder_external_str=str(config_model.META_cwd),
    )

    return {
        "train_job_id": train_job_id,
        "weights_id": weights_id,
        "gpu_job_id": gpu_job_id,
        "config_file_path": config_path,
        "message": "submitting train COM job to slurm in background",
    }


@router.get("/list")
def list_all_train_jobs(conn: SessionDep):
    # return []
    rows = conn.execute(
        f"""
SELECT
    t1.id AS train_job_id,
    t1.name AS train_job_name,
    t1.created_at AS created_at,
    t1.weights AS weights_id,
    t1.gpu_job AS gpu_job_id,
    t1.runtime AS runtime_id,
    t2.name AS weights_name,
    t2.path AS weights_path,
    t2.mode AS mode,
    t3.slurm_status AS slurm_status,
    t3.local_status AS local_status,
    t3.slurm_job_id AS slurm_job_id,
    t3.local_process_id AS local_process_id,
    t3.log_path AS log_path,
    t4.name AS runtime_name,
    t4.runtime_type AS runtime_type
FROM {TABLE_TRAIN_JOB} t1
    LEFT JOIN {TABLE_WEIGHTS} t2
        ON t1.weights = t2.id
    LEFT JOIN {TABLE_GPU_JOB} t3
        ON t1.gpu_job = t3.id
    LEFT JOIN {TABLE_RUNTIME} t4
        ON t1.runtime = t4.id
"""
    ).fetchall()
    rows = [dict(x) for x in rows]

    for row in rows:
        row["log_path_external"] = Path(
            settings.JOB_LOGS_FOLDER_EXTERNAL, row["log_path"]
        )

    # for row in rows:
    #     if row["stdout_file"] is not None:
    #         row["stdout_file"] = row["stdout_file"].replace(
    #             "%j", str(row["slurm_job_id"])
    #         )
    return rows


@router.get("/{id}")
def get_job(
    conn: SessionDep,
    id: int,
) -> Any:
    row = conn.execute(
        f"""
SELECT
    t1.name,
    t1.config,
    t1.runtime AS runtime_id,
    t1.weights AS weights_id,
    t1.gpu_job AS gpu_job_id,
    t2.mode,
    t2.path AS weights_path,
    t2.name AS weights_name,
    t2.status AS weights_status,
    t3.name AS runtime_name,
    t3.runtime_type AS runtime_type,
    t4.local_status AS local_status,
    t4.slurm_status AS slurm_status,
    t4.local_process_id AS local_process_id,
    t4.slurm_job_id AS slurm_job_id,
    t4.log_path AS log_path
FROM
    {TABLE_TRAIN_JOB} t1
    LEFT JOIN {TABLE_WEIGHTS} t2
        ON t1.weights=t2.id
    LEFT JOIN {TABLE_RUNTIME} t3
        ON t1.runtime=t3.id
    LEFT JOIN {TABLE_GPU_JOB} t4
        ON t1.gpu_job=t4.id
WHERE
    t1.id=?""",
        (id,),
    ).fetchone()
    if not row:
        raise HTTPException(status_code=404)

    row = dict(row)

    # Get linked video folders
    rows = conn.execute(
        f"""
SELECT
    t3.path AS video_folder_path,
    t3.name AS video_folder_name,
    t3.id AS video_folder_id
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

    data = {
        "name": row["name"],
        "runtime_type": row["runtime_type"],
        "weights_id": row["weights_id"],
        "weights_path": row["weights_path"],
        "weights_status": row["weights_status"],
        "gpu_job_id": row["gpu_job_id"],
        "config": row["config"],
        "mode": row["mode"],
        "video_folders": video_folders,
        "runtime_id": row["runtime_id"],
        "runtime_name": row["runtime_name"],
        "slurm_job_id": row["slurm_job_id"],
        "slurm_status": row["slurm_status"],
        "local_process_id": row["local_process_id"],
        "local_status": row["local_status"],
        "log_path": row["log_path"],
        "log_path_external": Path(settings.JOB_LOGS_FOLDER_EXTERNAL, row["log_path"]),
    }
    return data
