# TRAINING
from pathlib import Path
import re
from sqlite3 import Connection
import sqlite3
import subprocess

from app.base_logger import logger

from app.core.config import settings
import app.core.db as db

from app.models import (
    JobStatusDataObject,
)
from app.utils.make_io_yaml import (
    ComPredictModel,
    ComTrainModel,
    DanncePredictModel,
    DannceTrainModel,
)
from app.utils.make_sbatch import make_sbatch_str
from app.utils.predictions import update_prediction_status_by_job_id
from app.utils.runtimes import get_runtime_data_id
from app.utils.time import now_timestamp
from app.utils.weights import update_weights_status_by_job_id

# wait at most this many seconds before killing the slurm subprocess
SLURM_TIMEOUT_SECONDS = 10
CONFIG_PATH = "/n/holylabs/LABS/olveczky_lab/Lab/dannce-dev/hannah-data/configs/dannce_rat_config.yaml"


def bg_submit_com_predict_job(
    cfg: ComPredictModel,
    runtime_id: int,
    predict_job_id: int,
    weights_id: int,
    prediction_id: int,
    config_file: Path,
):
    with open(config_file, "wt") as f:
        logger.info(f"Writing config file to {config_file}")
        yaml_string = cfg.to_yaml_string()
        f.write(yaml_string)

    with db.SessionContext() as conn:
        runtime_data = get_runtime_data_id(runtime_id, conn)

        command_enum = db.JobCommand.PREDICT_COM

        # make theh sbatch string
        sbatch_str = make_sbatch_str(
            command_enum,
            config_path=config_file,
            runtime_data=runtime_data,
            job_name="predict_com",
            cwd_folder=cfg.META_cwd,
        )

        # TODO: REMOVE - tmp debug by writing out slurm string
        # with open(Path(settings.DATA_FOLDER, "tmp", "pred-com-out.sbatch"), "wt") as f:
        #     f.write(sbatch_str)

        # submit sbatch string to slurm
        slurm_job_id = submit_sbatch_to_slurm(
            sbatch_str,
            # NOTE: this sets were the slurm process will start from.
            # shouldn't matter since it's paths are absolute and slurm job will cd where needed
            current_dir=settings.SLURM_TRAIN_FOLDER,
        )
        # slurm_job_id = 1234567

        insert_slurm_job_row(conn, slurm_job_id, predict_job_id, db.TABLE_PREDICT_JOB)


def bg_submit_com_train_job(
    cfg: ComTrainModel,
    runtime_id: int,
    train_job_id: int,
    weights_id: int,
    config_file: Path,
):
    with open(config_file, "wt") as f:
        logger.info(f"Writing config file to {config_file}")
        yaml_string = cfg.to_yaml_string()
        f.write(yaml_string)

    with db.SessionContext() as conn:
        runtime_data = get_runtime_data_id(runtime_id, conn)

        command_enum = db.JobCommand.TRAIN_COM

        # make theh sbatch string
        sbatch_str = make_sbatch_str(
            command_enum,
            config_path=config_file,
            runtime_data=runtime_data,
            job_name="train_com",
            cwd_folder=cfg.META_cwd,
        )

        # # TODO: REMOVE - tmp debug by writing out slurm string
        # with open(Path(settings.DATA_FOLDER, "tmp", "train-com-out.sbatch"), "wt") as f:
        #     f.write(sbatch_str)

        # submit sbatch string to slurm
        slurm_job_id = submit_sbatch_to_slurm(
            sbatch_str,
            # NOTE: this sets were the slurm process will start from.
            # shouldn't matter since it's paths are absolute and slurm job will cd where needed
            current_dir=settings.SLURM_TRAIN_FOLDER,
        )

        insert_slurm_job_row(conn, slurm_job_id, train_job_id, db.TABLE_TRAIN_JOB)


def bg_submit_dannce_predict_job(
    cfg: DanncePredictModel,
    runtime_id: int,
    predict_job_id: int,
    weights_id: int,
    prediction_id: int,
    config_file: Path,
):
    with open(config_file, "wt") as f:
        logger.info(f"Writing config file to {config_file}")
        yaml_string = cfg.to_yaml_string()
        f.write(yaml_string)

    with db.SessionContext() as conn:
        runtime_data = get_runtime_data_id(runtime_id, conn)

        command_enum = db.JobCommand.PREDICT_DANNCE

        # make theh sbatch string
        sbatch_str = make_sbatch_str(
            command_enum,
            config_path=config_file,
            runtime_data=runtime_data,
            job_name="predict_dannce",
            cwd_folder=cfg.META_cwd,
        )

        with open(
            Path(settings.SBATCH_DEBUG_FOLDER, config_file.with_suffix(".out").name),
            "wt",
        ) as f:
            f.write(sbatch_str)

        # TODO: REMOVE - tmp debug by writing out slurm string
        # with open(Path(settings.DATA_FOLDER, "tmp", "pred-com-out.sbatch"), "wt") as f:
        #     f.write(sbatch_str)

        # submit sbatch string to slurm
        slurm_job_id = submit_sbatch_to_slurm(
            sbatch_str,
            # NOTE: this sets were the slurm process will start from.
            # shouldn't matter since it's paths are absolute and slurm job will cd where needed
            current_dir=settings.SLURM_TRAIN_FOLDER,
        )
        # slurm_job_id = 1234567

        insert_slurm_job_row(conn, slurm_job_id, predict_job_id, db.TABLE_PREDICT_JOB)


