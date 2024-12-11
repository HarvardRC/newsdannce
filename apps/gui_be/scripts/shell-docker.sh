FASTAPI_PORT=8700
RABBITMQ_NODE_PORT=8701
INSTANCE_DIR=~/dannce_gui_data 

# docker run \
#   -it dannce-gui \
#   --entrypoint "/app/scripts/start_from_container.sh" \
#   /bi/bash

docker run \
    -it \
    --env FASTAPI_PORT=$FASTAPI_PORT \
    --env RABBITMQ_NODE_PORT=$RABBITMQ_NODE_PORT \
    --env INSTANCE_DIR=$INSTANCE_DIR \
    --env PYTHONUNBUFFERED=1 \
    -p ${FASTAPI_PORT}:${FASTAPI_PORT} \
    -v $INSTANCE_DIR:/instance_dir \
    --entrypoint "/usr/local/bin/_entrypoint.sh" \
    dannce-gui \
    /bin/bash
