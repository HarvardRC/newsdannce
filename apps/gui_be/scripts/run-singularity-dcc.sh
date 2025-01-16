#!/bin/bash

# testing run script on the Duke Compute Cluster (DCC)

FASTAPI_PORT=7911
RABBITMQ_PORT=7912

NODE_NAME=$SLURM_NODELIST

BASE_MOUNT=./data-mnt

mkdir -m777 -p $BASE_MOUNT

ENV_FILE=$(mktemp)
cat <<EOT >> $ENV_FILE
FASTAPI_PORT=${FASTAPI_PORT}
RABBITMQ_PORT=${RABBITMQ_PORT}
SERVER_BASE_URL=https://dcc-ondemand-01.oit.duke.edu/rnode/${NODE_NAME}/${FASTAPI_PORT}
API_BASE_URL=https://dcc-ondemand-01.oit.duke.edu/rnode/${NODE_NAME}/${FASTAPI_PORT}/v1
REACT_APP_BASE_URL=https://dcc-ondemand-01.oit.duke.edu/rnode/${NODE_NAME}/${FASTAPI_PORT}/app/index.html
SDANNCE_SINGULARITY_IMG_PATH=NOT_SET_ON_LOCALHOST
SLURM_CPUS_PER_TASK=8
SLURM_GPUS_ON_NODE=1
SLURM_MEM_PER_NODE=16384
SLURM_JOB_END_TIME=1734668185
SLURM_JOB_PARTITION=test
EOT

echo "Created env file at $ENV_FILE"
cat $ENV_FILE

#### start shell in the container

singularity run \
    --bind $BASE_MOUNT:/mnt-data \
    --bind /hpc:/hpc
    --env-file $ENV_FILE \
    ./dannce-gui.sif
