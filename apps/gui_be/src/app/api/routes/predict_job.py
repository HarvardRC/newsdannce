"""
/predict_job
"""

from pathlib import Path
import sqlite3
from typing import Any
from fastapi import APIRouter, BackgroundTasks, HTTPException

from app.api.deps import SessionDep
from app.core.config import settings
from app.core.db import (
    TABLE_GPU_JOB,
    TABLE_PREDICT_JOB,
    TABLE_PREDICTION,
    TABLE_RUNTIME,
    TABLE_VIDEO_FOLDER,
    TABLE_WEIGHTS,
)
from app.models import (
    PredictJobSubmitComModel,
    PredictJobSubmitDannceModel,
)
from app.utils.make_io_yaml import config_com_predict, config_dannce_predict

from app.base_logger import logger
from app.utils.helpers import make_resource_name

import taskqueue.submit_job


router = APIRouter()


@router.post("/submit_com")
def predict_job_submit_com(conn: SessionDep, user_data: PredictJobSubmitComModel):
    """Submit a predict job"""

    config_model = config_com_predict(conn, user_data)

    config_path = config_model.META_config_path
    log_path = config_model.META_log_path
    prediction_path = config_model.META_prediction_path

    curr = conn.cursor()
    curr.execute("BEGIN")
    try:
        # create prediction table entry
        prediction_path = prediction_path

        # weights_name = data.output_model_name
        curr.execute(
            f"INSERT INTO {TABLE_PREDICTION} (path, name, video_folder, status, mode) VALUES (?, ?, ?, 'PENDING', 'COM')",
            (prediction_path, user_data.prediction_name, user_data.video_folder_id),
        )
        prediction_id = curr.lastrowid

        # create gpu_job table entry
        curr.execute(f"INSERT INTO {TABLE_GPU_JOB} (log_path) VALUES (?)", (log_path,))
        gpu_job_id = curr.lastrowid

        # first insert the train job
        curr.execute(
            f"""
            INSERT INTO {TABLE_PREDICT_JOB}
            (   name,
                weights,
                prediction,
                video_folder,
                runtime,
                config,
                gpu_job
            ) VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                user_data.name,
                user_data.weights_id,
                prediction_id,
                user_data.video_folder_id,
                user_data.runtime_id,
                config_model.to_json_string(),
                gpu_job_id,
            ),
        )

        predict_job_id = curr.lastrowid

        # save config file to intance file system
        config_path_internal = Path(settings.CONFIGS_FOLDER, config_path)
        with open(config_path_internal, "wt") as f:
            yaml_config = config_model.to_yaml_string()
            f.write(yaml_config)

        curr.execute("COMMIT")

    except sqlite3.Error as e:
        logger.info(f"ERROR: {e}")
        curr.execute("ROLLBACK")
        raise HTTPException(
            status_code=400,
            detail="SQLITE3 Error. Transaction rolled back. Perhaps there is already a model with modelname?",
        )

    taskqueue.submit_job.submit_predict_job.delay(
        mode="COM",
        predict_job_id=predict_job_id,
        job_name=user_data.name,
        log_path=log_path,
        config_path=config_path,
        runtime_id=user_data.runtime_id,
        cwd_folder_external_str=str(config_model.META_cwd),
    )

    return {
        "predict_job_id": predict_job_id,
        "prediction_id": prediction_id,
        "config_file_path": config_path,
        "message": "submitting predict COM job to slurm in background",
    }


@router.post("/submit_com")
def predict_job_submit_dannce(conn: SessionDep, user_data: PredictJobSubmitDannceModel):
    """Submit a predict job"""

    config_model = config_com_predict(conn, user_data)

    config_path = config_model.META_config_path
    log_path = config_model.META_log_path
    prediction_path = config_model.META_prediction_path

    curr = conn.cursor()
    curr.execute("BEGIN")
    try:
        # create prediction table entry
        prediction_path = prediction_path

        # weights_name = data.output_model_name
        curr.execute(
            f"INSERT INTO {TABLE_PREDICTION} (path, name, video_folder, status, mode) VALUES (?, ?, ?, 'PENDING', 'DANNCE')",
            (prediction_path, user_data.prediction_name, user_data.video_folder_id),
        )
        prediction_id = curr.lastrowid

        # create gpu_job table entry
        curr.execute(f"INSERT INTO {TABLE_GPU_JOB} (log_path) VALUES (?)", (log_path,))
        gpu_job_id = curr.lastrowid

        # first insert the train job
        curr.execute(
            f"""
            INSERT INTO {TABLE_PREDICT_JOB}
            (   name,
                weights,
                prediction,
                video_folder,
                runtime,
                config,
                gpu_job
            ) VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                user_data.name,
                user_data.weights_id,
                prediction_id,
                user_data.video_folder_id,
                user_data.runtime_id,
                config_model.to_json_string(),
                gpu_job_id,
            ),
        )

        predict_job_id = curr.lastrowid

        # save config file to intance file system
        config_path_internal = Path(settings.CONFIGS_FOLDER, config_path)
        with open(config_path_internal, "wt") as f:
            yaml_config = config_model.to_yaml_string()
            f.write(yaml_config)

        curr.execute("COMMIT")

    except sqlite3.Error as e:
        logger.info(f"ERROR: {e}")
        curr.execute("ROLLBACK")
        raise HTTPException(
            status_code=400,
            detail="SQLITE3 Error. Transaction rolled back. Perhaps there is already a model with modelname?",
        )

    taskqueue.submit_job.submit_predict_job.delay(
        mode="DANNCE",
        predict_job_id=predict_job_id,
        job_name=user_data.name,
        log_path=log_path,
        config_path=config_path,
        runtime_id=user_data.runtime_id,
        cwd_folder_external_str=str(config_model.META_cwd),
    )

    return {
        "predict_job_id": predict_job_id,
        "prediction_id": prediction_id,
        "config_file_path": config_path,
        "message": "submitting predict DANNCE job to slurm in background",
    }


