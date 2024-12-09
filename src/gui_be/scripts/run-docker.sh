#!/bin/bash

FASTAPI_PORT=8700
RABBITMQ_NODE_PORT=8701
INSTANCE_DIR=~/dannce_gui_data 

port=$FASTAPI_PORT

echo "Connect to port ${FASTAPI_PORT}"

# adding -it will allow docker to be killed with CTRL+C

docker run \
    -it \
    --env FASTAPI_PORT=$FASTAPI_PORT \
    --env RABBITMQ_NODE_PORT=$RABBITMQ_NODE_PORT \
    --env INSTANCE_DIR=$INSTANCE_DIR \
    -p ${FASTAPI_PORT}:${FASTAPI_PORT} \
    -v $INSTANCE_DIR:/instance_dir \
    dannce-gui
