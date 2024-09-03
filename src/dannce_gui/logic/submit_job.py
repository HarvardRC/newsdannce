# submit job for training or inference


# TRAINING

from pathlib import Path
import argparse
import os
import re
import subprocess
import time
from datetime import datetime
from dateutil.parser import parse

from ..db import get_db, JOB_TABLE
from .sdannce_command_enum import SDannceCommand
from .job_state_enum import JobState

# wait at most this many seconds before killing hte subprocess
DEFAULT_TIMEOUT_SECONDS = 10


def submit_job(sbatch_str, sdannce_command: SDannceCommand, project_folder):
    # unix seconds since epoch when job was created
    timestamp_seconds = int(datetime.now().timestamp())

    # Submit the job
    output = subprocess.check_output(
        "sbatch", input=sbatch_str, universal_newlines=True
    )

    m = re.match(r"Submitted batch job (\d+)$", output)
    if m:
        job_id = m.group(1)
        job_id = int(job_id)
    else:
        raise Exception("unable to submit slurm job")

    print("SUBMITTED {} JOB WITH ID: {}".format(sdannce_command, job_id))

    initial_data = check_job_status(job_id=job_id)
    stdout_file = initial_data["stdout_file"]

    try:
        conn = get_db()
        conn.execute(
            f"INSERT INTO {JOB_TABLE} (job_id, sdannce_command, status, created_at, stdout_file, project_folder) VALUES (?, ?, ?, ?, ?, ?)",
            [
                job_id,
                sdannce_command.value,
                JobState.PENDING.value,
                timestamp_seconds,
                stdout_file,
                project_folder,
            ],
        )
        conn.commit()

    except Exception as e:
        print("unable to write to the database")
        raise e

    return job_id


def check_job_status_multiple(job_list):
    job_list = [str(x) for x in job_list]
    jobs_str = ",".join(job_list)

    try:
        output = subprocess.check_output(
            ["sacct", "-j", "job", jobs_str, "--format=JobID,State", "--noheader"],
            stderr=subprocess.STDOUT,
            timeout=DEFAULT_TIMEOUT_SECONDS,
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
            {"job_id": int(job_id_str), "job_state": JobState(job_state)}
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
            timeout=DEFAULT_TIMEOUT_SECONDS,
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

    job_state_re = r"^[ \t]*JobState=(\w+)"
    stdout_file_re = r"^[ \t]*StdOut=(.+)$"
    start_time_re = r"^[ \t]*StartTime=(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})"

    m_job_state = re.search(job_state_re, output_scontrol, re.MULTILINE)
    if m_job_state:
        out_data["job_state"] = m_job_state.group(1)

    m_stdout_file = re.search(stdout_file_re, output_scontrol, re.MULTILINE)
    if m_stdout_file:
        out_data["stdout_file"] = m_stdout_file.group(1)

    #  check for estimated start time

    # m_start_time = re.search(start_time_re, output_scontrol, re.MULTILINE)
    # if m_start_time:
    #     out_data["start_time"] = m_start_time.group(1)

    return out_data


def update_job_status_all():
    curr = get_db()

    states_to_check = [
        x.value
        for x in [
            JobState.PENDING,
            JobState.PREEMPTED,
            JobState.SUSPENDED,
            JobState.COMPLETING,
            JobState.RUNNING,
        ]
    ]
    states_to_check_str = ",".join(states_to_check)
    curr.execute(
        f"""
SELECT 
    job_id
FROM 
    {JOB_TABLE}
WHERE 
    job_state IN ({states_to_check_str})
"""
    )
