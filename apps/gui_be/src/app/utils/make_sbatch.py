"""Build SBATCH Scripts"""

from pathlib import Path
import shlex

import app.core.db as db
from app.models import RuntimeData
from app.core.config import settings


def make_sbatch_str(
    command_enum: db.JobCommand,
    config_path: str,
    job_name: str,
    runtime_data: RuntimeData,
    cwd_folder: str,
):
    script_str = _build_sbatch_script(
        sdannce_command=command_enum,
        config_path=config_path,
        runtime_data=runtime_data,
        cwd_folder=cwd_folder,
        job_name=job_name,
    )
    return script_str


# internal call - you usually want to use the version which includes defaults
def _build_sbatch_script(
    config_path,
    sdannce_command: db.JobCommand,
    cwd_folder,
    job_name,
    runtime_data: RuntimeData,
):
    # make sure Path objects are strings
    config_path_str = str(config_path)
    cwd_folder_str = str(cwd_folder)
    log_file_str = str(Path(settings.LOGS_FOLDER, "%j.out").resolve())
    sdannce_img_path_str = str(settings.SDANNCE_IMAGE_PATH)

    sdannce_command_safe = sdannce_command.get_full_command()

    return f"""#!/bin/bash
#SBATCH --mem={shlex.quote(str(runtime_data.memory_gb))}GB
#SBATCH --gres=gpu:1
#SBATCH --time={shlex.quote(str(runtime_data.time_hrs))}:00:00
#SBATCH --cpus-per-task={shlex.quote(str(runtime_data.n_cpus))}
#SBATCH --partition={shlex.quote(runtime_data.partition_list)}
#SBATCH --job-name={shlex.quote(job_name)}
#SBATCH --output={shlex.quote(log_file_str)}

# metadata: runtime name={shlex.quote(runtime_data.name)}

# run with conda env (debugging)
#########
### TODO: REMOVE -- debug with conda instead of singularity for now ################
# source ~/.bashrc
# module load Mambaforge
# conda activate sdannce311
# cd {shlex.quote(cwd_folder_str)}
# dannce {sdannce_command_safe} {shlex.quote(config_path_str)}
### END TODO: REMOVE ###############################################################

# run from sdannce container
#########
SDANNCE_IMG={shlex.quote(sdannce_img_path_str)}
singularity exec --nv --pwd={shlex.quote(cwd_folder_str)} "$SDANNCE_IMG" dannce {sdannce_command_safe} {shlex.quote(config_path_str)}

"""
