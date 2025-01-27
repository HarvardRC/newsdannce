from pathlib import Path
import sqlite3
from typing import Any
import uuid
from fastapi import APIRouter, BackgroundTasks, HTTPException

from app.api.deps import SessionDep
from app.core.config import settings
from app.core.db import (
    TABLE_PREDICT_JOB,
    TABLE_PREDICTION,
    TABLE_RUNTIME,
    TABLE_SLURM_JOB,
    TABLE_VIDEO_FOLDER,
    TABLE_WEIGHTS,
)
from app.models import (
    PredictJobSubmitComModel,
    PredictJobSubmitDannceModel,
)
from app.utils.job import bg_submit_com_predict_job, bg_submit_dannce_predict_job
from app.utils.make_io_yaml import config_com_predict, config_dannce_predict

from app.base_logger import logger

router = APIRouter()


@router.post("/submit_com")
def predict_job_submit_com(
    session: SessionDep,
    data: PredictJobSubmitComModel,
    background_tasks: BackgroundTasks,
):
    # return {"message": "Thank u"}
    m = config_com_predict(session, data)

    # return {"config_com_pred": m}
    cfg_json = m.to_json_string()

    config_file = Path(
        settings.CONFIGS_FOLDER_EXTERNAL, f"predict_com_config_{uuid.uuid4().hex}.yaml"
    )

    """Submit a predict job"""
    curr = session.cursor()
    curr.execute("BEGIN")
    try:
        prediction_path = str(m.com_predict_dir)
        video_folder_id = data.video_folder_id
        prediction_name = data.prediction_name
        predict_job_name = data.name
        weights_id = data.weights_id
        runtime_id = data.runtime_id
        # weights_name = data.output_model_name
        curr.execute(
            f"INSERT INTO {TABLE_PREDICTION} (path, name, video_folder, status, mode) VALUES (?,?,?,?,?)",
            (prediction_path, prediction_name, video_folder_id, "PENDING", "COM"),
        )
        prediction_id = curr.lastrowid
        # first insert the train job
        curr.execute(
            f"INSERT INTO {TABLE_PREDICT_JOB} (name, weights, prediction, video_folder, runtime, config) VALUES (?,?,?,?,?,?)",
            (
                predict_job_name,
                weights_id,
                prediction_id,
                video_folder_id,
                runtime_id,
                cfg_json,
            ),
        )

        predict_job_id = curr.lastrowid
        curr.execute("COMMIT")

    except sqlite3.Error as e:
        logger.info(f"ERROR: {e}")
        curr.execute("ROLLBACK")
        raise HTTPException(
            status_code=400,
            detail="SQLITE3 Error. Transaction rolled back. Perhaps there is already a model with modelname?",
        )

    background_tasks.add_task(
        bg_submit_com_predict_job,
        m,
        runtime_id,
        predict_job_id,
        weights_id,
        prediction_id,
        config_file,
    )

    return {
        "predict_job_id": predict_job_id,
        "prediction_id": prediction_id,
        "config_file_path": config_file,
        "message": "submitting predict COM job to slurm in background",
    }


@router.post("/submit_dannce")
def predict_job_submit_dannce(
    session: SessionDep,
    data: PredictJobSubmitDannceModel,
    background_tasks: BackgroundTasks,
):
    # return {"message": "Thank u"}
    m = config_dannce_predict(session, data)

    # return {"config_com_pred": m}
    cfg_json = m.to_json_string()

    config_file = Path(
        settings.CONFIGS_FOLDER_EXTERNAL, f"predict_dannce_config_{uuid.uuid4().hex}.yaml"
    )

    """Submit a predict job"""
    curr = session.cursor()
    curr.execute("BEGIN")
    try:
        prediction_path = str(m.dannce_predict_dir)
        video_folder_id = data.video_folder_id
        prediction_name = data.prediction_name
        predict_job_name = data.name
        weights_id = data.weights_id
        runtime_id = data.runtime_id
        # weights_name = data.output_model_name
        curr.execute(
            f"INSERT INTO {TABLE_PREDICTION} (path, name, video_folder, status, mode) VALUES (?,?,?,?,?)",
            (prediction_path, prediction_name, video_folder_id, "PENDING", "DANNCE"),
        )
        prediction_id = curr.lastrowid
        # first insert the train job
        curr.execute(
            f"INSERT INTO {TABLE_PREDICT_JOB} (name, weights, prediction, video_folder, runtime, config) VALUES (?,?,?,?,?,?)",
            (
                predict_job_name,
                weights_id,
                prediction_id,
                video_folder_id,
                runtime_id,
                cfg_json,
            ),
        )

        predict_job_id = curr.lastrowid
        curr.execute("COMMIT")

    except sqlite3.Error as e:
        logger.info(f"ERROR: {e}")
        curr.execute("ROLLBACK")
        raise HTTPException(
            status_code=400,
            detail="SQLITE3 Error. Transaction rolled back. Perhaps there is already a model with modelname?",
        )

    background_tasks.add_task(
        bg_submit_dannce_predict_job,
        m,
        runtime_id,
        predict_job_id,
        weights_id,
        prediction_id,
        config_file,
    )

    return {
        "predict_job_id": predict_job_id,
        "prediction_id": prediction_id,
        "config_file_path": config_file,
        "message": "submitting predict COM job to slurm in background",
    }


