# TRAINING
from dataclasses import dataclass
import re
from sqlite3 import Connection
import sqlite3
import subprocess

from app.base_logger import logger

import app.core.db as db

from app.models import (
    JobStatusDataObject,
)

from app.utils.predictions import update_prediction_status_by_job_id
from app.utils.time import now_timestamp
from app.utils.weights import update_weights_status_by_job_id

# wait at most this many seconds before killing the slurm subprocess
SLURM_TIMEOUT_SECONDS = 15

def submit_sbatch_to_slurm(sbatch_str, current_dir=None):
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


def insert_slurm_job_row(
    conn: sqlite3.Connection,
    slurm_job_id,
    pred_or_train_job_id,
    job_table_name: str,
):
    """Insert a row into the SLURM_JOB table and connect it with the train/predict job_id"""
    if job_table_name not in [db.TABLE_TRAIN_JOB, db.TABLE_PREDICT_JOB]:
        raise Exception("Invalid job_table_name")
    curr = conn.cursor()
    # start sqlite3 transaction
    curr.execute("BEGIN")
    try:
        # add slurm job to slurm_job table
        curr.execute(
            f"INSERT INTO {db.TABLE_GPU_JOB} (job_type, slurm_job_id, slurm_status) VALUES ('SLURM', ?, 'PENDING')",
            (slurm_job_id,),
        )
        # update ID of job table to slurm_job_id
        curr.execute(
            f"UPDATE {job_table_name} SET slurm_job=? WHERE id=?",
            (slurm_job_id, pred_or_train_job_id),
        )
    except sqlite3.Error as e:
        curr.execute("ROLLBACK")
        raise e
    conn.commit()
    logger.info("Successfully inserted slurm job and updated ?jobs_table.slurm_job")


@dataclass
class RefreshJobListResult:
    live_jobs: list[JobStatusDataObject]
    jobs_updated: list[JobStatusDataObject]


def refresh_job_list(conn) -> RefreshJobListResult:
    live_jobs = get_nonfinal_job_ids(conn)
    jobs_updated = update_jobs_by_ids(conn=conn, job_list=live_jobs)

    return RefreshJobListResult(live_jobs=live_jobs, jobs_updated=jobs_updated)


def get_nonfinal_job_ids(conn: Connection) -> list[JobStatusDataObject]:
    """Get all job ids which are not either FINSIHED or FAILED"""
    nonfinal_statuses = db.JobStatus.nonfinal_statuses(as_escaped_str=True)
    # Find ID of train or predict jobs
    # and gpu_job_id, TRAIN/PREDICT, slurm_status, and rutime_type
    rows = conn.execute(
        f"""
SELECT
    t1.id AS train_predict_job_id,
    t1.gpu_job_id AS gpu_job_id,
    t1.train_or_predict AS train_or_predict,
    t2.slurm_status AS slurm_status,
    t2.slurm_job_id AS slurm_job_id,
    t2.created_at AS created_at
FROM (
    SELECT
        id,
        gpu_job AS gpu_job_id,
        runtime AS runtime_id,
        'TRAIN' AS train_or_predict
    FROM {db.TABLE_TRAIN_JOB}

    UNION ALL SELECT
        id,
        gpu_job AS gpu_job_id,
        runtime AS runtime_id,
        'PREDICT' AS train_or_predict
    FROM {db.TABLE_PREDICT_JOB}
    ) t1
LEFT JOIN {db.TABLE_GPU_JOB} t2 ON t1.gpu_job_id = t2.id
LEFT JOIN {db.TABLE_RUNTIME} t3 ON t1.runtime_id = t3.id
WHERE t2.slurm_status IN ({nonfinal_statuses})
    AND t3.runtime_type='SLURM'
"""
    ).fetchall()

    results = [
        JobStatusDataObject(
            train_predict_job_id=row["train_predict_job_id"],
            gpu_job_id=row["gpu_job_id"],
            train_or_predict=row["train_or_predict"],
            job_status=row["slurm_status"],
            slurm_job_id=row["slurm_job_id"],
            created_at=row["created_at"],
        )
        for row in rows
    ]

    return results


@dataclass
class JobWithStatusType:
    job_id: int
    job_status: str

