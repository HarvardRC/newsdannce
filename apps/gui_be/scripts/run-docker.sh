#!/bin/bash

# these ports must match the ports in dev.env file
FASTAPI_PORT=7901
RABBITMQ_NODE_PORT=7902

BASE_VOLUME=/tmp/dannce_gui
INSTANCE_DIR=$BASE_VOLUME/instance 
LOGS_DIR=$BASE_VOLUME/logs
TEMP_DIR=$BASE_VOLUME/tmp
RABBITMQ_MNESIA_DIR=$BASE_VOLUME/rabbitmq-mnesia

mkdir -p $INSTANCE_DIR
mkdir -p $LOGS_DIR
mkdir -p $TEMP_DIR
mkdir -p $RABBITMQ_MNESIA_DIR

ENV_FILE_PATH=./dev.env

port=$FASTAPI_PORT

echo "Connect to port ${FASTAPI_PORT}"

# adding -it will allow docker to be killed with CTRL+C
# --env PYTHONUNBUFFERED=1 \

docker run \
    --rm \
    -it \
    -p ${FASTAPI_PORT}:${FASTAPI_PORT} \
    -v $ENV_FILE_PATH:/mnt-data/.env \
    -v $INSTANCE_DIR:/mnt-data/instance \
    -v $TEMP_DIR:/tmp \
    -v $LOGS_DIR:/mnt-data/logs \
    -v $RABBITMQ_MNESIA_DIR:/mnt-data/rabbitmq_mnesia \
    --read-only \
    dannce-gui
