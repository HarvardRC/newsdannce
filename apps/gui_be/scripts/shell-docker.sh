#!/bin/bash 

# these ports must match the ports in dev.env file
FASTAPI_PORT=7801
RABBITMQ_PORT=7802
FLOWER_PORT=7903
BASE_MOUNT=~/dannce-gui-instance

DATA_FOLDER=/Users/caxon/olveczky/dannce_data

# make a env file at a temporary location
ENV_TEMPFILE=$(mktemp)
cat <<EOT >> $ENV_TEMPFILE
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


docker run \
    --rm \
    -it \
    -v $BASE_MOUNT:/mnt-data \
    -v ./scripts:/app/scripts \
    -v ./src:/app/src \
    -v ./resources:/app/resources \
    -v $DATA_FOLDER:$DATA_FOLDER \
    --env-file ${ENV_TEMPFILE} \
    --read-only \
    --entrypoint /usr/local/bin/_entrypoint.sh \
    dannce-gui \
    /bin/bash