# @router.post("/submit_dannce")
# def predict_job_submit_dannce(
#     conn: SessionDep,
#     data: PredictJobSubmitDannceModel,
#     background_tasks: BackgroundTasks,
# ):
#     """Submit a predict job"""

#     m = config_dannce_predict(conn, data)

#     cfg_json = m.to_json_string()

#     config_file = Path(
#         settings.CONFIGS_FOLDER_EXTERNAL,
#         make_resource_name("predict_dannce_config_", ".yaml"),
#     )

#     curr = conn.cursor()
#     curr.execute("BEGIN")
#     try:
#         prediction_path = str(m.dannce_predict_dir)
#         video_folder_id = data.video_folder_id
#         prediction_name = data.prediction_name
#         predict_job_name = data.name
#         weights_id = data.weights_id
#         runtime_id = data.runtime_id
#         # weights_name = data.output_model_name
#         curr.execute(
#             f"INSERT INTO {TABLE_PREDICTION} (path, name, video_folder, status, mode) VALUES (?,?,?,?,?)",
#             (prediction_path, prediction_name, video_folder_id, "PENDING", "DANNCE"),
#         )
#         prediction_id = curr.lastrowid
#         # first insert the train job
#         curr.execute(
#             f"INSERT INTO {TABLE_PREDICT_JOB} (name, weights, prediction, video_folder, runtime, config) VALUES (?,?,?,?,?,?)",
#             (
#                 predict_job_name,
#                 weights_id,
#                 prediction_id,
#                 video_folder_id,
#                 runtime_id,
#                 cfg_json,
#             ),
#         )

#         predict_job_id = curr.lastrowid
#         curr.execute("COMMIT")

#     except sqlite3.Error as e:
#         logger.info(f"ERROR: {e}")
#         curr.execute("ROLLBACK")
#         raise HTTPException(
#             status_code=400,
#             detail="SQLITE3 Error. Transaction rolled back. Perhaps there is already a model with modelname?",
#         )

#     background_tasks.add_task(
#         bg_submit_dannce_predict_job,
#         m,
#         runtime_id,
#         predict_job_id,
#         weights_id,
#         prediction_id,
#         config_file,
#     )

#     return {
#         "predict_job_id": predict_job_id,
#         "prediction_id": prediction_id,
#         "config_file_path": config_file,
#         "message": "submitting predict COM job to slurm in background",
#     }


