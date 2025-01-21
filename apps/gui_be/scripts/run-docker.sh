#!/bin/bash

FASTAPI_PORT=7901
RABBITMQ_PORT=7902
BASE_MOUNT=~/dannce-data
DATA_FOLDER=/Users/caxon/olveczky/dannce_data

# make sure BASE_VOLUME exists with correct permissions
mkdir -m777 -p $BASE_MOUNT

# make a env file at a temporary location
ENV_TEMPFILE=$(mktemp)
cat <<EOT >> $ENV_TEMPFILE
FASTAPI_PORT=${FASTAPI_PORT}
RABBITMQ_PORT=${RABBITMQ_PORT}
SERVER_BASE_URL=http://localhost:${FASTAPI_PORT}
API_BASE_URL=http://localhost:${FASTAPI_PORT}/v1
REACT_APP_BASE_URL=http://localhost:${FASTAPI_PORT}/app/index.html
SDANNCE_SINGULARITY_IMG_PATH=NOT_SET_ON_LOCALHOST
MAX_CONCURRENT_LOCAL_JOBS=1
EOT

echo "Created env file at $ENV_TEMPFILE"
cat $ENV_TEMPFILE

# NOTE: run docker as read-only to ensure no data is stored in container
# this also makes it easier to run with singularity which is always read-only

docker run \
    --rm \
    -it \
    -p ${FASTAPI_PORT}:${FASTAPI_PORT} \
    -v $BASE_MOUNT:/mnt-data \
    -v $DATA_FOLDER:$DATA_FOLDER \
    --env-file ${ENV_TEMPFILE} \
    --read-only \
    dannce-gui
