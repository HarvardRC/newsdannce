#!/bin/bash

# run this from the gui_be directory

FASTAPI_PORT=7911
RABBITMQ_PORT=7912

BASE_MOUNT=/n/holylabs/LABS/olveczky_lab/Lab/dannce-dev/gui-instances/chris-20241218c
SDANNCE_IMG=/n/holylabs/LABS/olveczky_lab/Lab/singularity2/sdannce/sdannce-20241210.sif
DANNCE_GUI_IMG=/n/holylabs/LABS/olveczky_lab/Lab/dannce-dev/containers/dannce-gui-no-slurm-user.sif

mkdir -m777 -p $BASE_MOUNT

NODE_NAME=$SLURM_NODELIST

ENV_FILE=$(mktemp)
cat <<EOT >> $ENV_FILE
FASTAPI_PORT=${FASTAPI_PORT}
RABBITMQ_PORT=${RABBITMQ_PORT}
SERVER_BASE_URL=https://rcood.rc.fas.harvard.edu/rnode/${NODE_NAME}.rc.fas.harvard.edu/${FASTAPI_PORT}
API_BASE_URL=https://rcood.rc.fas.harvard.edu/rnode/${NODE_NAME}.rc.fas.harvard.edu/${FASTAPI_PORT}/v1
REACT_APP_BASE_URL=https://rcood.rc.fas.harvard.edu/rnode/${NODE_NAME}.rc.fas.harvard.edu/${FASTAPI_PORT}/app/index.html
SDANNCE_SINGULARITY_IMG_PATH=${SDANNCE_IMG}
EOT

echo "Created env file at $ENV_FILE"
cat $ENV_FILE

#### start shell in the container

# make slurm commands availbe within singularity container
SING_BINDS="-B /etc/nsswitch.conf -B /etc/sssd/ -B /var/lib/sss -B /etc/slurm -B /slurm -B /var/run/munge -B `which sbatch ` -B `which srun ` -B `which sacct ` -B `which scontrol ` -B `which salloc ` -B `which squeue` -B /usr/lib64/slurm/ "


singularity run \
    --bind $BASE_MOUNT:/mnt-data \
    --bind ./src:/app/src \
    --bind ./resources:/app/resources \
    --bind ./scripts/start_from_container-dev.sh:/app/scripts/start_from_container.sh \
    $SING_BINDS \
    --env-file $ENV_FILE \
    ${DANNCE_GUI_IMG}