def update_jobs_by_ids(
    conn: Connection, job_list: list[JobStatusDataObject]
) -> list[JobStatusDataObject]:
    """Given a list of job id integers, update each job id using sacct. Returns any jobIds which have been updated"""
    # skip processing if no jobs to update
    if len(job_list) == 0:
        return []

    job_id_list_str = [str(x.slurm_job_id) for x in job_list]

    jobs_str = ",".join(job_id_list_str)
    logger.warning(f"Trying to update jobs with job_ids: {jobs_str}")

    try:
        output_sacct = subprocess.check_output(
            [
                "sacct",
                "-X",  # only return primary job for each JobID
                "-P",  # return parsable format
                "--delimiter=,",  # seperate entries with a comma
                "--format=JobID,State",  # return just these entries
                "--noheader",  # do not return header column
                f"--jobs={jobs_str}",  # list of jobs id strings separated by a comma
            ],
            stderr=subprocess.STDOUT,
            timeout=10,
            universal_newlines=True,
        )
    except subprocess.TimeoutExpired as e:
        logger.warning(f"timed out while fetching slurm job information. Error: {e}")
        raise e
    except subprocess.CalledProcessError as e:
        logger.warning(f"Nonzero process error code. Error: {e}")
        raise e

    logger.warning(f"Job output was: <{output_sacct}>")

    jobs_with_status: list[JobWithStatusType] = []
    for line in output_sacct.splitlines():
        logger.info(f"LINE: {line}")
        m = re.match(r"^(\d+),(\w+)", line)
        m_job_id = int(m.group(1))
        m_new_status = m.group(2)
        jobs_with_status.append(JobWithStatusType(
            job_id=m_job_id,
            job_status=m_new_status
        ))

    ids_queried_set = {x.slurm_job_id for x in job_list}
    ids_recieved_set = {x.job_id for x in jobs_with_status}

    # list of ids which were asked for but not returned by slurm (subtraction does set difference)
    ids_lost_to_slurm = list(ids_queried_set - ids_recieved_set)
    if len(ids_lost_to_slurm) > 0:
        logger.warning(
            f"The following slurm job ids were not found by slurm: {ids_lost_to_slurm}"
        )

    updated_job_list: list[JobStatusDataObject] = []

    for job_content in jobs_with_status:
        job_id = job_content.job_id
        new_status = job_content.job_status

        old_job_object = next(x for x in job_list if x.slurm_job_id == job_id)

        conn.execute(
            f"UPDATE {db.TABLE_GPU_JOB} SET slurm_status = ? WHERE slurm_job_id = ?",
            (new_status, job_id),
        )

        # if the job status was changed, add it to the list
        new_status_enum = db.JobStatus(new_status)
        if new_status_enum != old_job_object.job_status:
            new_job_object = old_job_object.model_copy(
                update={"job_status": new_status_enum}
            )
            logger.info(f"NEW JOB OBJECT: {new_job_object}")
            updated_job_list.append(new_job_object)

    for lost_job_id in ids_lost_to_slurm:
        old_job_object = next(x for x in job_list if x.slurm_job_id == lost_job_id)
        time_since_creation = now_timestamp() - old_job_object.created_at
        if (
            time_since_creation > 60 * 1
        ):  # if it's been at least 1 min since job created, we can mark it as lost
            conn.execute(
                f"UPDATE {db.TABLE_GPU_JOB} SET slurm_status = ? WHERE slurm_job_id = ?",
                (db.JobStatus.LOST_TO_SLURM.value, lost_job_id),
            )

            if new_status_enum != old_job_object.job_status:
                new_job_object = old_job_object.model_copy(
                    update={"job_status": db.JobStatus.LOST_TO_SLURM}
                )

                updated_job_list.append(new_job_object)

    for j in updated_job_list:
        logger.info(f"JOB DATA: {j}")
        if j.train_or_predict == "TRAIN":
            if j.job_status.is_failure():
                update_weights_status_by_job_id(conn, j.gpu_job_id, db.WeightsStatus.FAILED)
            elif j.job_status.is_success():
                update_weights_status_by_job_id(
                    conn, j.gpu_job_id, db.WeightsStatus.COMPLETED
                )
        elif j.train_or_predict == "PREDICT":
            if j.job_status.is_failure():
                logger.info(f"GPU PREDICT JOB FAILED: {j.gpu_job_id}")
                update_prediction_status_by_job_id(
                    conn, j.gpu_job_id, db.PredictionStatus.FAILED
                )
            elif j.job_status.is_success():
                logger.info(f"GPU PREDICT JOB SUCCEEDED: {j.gpu_job_id}")
                update_prediction_status_by_job_id(
                    conn, j.gpu_job_id, db.PredictionStatus.COMPLETED
                )
    conn.execute("COMMIT")

    return updated_job_list