@router.get("/list")
def list_all_predict_jobs(session: SessionDep):
    rows = session.execute(f"""
SELECT
    t1.id as predict_job_id,
    t1.name as predict_job_name,
    t1.created_at as created_at,
    t1.weights as weights_id,
    t1.slurm_job as slurm_job_id,
    t1.prediction as prediction_id,
    t1.video_folder as video_folder_id,
    t1.runtime as runtime_id,
    t2.name as weights_name,
    t2.mode as mode,
    t3.status as status,
    t3.stdout_file as stdout_file,
    t4.name as video_folder_name,
    t5.name as prediction_name
FROM {TABLE_PREDICT_JOB} t1
    LEFT JOIN {TABLE_WEIGHTS} t2
        ON t1.weights=t2.id
    LEFT JOIN {TABLE_SLURM_JOB} t3
        ON t1.slurm_job=t3.slurm_job_id
    LEFT JOIN {TABLE_VIDEO_FOLDER} t4
        ON t1.video_folder=t4.id
    LEFT JOIN {TABLE_PREDICTION} t5
        ON t1.prediction=t5.id
""").fetchall()
    rows = [dict(x) for x in rows]
    for row in rows:
        if row["stdout_file"] is not None:
            row["stdout_file"] = row["stdout_file"].replace(
                "%j", str(row["slurm_job_id"])
            )
    return rows


@router.get("/{id}")
def get_predict_job(id: int, session: SessionDep) -> Any:
    # row = None
    # if not row:
    #     raise HTTPException(status_code=404)

    row = session.execute(
        f"""
SELECT
    t1.name,
    t1.config,
    t1.runtime as runtime_id,
    t1.weights as weights_id,
    t1.slurm_job as slurm_job_id,
    t1.prediction as prediction_id,
    t1.video_folder as video_folder_id,
    t2.mode,
    t2.path as weights_path,
    t2.name as weights_name,
    t2.status as weights_status,
    t3.name as runtime_name,
    t4.status as slurm_job_status,
    t4.stdout_file as stdout_file,
    t5.status as prediction_status,
    t5.path as prediction_path,
    t6.name as video_folder_name,
    t6.path as video_folder_path
FROM
    {TABLE_PREDICT_JOB} t1
    LEFT JOIN {TABLE_WEIGHTS} t2
        ON t1.weights=t2.id
    LEFT JOIN {TABLE_RUNTIME} t3
        ON t1.runtime=t3.id
    LEFT JOIN {TABLE_SLURM_JOB} t4
        ON t1.slurm_job=t4.slurm_job_id
    LEFT JOIN {TABLE_PREDICTION} t5
        ON t1.prediction = t5.id
    LEFT JOIN {TABLE_VIDEO_FOLDER} t6
        ON t1.video_folder = t6.id
WHERE
    t1.id=?""",
        (id,),
    ).fetchone()
    if not row:
        raise HTTPException(status_code=404)

    row = dict(row)

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
        "runtime_id": row["runtime_id"],
        "runtime_name": row["runtime_name"],
        "slurm_job_id": row["slurm_job_id"],
        "slurm_job_status": row["slurm_job_status"],
        "stdout_file": stdout_file,
        "prediction_id": row["prediction_id"],
        "prediction_path": row["prediction_path"],
        "video_folder_id": row["video_folder_id"],
        "video_folder_path": row["video_folder_path"],
        "video_folder_name": row["video_folder_name"],
    }
    return data
