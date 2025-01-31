from pathlib import Path
import re
import subprocess
from typing import Literal
from app.core import db
from app.utils import make_sbatch
from app.utils.job import SLURM_TIMEOUT_SECONDS
from app.core.config import settings

import logging as logger

from app.core.db import TABLE_GPU_JOB, TABLE_RUNTIME, get_db_context
from app.models import RuntimeData

from taskqueue.celery import celery_app

logger.basicConfig(level=logger.INFO)


@celery_app.task
def submit_train_job(
    mode: Literal["COM", "DANNCE"],
    gpu_job_id: int,
    train_job_id: int,
    runtime_id: int,
    job_name: str,
    log_path: str,
    config_path: str,
    cwd_folder_external_str: Path,
):
    if mode == "COM":
        sdannce_command = db.JobCommand.TRAIN_COM
    elif mode == "DANNCE":
        sdannce_command = db.JobCommand.TRAIN_DANNCE
    else:
        raise Exception("INVALID SDANNCE COMMAND")

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
            sdannce_command=sdannce_command,
            cwd_folder_external=Path(cwd_folder_external_str),
            job_name=job_name,
            log_file_external=job_log_path_external,
            runtime_data=runtime_data,
        )

        with open(Path(settings.LOGS_FOLDER, f"{config_path}.sbatch"), "wt") as f:
            f.write(sbatch_str)

        slurm_job_id = _submit_sbatch_to_slurm(
            sbatch_str, settings.SLURM_TRAIN_FOLDER_EXTERNAL
        )

        logger.info(f"SUBMITTED COM TRAIN JOB TO CLUSTER. SLURM_JOB_ID={slurm_job_id}")
        # update jobs row to reflect job has been submitted
        curr.execute(
            f"UPDATE {TABLE_GPU_JOB} SET slurm_job_id = ?, slurm_status = 'PENDING' WHERE id = ?",
            (slurm_job_id, gpu_job_id),
        )
        conn.execute("COMMIT")

    return {"slurm_job_id": slurm_job_id}


@celery_app.task
def submit_predict_job(
    mode: Literal["COM", "DANNCE"],
    gpu_job_id: int,
    predict_job_id: int,
    runtime_id: int,
    job_name: str,
    log_path: str,
    config_path: str,
    cwd_folder_external_str: Path,
):
    if mode == "COM":
        sdannce_command = db.JobCommand.PREDICT_COM
    elif mode == "DANNCE":
        sdannce_command = db.JobCommand.PREDICT_DANNCE
    else:
        raise Exception("INVALID SDANNCE COMMAND")

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
            sdannce_command=sdannce_command,
            cwd_folder_external=Path(cwd_folder_external_str),
            job_name=job_name,
            log_file_external=job_log_path_external,
            runtime_data=runtime_data,
        )

        with open(Path(settings.LOGS_FOLDER, f"{config_path}.sbatch"), "wt") as f:
            f.write(sbatch_str)
            logger.info(f"FOR PREDICT JOB ID: {predict_job_id}, sbatch is written to: {Path(settings.LOGS_FOLDER_EXTERNAL, f'{config_path}.sbatch')}")

        slurm_job_id = _submit_sbatch_to_slurm(
            sbatch_str, settings.SLURM_TRAIN_FOLDER_EXTERNAL
        )
        logger.info(f"SUBMITTED COM PREDICT JOB TO CLUSTER. SLURM_JOB_ID={slurm_job_id}")

        # update jobs row to reflect job has been submitted
        curr.execute(
            f"UPDATE {TABLE_GPU_JOB} SET slurm_job_id = ?, slurm_status = 'PENDING' WHERE id = ?",
            (slurm_job_id, gpu_job_id),
        )

        logger.info(f"SHOUDL HAVE UPDATED TABLE GPU JOB to set slurm_job_id={slurm_job_id} WHERE gpu_job_id={gpu_job_id}")

        conn.execute("COMMIT")

    return {"slurm_job_id": slurm_job_id}


def _submit_sbatch_to_slurm(sbatch_str, current_dir=None) -> int:
    """Using subprocess, submit sbatch script to slurm from the specified directory

    Returns the slurm job id of the submitted job"""
    # Submit the job
    output = subprocess.check_output(
        "sbatch",
        input=sbatch_str,
        universal_newlines=True,
        cwd=current_dir,
        timeout=SLURM_TIMEOUT_SECONDS,
    )

    m = re.match(r"Submitted batch job (\d+)$", output)
    if m:
        job_id = m.group(1)
        job_id = int(job_id)
    else:
        raise Exception("unable to submit slurm job")
    return job_id
