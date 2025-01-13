#!/bin/bash 

# these ports must match the ports in dev.env file
FASTAPI_PORT=7901
RABBITMQ_NODE_PORT=7902

INSTANCE_DIR=/tmp/dannce_gui_data 
ENV_FILE_PATH=./dev.env
TEMP_DIR=/tmp/dannce_gui
DATA_FOLDER=/Users/caxon/olveczky/dannce_data


# docker run \
#   -it dannce-gui \
#   --entrypoint "/app/scripts/start_from_container.sh" \
#   /bi/bash
echo 'source /mnt-data/.env after container starts'

docker run \
    --rm \
    -it \
    -p ${FASTAPI_PORT}:${FASTAPI_PORT} \
    -v $INSTANCE_DIR:/mnt-data/instance \
    -v $ENV_FILE_PATH:/mnt-data/.env \
    -v $TEMP_DIR:/tmp \
    -v $DATA_FOLDER:$DATA_FOLDER \
    --entrypoint "/usr/local/bin/_entrypoint.sh" \
    dannce-gui \
    /bin/bash
