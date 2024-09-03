"""Build SBATCH Scripts"""

from enum import Enum
from pathlib import PurePosixPath
import shlex
from .sdannce_command_enum import SDannceCommand
# DEFAULT SLURM SETTINGS

# medium priority params used for SPECIFIC sdannce train/predict slurm submissions, can be override by user data
TRAIN_COM_DEFAULT = {
    "mem_gb": 50,
    "max_time_hrs": 24,
    "n_cpus_per_task": 4,
    "output_file": "train_com-%j.out",
    "job_name": "train_com-DANNCE_GUI",
}
TRAIN_DANNCE_DEFAULT = {
    "mem_gb": 300,
    "max_time_hrs": 72,
    "n_cpus_per_task": 16,
    "output_file": "train_dannce-%j.out",
    "job_name": "train_dannce-DANNCE_GUI",
}
PREDICT_COM_DEFAULT = {
    "mem_gb": 30,
    "max_time_hrs": 24,
    "n_cpus_per_task": 4,
    "output_file": "pred_com-%j.out",
    "job_name": "pred_com-DANNCE_GUI",
}
PREDICT_DANNCE_DEFAULT = {
    "mem_gb": 30,
    "max_time_hrs": 24,
    "n_cpus_per_task": 4,
    "output_file": "pred_dannce-%j.out",
    "job_name": "pred_dannce-DANNCE_GUI",
}

# lowest priority params used for ALL sdannce train/predict slurm submissions, can be overriden by user data
DEFAULT_PARAMS = {
    "sdannce_container": "/n/holylabs/LABS/olveczky_lab/Lab/singularity/sdannce2/sdannce2.sif",
    "logs_folder": "./logs",
}


def merge_data(override_data, command_default_data):
    """Merge three dicts to create data for slurm command"""
    return {**DEFAULT_PARAMS, **command_default_data, **override_data}


DEFAULT_AVAILABLE_PARTITIONS = {
    "olveczkygpu": {
        "mem_per_node": 192,
        "max_time_hrs": 7 * 24,
        # MAX_TIME_HOURS for olveczkygpu is actually unlimited but no DANNCE job should run for more than 7 days
        "cpus_per_node": 48,
    },
    "gpu": {"mem_per_node": 64, "max_time_hrs": 7 * 3, "cpus_per_node": 64},
}


def get_valid_partitions_str(
    max_time_hrs,
    n_cpus_per_task,
    mem_gb,
    available_partitions=DEFAULT_AVAILABLE_PARTITIONS,
) -> str:
    """Given constraints, return a list of partitions specified by PARTITIONS argument
    E.g. returns: 'olveczkygpu,gpu'"""
    valid_partitions = []
    for name, specs in available_partitions.items():
        if (
            max_time_hrs <= specs["max_time_hrs"]
            and n_cpus_per_task <= specs["cpus_per_node"]
            and mem_gb <= specs["mem_per_node"]
        ):
            valid_partitions.append(name)

    if len(valid_partitions) == 0:
        raise Exception("Unable to find any valid partitions for job params")

    partition_str = ",".join(valid_partitions)
    return partition_str


# internal call - you usually want to use the version which includes defaults
def _build_sbatch_script(
    config_path,
    sdannce_command: SDannceCommand,
    project_folder,
    job_name,
    mem_gb,
    max_time_hrs,
    n_cpus_per_task,
    sdannce_container,
    logs_folder,
    output_file,
    override_partition=None,  # optionally manually specify a partition
):
    if override_partition is not None:
        partition_str = override_partition
    else:
        partition_str = get_valid_partitions_str(n_cpus_per_task, max_time_hrs, mem_gb)

    output_file_full = str(PurePosixPath(logs_folder, output_file))

    sdannce_command_safe = sdannce_command.value

    return f"""#!/bin/bash
#SBATCH --mem='{shlex.quote(str(mem_gb))}GB'
#SBATCH --gres='gpu:1'
#SBATCH --time='{shlex.quote(str(max_time_hrs))}:00:00'
#SBATCH --cpus-per-task='{shlex.quote(str(n_cpus_per_task))}'
#SBATCH --partition='{shlex.quote(partition_str)}'
#SBATCH --job-name='{shlex.quote(job_name)}'
#SBATCH --output='{shlex.quote(output_file_full)}'

### TODO: REMOVE -- debug with conda instead of singularity for now ################
source ~/.bashrc
module load Mambaforge
conda activate sdannce311
cd {shlex.quote(project_folder)}
dannce {sdannce_command_safe} {shlex.quote(config_path)}
### END TODO: REMOVE ###############################################################

# img='{shlex.quote(sdannce_container)}'
# singularity exec --nv --pwd={shlex.quote(project_folder)} "$img" dannce {sdannce_command_safe} {shlex.quote(config_path)}
"""


def make_sbatch_str(
    command_enum: SDannceCommand, config_path: str, project_folder: str, **override_data
):
    match command_enum:
        case SDannceCommand.TRAIN_COM:
            default_dict = TRAIN_COM_DEFAULT
        case SDannceCommand.TRAIN_DANNCE:
            default_dict = TRAIN_DANNCE_DEFAULT
        case SDannceCommand.PREDICT_COM:
            default_dict = PREDICT_COM_DEFAULT
        case SDannceCommand.PREDICT_DANNCE:
            default_dict = PREDICT_DANNCE_DEFAULT
        case _:
            raise Exception('Invalid script type: must be e.g. "train com"')
    data = merge_data(override_data, default_dict)

    script_str = _build_sbatch_script(
        sdannce_command=command_enum,
        project_folder=project_folder,
        config_path=config_path,
        **data,
    )
    return script_str
