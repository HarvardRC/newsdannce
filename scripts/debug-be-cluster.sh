#!/bin/bash

BASE_PROXY_HOST="https://rcood.rc.fas.harvard.edu/rnode/${SLURM_NODELIST}.rc.fas.harvard.edu"

export port=10790
export FASTAPI_PORT=${port}

export FLOWER_PORT=10791
export RABBITMQ_PORT=10792

export FLOWER_BASE_URL="${BASE_PROXY_HOST}/${FLOWER_PORT}"
export SERVER_BASE_URL="${BASE_PROXY_HOST}/${FASTAPI_PORT}"
export API_BASE_URL="${SERVER_BASE_URL}/v1"
export REACT_APP_BASE_URL="${SERVER_BASE_URL}/app/index.html"
export SDANNCE_SINGULARITY_IMG_PATH="/n/holylabs/LABS/olveczky_lab/Lab/singularity2/sdannce/sdannce-20241210.sif"
export DANNCE_GUI_SINGULARITY_IMG_PATH="/n/holylabs/LABS/olveczky_lab/Lab/dannce-dev/containers/dannce-gui.sif"

export ENV_FILE="/n/holylabs/LABS/olveczky_lab/Lab/dannce-dev/tmp-run/cluster-debug.env"
export BASE_MOUNT="/n/holylabs/LABS/olveczky_lab/Lab/dannce-dev/gui-instances/chris-20250204a"
echo "Base Mount (instance_dir): $BASE_MOUNT (making if does not exist)"

mkdir -p $BASE_MOUNT

echo "FLOWER PORT IS ${FLOWER_PORT}"
echo "FLOWER URL IS: ${FLOWER_BASE_URL}"

# write an env file used to launch singularity
cat <<EOT >> $ENV_FILE
BASE_MOUNT=${BASE_MOUNT}
FASTAPI_PORT=${FASTAPI_PORT}
RABBITMQ_PORT=${RABBITMQ_PORT}
FLOWER_PORT=${FLOWER_PORT}
SERVER_BASE_URL=${SERVER_BASE_URL}
FLOWER_BASE_URL=${FLOWER_BASE_URL}
API_BASE_URL="${API_BASE_URL}"
REACT_APP_BASE_URL="${REACT_APP_BASE_URL}"
SDANNCE_SINGULARITY_IMG_PATH="${SDANNCE_SINGULARITY_IMG_PATH}"
MAX_CONCURRENT_LOCAL_JOBS=0
EOT

export JOBROOT=$PWD

echo "Cat'ing env file"
cat $ENV_FILE
echo "Eching env varibales..."
echo "RABBITMQ_PORT=${RABBITMQ_PORT}"
echo "FASTAPI_PORT=${FASTAPI_PORT}"
echo "FLOWER_PORT=${FLOWER_PORT}"
echo "SERVER_BASE_URL=${SERVER_BASE_URL}"
echo "API_BASE_URL=${API_BASE_URL}"
echo "REACT_APP_BASE_URL=${REACT_APP_BASE_URL}"
echo "ENV_FILE=${ENV_FILE}"
echo "JOBROOT=${JOBROOT}"
echo "SDANNCE_SINGULARITY_IMG_PATH=${SDANNCE_SINGULARITY_IMG_PATH}"
echo "DANNCE_GUI_SINGULARITY_IMG_PATH=${DANNCE_GUI_SINGULARITY_IMG_PATH}"
echo "HOSTNAME:"
hostname -I

echo "DONE WITH BEFORE SCRIPT"

SING_BINDS=\
'-B /etc/nsswitch.conf '\
'-B /etc/slurm '\
'-B /lib64/libnss_sss.so.2:/lib/libnss_sss.so.2 '\
'-B /run/munge '\
'-B /slurm '\
'-B /usr/bin/sacct '\
'-B /usr/bin/salloc '\
'-B /usr/bin/sbatch '\
'-B /usr/bin/scancel '\
'-B /usr/bin/scontrol '\
'-B /usr/bin/scrontab '\
'-B /usr/bin/seff '\
'-B /usr/bin/sinfo '\
'-B /usr/bin/squeue '\
'-B /usr/bin/srun '\
'-B /usr/bin/sshare '\
'-B /usr/bin/sstat '\
'-B /usr/bin/strace '\
'-B /usr/lib64/libmunge.so.2 '\
'-B /usr/lib64/slurm '\
'-B /var/lib/sss'

singularity run \
    $SING_BINDS \
    --bind ${BASE_MOUNT}:/mnt-data \
    --bind ${BASE_MOUNT}:/${BASE_MOUNT} \
    --env-file ${ENV_FILE} \
    ${DANNCE_GUI_SINGULARITY_IMG_PATH}