def bg_submit_dannce_train_job(
    cfg: DannceTrainModel,
    runtime_id: int,
    train_job_id: int,
    weights_id: int,
    config_file: Path,
):
    with open(config_file, "wt") as f:
        logger.info(f"Writing config file to {config_file}")
        yaml_string = cfg.to_yaml_string()
        f.write(yaml_string)

    with db.SessionContext() as conn:
        runtime_data = get_runtime_data_id(runtime_id, conn)

        command_enum = db.JobCommand.TRAIN_DANNCE

        # make theh sbatch string
        sbatch_str = make_sbatch_str(
            command_enum,
            config_path=config_file,
            runtime_data=runtime_data,
            job_name="train_dannce",
            cwd_folder=cfg.META_cwd,
        )

        with open(
            Path(settings.SBATCH_DEBUG_FOLDER, config_file.with_suffix(".out").name),
            "wt",
        ) as f:
            f.write(sbatch_str)

        # submit sbatch string to slurm
        slurm_job_id = submit_sbatch_to_slurm(
            sbatch_str,
            # NOTE: this sets were the slurm process will start from.
            # shouldn't matter since it's paths are absolute and slurm job will cd where needed
            current_dir=settings.SLURM_TRAIN_FOLDER,
        )

        insert_slurm_job_row(conn, slurm_job_id, train_job_id, db.TABLE_TRAIN_JOB)


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
            f"INSERT INTO {db.TABLE_SLURM_JOB} (slurm_job_id, status) VALUES (?, 'PENDING')",
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


def check_job_status_multiple(job_list):
    job_list = [str(x) for x in job_list]
    jobs_str = ",".join(job_list)

    try:
        output = subprocess.check_output(
            ["sacct", "-j", "job", jobs_str, "--format=JobID,State", "--noheader"],
            stderr=subprocess.STDOUT,
            timeout=SLURM_TIMEOUT_SECONDS,
            universal_newlines=True,
        )
    except subprocess.TimeoutExpired as e:
        print("timed out while fetching slurm job information. Error: {e}")
        raise Exception
    except subprocess.CalledProcessError as e:
        print("Nonzero process error code. Error: {e}")
        raise Exception
    except Exception as e:
        raise Exception(f"Uknown error {e}")

    matches = re.findall(r"^(\d+)\s*([A-Z]+)", output, re.MULTILINE)

    update_list = []

    for job_id_str, job_state in matches:
        update_list.append(
            {"job_id": int(job_id_str), "job_state": db.JobState(job_state)}
        )

    return update_list


def check_job_status(job_id):
    out_data = {
        "job_id": job_id,
        "job_state": None,
        "start_time": None,
        "stdout_file": None,
    }
    try:
        output_scontrol = subprocess.check_output(
            ["scontrol", "show", "job", str(job_id)],
            stderr=subprocess.STDOUT,
            timeout=SLURM_TIMEOUT_SECONDS,
            universal_newlines=True,
        )
    except subprocess.TimeoutExpired as e:
        print(f"timed out while fetching slurm job information. Error: {e}")
        raise Exception
    except subprocess.CalledProcessError as e:
        print(f"Nonzero process error code. Error: {e}")
        raise Exception
    except Exception as e:
        raise Exception(f"Uknown error {e}")

    job_state_re = r"^[ \t]*JobState=(\w+)"
    stdout_file_re = r"^[ \t]*StdOut=(.+)$"

    m_job_state = re.search(job_state_re, output_scontrol, re.MULTILINE)
    if m_job_state:
        out_data["job_state"] = m_job_state.group(1)

    m_stdout_file = re.search(stdout_file_re, output_scontrol, re.MULTILINE)
    if m_stdout_file:
        out_data["stdout_file"] = m_stdout_file.group(1)

    return out_data


