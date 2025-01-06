#!/bin/bash

FASTAPI_PORT=7911
RABBITMQ_PORT=7912

BASE_MOUNT=~/dannce-data-singularity

mkdir -m777 -p $BASE_MOUNT

ENV_FILE=$(mktemp)
cat <<EOT >> $ENV_FILE
FASTAPI_PORT=${FASTAPI_PORT}
RABBITMQ_PORT=${RABBITMQ_PORT}
SERVER_BASE_URL=http://localhost:${FASTAPI_PORT}
API_BASE_URL=http://localhost:${FASTAPI_PORT}/v1
REACT_APP_BASE_URL=http://localhost:${FASTAPI_PORT}/app/index.html
SDANNCE_SINGULARITY_IMG_PATH=NOT_SET_ON_LOCALHOST
EOT

echo "Created env file at $ENV_FILE"
cat $ENV_FILE

#### start shell in the container

singularity run \
    --bind $BASE_MOUNT:/mnt-data \
    --env-file $ENV_FILE \
    ./dannce-gui.sif
