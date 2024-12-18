#!/bin/bash

echo "Running from container start script"

if [ ! -f /mnt-data/.env ]; then
  echo "An env file must be mounted at /mnt-data/.env"
  echo "File does not exist! Exiting."
fi

source /mnt-data/.env

# echo variables for debugging
echo "###### ENV VARIABLES: ######"
echo "INSTANCE_DIR_MOUNT = ${INSTANCE_DIR_MOUNT}"
echo "ENV_FILE_MOUNT = ${ENV_FILE_MOUNT}"
echo "TMP_DIR_MOUNT = ${TMP_DIR_MOUNT}"
echo "APP_DIR = ${APP_DIR}"
echo "APP_SRC_DIR = ${APP_SRC_DIR}"
echo "APP_RESOURCES_DIR = ${APP_RESOURCES_DIR}"
echo "REACT_APP_DIST_FOLDER = ${REACT_APP_DIST_FOLDER}"
echo "FASTAPI_PORT = ${FASTAPI_PORT}"
echo "RABBITMQ_NODE_PORT = ${RABBITMQ_NODE_PORT}"
echo "FLOWER_PORT = ${FLOWER_PORT}"
echo "FASTAPI_BASE_URL = ${FASTAPI_BASE_URL}"
echo "REACT_APP_BASE_URL = ${REACT_APP_BASE_URL}"
echo "SDANNCE_SINGULARITY_IMG_PATH = ${SDANNCE_SINGULARITY_IMG_PATH}"
echo "RABBITMQ_MNESIA_DIR = ${RABBITMQ_MNESIA_DIR}"

echo "#####################"

cd /app/src

echo "Starting processes for dannce-gui..."
export MPLCONFIGDIR="/tmp"

export HOME="/tmp"

# allow killing all processes with single CTRL+C
(trap 'kill 0' SIGINT; \
    rabbitmq-server &\
    celery -A taskqueue.celery worker --loglevel=INFO &\
    python -m uvicorn app.main:app --host 0.0.0.0 --port $FASTAPI_PORT --log-level debug
)

echo "Done running dannce-gui"