def get_nonfinal_job_ids(conn: Connection) -> list[JobStatusDataObject]:
    """Get all job ids which are not either FINSIHED or FAILED"""
    nonfinal_statuses = db.JobStatus.nonfinal_statuses(as_escaped_str=True)
    rows = conn.execute(
        f"""
SELECT id, slurm_job_id, train_or_predict, status, created_at FROM (
    SELECT id, slurm_job as slurm_job_id, 'TRAIN' as train_or_predict from {db.TABLE_TRAIN_JOB}
    UNION ALL
    select id, slurm_job as slurm_job_id, 'PREDICT' as train_or_predict from {db.TABLE_PREDICT_JOB}
), {db.TABLE_SLURM_JOB} USING (slurm_job_id) WHERE status IN ({nonfinal_statuses})
"""
    ).fetchall()

    results = [
        JobStatusDataObject(
            slurm_job_id=row["slurm_job_id"],
            job_id=row["id"],
            train_or_predict=row["train_or_predict"],
            job_status=row["status"],
            created_at=row["created_at"],
        )
        for row in rows
    ]

    return results


def update_jobs_by_ids(conn: Connection, job_list: list[JobStatusDataObject]):
    """Given a list of job id integers, update each job id using sacct. Returns any jobIds which have been updated"""
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
                "--format=JobID,State,StdOut",  # return just these entries
                "--noheader",  # do not return header column
                f"--jobs={jobs_str}",  # list of jobs id strings separated by a comma
            ],
            stderr=subprocess.STDOUT,
            timeout=10,
            universal_newlines=True,
        )
    except subprocess.TimeoutExpired as e:
        print(f"timed out while fetching slurm job information. Error: {e}")
        raise e
    except subprocess.CalledProcessError as e:
        print(f"Nonzero process error code. Error: {e}")
        raise e

    logger.warning(f"Job output was: <{output_sacct}>")

    jobs_with_status = []
    for line in output_sacct.splitlines():
        print(line)
        m = re.match(r"^(\d+),(\w+),(.+)", line)
        m_job_id = int(m.group(1))
        m_new_status = m.group(2)
        m_stdout = m.group(3)
        jobs_with_status.append([m_job_id, m_new_status, m_stdout])

    ids_queried_set = {x.slurm_job_id for x in job_list}
    ids_recieved_set = {x[0] for x in jobs_with_status}
    # list of ids which were asked for but not returned by slurm
    ids_lost_in_slurm = list(ids_queried_set - ids_recieved_set)
    if len(ids_lost_in_slurm) > 0:
        logger.warning(
            f"The following slurm job ids were not found by slurm: {ids_lost_in_slurm}"
        )

    updated_job_list: list[JobStatusDataObject] = []

    for job_content in jobs_with_status:
        job_id = job_content[0]
        new_status = job_content[1]
        stdout_file = job_content[2]

        old_job_object = next(x for x in job_list if x.slurm_job_id == job_id)

        conn.execute(
            f"UPDATE {db.TABLE_SLURM_JOB} SET status=?, stdout_file=? WHERE slurm_job_id=?",
            (new_status, stdout_file, job_id),
        )

        # if the job status was changed, add it to the list
        new_status_enum = db.JobStatus(new_status)
        if new_status_enum != old_job_object.job_status:
            new_job_object = old_job_object.model_copy(
                update={"job_status": new_status_enum}
            )

            updated_job_list.append(new_job_object)

    for lost_job_id in ids_lost_in_slurm:
        old_job_object = next(x for x in job_list if x.slurm_job_id == lost_job_id)
        time_since_creation = now_timestamp() - old_job_object.created_at
        if (
            time_since_creation > 60 * 1
        ):  # if it's been at least 1 min since job created, we can mark it as lost
            conn.execute(
                f"UPDATE {db.TABLE_SLURM_JOB} SET status=? WHERE slurm_job_id=?",
                (db.JobStatus.LOST_TO_SLURM.value, lost_job_id),
            )

            if new_status_enum != old_job_object.job_status:
                new_job_object = old_job_object.model_copy(
                    update={"job_status": db.JobStatus.LOST_TO_SLURM}
                )

                updated_job_list.append(new_job_object)

    for j in updated_job_list:
        if j.train_or_predict == "TRAIN":
            if j.job_status.is_failure():
                update_weights_status_by_job_id(conn, j.job_id, db.WeightsStatus.FAILED)
            elif j.job_status.is_success():
                update_weights_status_by_job_id(
                    conn, j.job_id, db.WeightsStatus.COMPLETED
                )
        elif j.train_or_predict == "PREDICT":
            if j.job_status.is_failure():
                update_prediction_status_by_job_id(
                    conn, j.job_id, db.PredictionStatus.FAILED
                )
            elif j.job_status.is_success():
                update_prediction_status_by_job_id(
                    conn, j.job_id, db.PredictionStatus.COMPLETED
                )
    conn.commit()

    return updated_job_list
