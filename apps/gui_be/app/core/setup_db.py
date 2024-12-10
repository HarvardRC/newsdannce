from dataclasses import dataclass
from app.core.db import TABLE_RUNTIME, get_db_context
import os
from datetime import datetime


@dataclass
class LocalResources:
    memory_gb: int
    time_hrs: int
    n_cpus: int
    n_gpus: int
    partition_list: str


def update_local_runtime():
    """Create the "local" runtime in the runtime table if it does not exist.
    Update the runtime to the current resources available if it does exist.

    This can be used to run dannce jobs on the same machine as the dannce_gui backend server is running on.
    """

    if "SLURM_JOB_ID" in os.environ:
        local_resources = get_local_resources_slurm()
    else:
        local_resources = get_local_resources_pc()


    with get_db_context() as session:
        curr = session.cursor()
        curr.execute(
            f"""
INSERT OR REPLACE INTO {TABLE_RUNTIME}(id, destination, name, memory_gb, time_hrs, n_cpus, n_gpus, partition_list) VALUES (1,'LOCAL','local',?,?,?,?,?)
                     """,
            (
                local_resources.memory_gb,
                local_resources.time_hrs,
                local_resources.n_cpus,
                local_resources.n_gpus,
                local_resources.partition_list,
            ),
        )
        curr.execute("COMMIT")
        print("UPDATED LOCAL RUNTIME")


def get_local_resources_slurm():
    """Get runtime parameters if the gui_be app is running on slurm"""
    n_cpus = int(os.environ["SLURM_CPUS_PER_TASK"])
    n_gpus = int(os.environ.get("SLURM_GPUS_ON_NODE", 0))
    mem_mb = int(os.environ["SLURM_MEM_PER_NODE"])
    mem_gb = int(mem_mb / 1024)
    job_end_timestamp = int(os.environ["SLURM_JOB_END_TIME"])
    now_timestamp = int(datetime.now().timestamp())
    # give a 2 minute buffer
    seconds_remaining = job_end_timestamp - now_timestamp - 2 * 60
    time_hrs = int(seconds_remaining / 3600)
    partition_list = os.environ["SLURM_JOB_PARTITION"]

    return LocalResources(
        n_cpus=n_cpus,
        n_gpus=n_gpus,
        memory_gb=mem_gb,
        partition_list=partition_list,
        time_hrs=time_hrs,
    )


def get_local_resources_pc():
    """Get runtime parameters if the gui_be app is running a local machine"""
    import psutil
    #import torch

    n_cpus = os.cpu_count()
    mem_gb = int(psutil.virtual_memory().total / 1024 / 1024 / 1024)
    time_hrs = 100_000  # very large number
    #n_gpus = 1 if torch.cuda.is_available else 0
    #TODO: FIX
    n_gpus = 0
    partition_list = None
    return LocalResources(
        n_cpus=n_cpus,
        n_gpus=n_gpus,
        memory_gb=mem_gb,
        partition_list=partition_list,
        time_hrs=time_hrs,
    )
