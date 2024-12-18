#!/bin/bash

FASTAPI_PORT=7911
RABBITMQ_NODE_PORT=7912

BASE_VOLUME=~/dannce-data-singularity

mkdir -m777 -p $BASE_VOLUME

ENV_TEMPFILE=$(mktemp)
cat <<EOT >> $ENV_TEMPFILE
FASTAPI_PORT=${FASTAPI_PORT}
RABBITMQ_PORT=${RABBITMQ_PORT}
FASTAPI_BASE_URL="http://localhost:${FASTAPI_PORT}/v1"
REACT_APP_BASE_URL="http://localhost:${FASTAPI_PORT}/app/index.html"
SDANNCE_SINGULARITY_IMG_PATH="NOT_SET_ON_LOCALHOST"
EOT

echo "Created env file at $ENV_TEMPFILE"
cat $ENV_TEMPFILE

#### start shell in the container
# singularity exec dannce-gui.sif /usr/local/bin/_entrypoint.sh /bin/bash
# singularity run dannce-gui.sif

singularity run \
    --bind $BASE_MOUNT:/mnt-data \
    --env-file $ENV_FILE
    dannce-gui.sif

# singularity exec \
#     --bind $ENV_FILE_PATH:/mnt-data/.env \
#     --bind $INSTANCE_DIR:/mnt-data/instance \
#     --bind $TEMP_DIR:/tmp \
#     --bind $LOGS_DIR:/mnt-data/logs \
#     --bind $RABBITMQ_MNESIA_DIR:/mnt-data/rabbitmq_mnesia \
#     dannce-gui.sif /usr/local/bin/_entrypoint.sh /bin/bash
