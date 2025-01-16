#!/bin/bash

FASTAPI_PORT=7901
RABBITMQ_PORT=7902
FLOWER_PORT=7903
BASE_MOUNT=~/dannce-data
DATA_FOLDER=/Users/caxon/olveczky/dannce_data

# make sure BASE_VOLUME exists with correct permissions
mkdir -m777 -p $BASE_MOUNT

# make a env file at a temporary location
ENV_TEMPFILE=$(mktemp)
cat <<EOT >> $ENV_TEMPFILE
BASE_MOUNT=${BASE_MOUNT}
FASTAPI_PORT=${FASTAPI_PORT}
RABBITMQ_PORT=${RABBITMQ_PORT}
FLOWER_PORT=${FLOWER_PORT}
SERVER_BASE_URL=http://localhost:${FASTAPI_PORT}
API_BASE_URL=http://localhost:${FASTAPI_PORT}/v1
REACT_APP_BASE_URL=http://localhost:${FASTAPI_PORT}/app/index.html
SDANNCE_SINGULARITY_IMG_PATH=NOT_SET_ON_LOCALHOST
EOT

echo "Created env file at $ENV_TEMPFILE"
cat $ENV_TEMPFILE

# NOTE: run docker as read-only to ensure no data is stored in container
# this also makes it easier to run with singularity which is always read-only

docker run \
    --rm \
    -it \
    -p ${FASTAPI_PORT}:${FASTAPI_PORT} \
    -p ${FLOWER_PORT}:${FLOWER_PORT} \
    -v $BASE_MOUNT:/mnt-data \
    -v ./scripts:/app/scripts \
    -v ./src:/app/src \
    -v ./resources:/app/resources \
    -v $DATA_FOLDER:$DATA_FOLDER \
    --env-file ${ENV_TEMPFILE} \
    --read-only \
    --entrypoint /usr/local/bin/_entrypoint.sh \
    dannce-gui \
    /app/scripts/start_from_container-dev.sh
