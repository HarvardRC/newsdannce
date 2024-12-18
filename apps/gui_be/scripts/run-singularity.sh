#!/bin/bash

FASTAPI_PORT=7911
RABBITMQ_NODE_PORT=7912

BASE_VOLUME=/home/caxon/dannce-data-sing
INSTANCE_DIR=$BASE_VOLUME/instance 
LOGS_DIR=$BASE_VOLUME/logs
TEMP_DIR=$BASE_VOLUME/tmp
RABBITMQ_MNESIA_DIR=$BASE_VOLUME/rabbitmq-mnesia

mkdir -m777 -p $BASE_VOLUME
mkdir -m777 -p $INSTANCE_DIR
mkdir -m777 -p $LOGS_DIR
mkdir -m777 -p $TEMP_DIR
mkdir -m777 -p $RABBITMQ_MNESIA_DIR

ENV_FILE_PATH=./dev.env

port=$FASTAPI_PORT

echo "Connect to port ${FASTAPI_PORT}"

#### start shell in the container
# singularity exec dannce-gui.sif /usr/local/bin/_entrypoint.sh /bin/bash
# singularity run dannce-gui.sif

singularity run \
    --bind $ENV_FILE_PATH:/mnt-data/.env \
    --bind $INSTANCE_DIR:/mnt-data/instance \
    --bind $TEMP_DIR:/tmp \
    --bind $LOGS_DIR:/mnt-data/logs \
    --bind $RABBITMQ_MNESIA_DIR:/mnt-data/rabbitmq_mnesia \
    dannce-gui.sif

# singularity exec \
#     --bind $ENV_FILE_PATH:/mnt-data/.env \
#     --bind $INSTANCE_DIR:/mnt-data/instance \
#     --bind $TEMP_DIR:/tmp \
#     --bind $LOGS_DIR:/mnt-data/logs \
#     --bind $RABBITMQ_MNESIA_DIR:/mnt-data/rabbitmq_mnesia \
#     dannce-gui.sif /usr/local/bin/_entrypoint.sh /bin/bash
