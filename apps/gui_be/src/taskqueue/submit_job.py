from dataclasses import dataclass
from pathlib import Path
import re
import subprocess
import shutil
from typing import Literal
from app.core import db
from app.utils import make_sbatch
from app.utils.helpers import make_resource_name
from app.utils.make_io_yaml import ComTrainModel
from app.utils.video_folders import process_label_mat_file
from app.core.config import settings
from caldannce.calibration_data import CameraParams
import json
import time

import logging as logger

from app.utils.dannce_mat_processing import MatFileInfo
from app.core.db import (
    TABLE_GPU_JOB,
    TABLE_PREDICTION,
    TABLE_RUNTIME,
    TABLE_TRAIN_JOB,
    TABLE_VIDEO_FOLDER,
    TABLE_WEIGHTS,
    get_db_context,
)
from app.models import RuntimeData
from app.utils.video_processing import get_video_metadata

# from taskqueue.celery import celery_app
from taskqueue.celery import celery_app

logger.basicConfig(level=logger.INFO)


@celery_app.task
def submit_train_job(
    train_job_id: int,
    runtime_id: int,
    job_name: str,
    log_path: str,
    config_path: str,
    cwd_folder_external_str: Path,
):
    logger.warning("BACKGROUND TASK RUNNING")
    # 1. load context needed to submit job
    with get_db_context() as conn:
        curr = conn.cursor()
        row = curr.execute(
            f"SELECT id, memory_gb, partition_list, time_hrs, n_cpus, name, runtime_type FROM {TABLE_RUNTIME} WHERE id = ?",
            (runtime_id,),
).fetchone()
        runtime_data = RuntimeData(
            id=row["id"],
            memory_gb=row["memory_gb"],
            partition_list=row["partition_list"],
            time_hrs=row["time_hrs"],
            n_cpus=row["n_cpus"],
            runtime_type=row["runtime_type"],
            name=row["name"],
        )
        job_log_path_external = Path(settings.JOB_LOGS_FOLDER_EXTERNAL, log_path)
        config_path_external = Path(settings.CONFIGS_FOLDER_EXTERNAL, config_path)

        sbatch_str = make_sbatch.make_sbatch_str(
            config_path_external=config_path_external,
            sdannce_command=db.JobCommand.TRAIN_COM,
            cwd_folder_external=Path(cwd_folder_external_str),
            job_name=job_name,
            log_file_external=job_log_path_external,
            runtime_data=runtime_data,
        )

        with open(Path(settings.LOGS_FOLDER, f"{config_path}.sbatch"), "wt") as f:
            f.write(sbatch_str)


        # FAKE SUBMIT JOB: TODO: REMOVE
        time.sleep(10)
        slurm_job_id = 12345

        # update jobs row to reflect job has been submitted
        curr.execute(
            f"UPDATE {TABLE_GPU_JOB} SET slurm_job_id = ?, slurm_status = 'PENDING' WHERE id = ?",
            (slurm_job_id, train_job_id),
        )
        conn.execute("COMMIT")

    return {"slurm_job_id": slurm_job_id}


@celery_app.task
def submit_local_train_com():
    pass


# @celery_app.task
# def run_gpu_job_local(video_folder_path: str | Path, camnames: list[str]):
