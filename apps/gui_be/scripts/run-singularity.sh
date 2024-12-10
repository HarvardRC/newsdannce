#!/bin/bash

FASTAPI_PORT=8700
RABBITMQ_NODE_PORT=8701
INSTANCE_DIR=~/dannce_gui_data

port=$FASTAPI_PORT

echo "Connect to port ${FASTAPI_PORT}"

#### start shell in the container
# singularity exec dannce-gui.sif /usr/local/bin/_entrypoint.sh /bin/bash
singularity run dannce-gui.sif --bind $INSTANCE_DIR:/instance_dir
