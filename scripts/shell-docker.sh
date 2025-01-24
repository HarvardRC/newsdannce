#!/bin/bash 

# these ports must match the ports in dev.env file
FASTAPI_PORT=7701
RABBITMQ_PORT=7702
FLOWER_PORT=7703

BASE_MOUNT=~/dannce-gui-instance
DATA_FOLDER=~/olveczky/dannce_data

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
MAX_CONCURRENT_LOCAL_JOBS=1
EOT

echo "Created env file at $ENV_TEMPFILE"
cat $ENV_TEMPFILE

docker run \
    --rm \
    -it \
    -p ${FASTAPI_PORT}:${FASTAPI_PORT} \
    -v $BASE_MOUNT:/mnt-data \
    -v $DATA_FOLDER:$DATA_FOLDER \
    -v /var/run/docker.sock:/var/run/docker.sock \
    --env-file ${ENV_TEMPFILE} \
    --read-only \
    --entrypoint /usr/local/bin/_entrypoint.sh \
    dannce-gui \
    /bin/bash