@router.get("/list")
def list_all_predict_jobs(conn: SessionDep):
    rows = conn.execute(f"""
SELECT
    t1.id AS predict_job_id,
    t1.name AS predict_job_name,
    t1.created_at AS created_at,
    t1.weights AS weights_id,
    t1.gpu_job AS gpu_job_id,
    t1.prediction AS prediction_id,
    t1.video_folder AS video_folder_id,
    t1.runtime AS runtime_id,
    t2.name AS weights_name,
    t2.mode AS mode,
    t3.local_status AS local_status,
    t3.slurm_status AS slurm_status,
    t3.log_path AS log_path,
    t4.name AS video_folder_name,
    t5.name AS prediction_name,
    t6.name AS runtime_name,
    t6.runtime_type AS runtime_type
FROM {TABLE_PREDICT_JOB} t1
    LEFT JOIN {TABLE_WEIGHTS} t2
        ON t1.weights = t2.id
    LEFT JOIN {TABLE_GPU_JOB} t3
        ON t1.gpu_job = t3.id
    LEFT JOIN {TABLE_VIDEO_FOLDER} t4
        ON t1.video_folder = t4.id
    LEFT JOIN {TABLE_PREDICTION} t5
        ON t1.prediction = t5.id
    LEFT JOIN {TABLE_RUNTIME} t6
        ON t1.runtime = t6.id
""").fetchall()
    rows = [dict(x) for x in rows]
    for row in rows:
        if row["stdout_file"] is not None:
            row["stdout_file"] = row["stdout_file"].replace(
                "%j", str(row["slurm_job_id"])
            )
        row["status"] = (
            row["slurm_status"] if row["job_type"] == "SLURM" else row["local_status"]
        )
    return rows


@router.get("/{id}")
def get_predict_job(
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
    t1.id AS gpu_job_id,
    t1.prediction AS prediction_id,
    t1.video_folder AS video_folder_id,
    t2.mode,
    t2.path AS weights_path,
    t2.name AS weights_name,
    t2.status AS weights_status,
    t3.name AS runtime_name,
    t3.runtime_type AS runtime_type,
    t4.slurm_status AS slurm_status,
    t4.local_status AS local_status,
    t4.slurm_job_id AS slurm_job_id,
    t4.local_process_id AS local_process_id,
    t4.log_path AS log_path,
    t5.status AS prediction_status,
    t5.path AS prediction_path,
    t6.name AS video_folder_name,
    t6.path AS video_folder_path
FROM
    {TABLE_PREDICT_JOB} t1
    LEFT JOIN {TABLE_WEIGHTS} t2
        ON t1.weights = t2.id
    LEFT JOIN {TABLE_RUNTIME} t3
        ON t1.runtime = t3.id
    LEFT JOIN {TABLE_GPU_JOB} t4
        ON t1.gpu_job_id = t4.id
    LEFT JOIN {TABLE_PREDICTION} t5
        ON t1.prediction = t5.id
    LEFT JOIN {TABLE_VIDEO_FOLDER} t6
        ON t1.video_folder = t6.id
WHERE
    t1.id = ?
""",
        (id,),
    ).fetchone()
    if not row:
        raise HTTPException(status_code=404)

    row = dict(row)

    data = {
        "name": row["name"],
        "weights_id": row["weights_id"],
        "weights_path": row["weights_path"],
        "weights_status": row["weights_status"],
        "gpu_job_id": row["gpu_job_id"],
        "config": row["config"],
        "mode": row["mode"],
        "runtime_id": row["runtime_id"],
        "runtime_name": row["runtime_name"],
        "slurm_job_id": row["slurm_job_id"],
        "slurm_job_status": row["slurm_job_status"],
        "local_job_status": row["local_job_status"],
        "stdout_file": row["log_path"],
        "prediction_id": row["prediction_id"],
        "prediction_path": row["prediction_path"],
        "video_folder_id": row["video_folder_id"],
        "video_folder_path": row["video_folder_path"],
        "video_folder_name": row["video_folder_name"],
        "runtime_type": row["runtime_type"],
    }
    return data
