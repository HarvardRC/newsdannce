#!/bin/bash
echo "Running from container start script"
echo "RUNNING DEV VERSION OF SCRIPT"

export TMPDIR="/mnt-data/tmp" # must be set before you can use a here-doc

echo "The following variables should been set from container env-file"
cat << EOF
BASE_MOUNT=${BASE_MOUNT}
FASTAPI_PORT=${FASTAPI_PORT}
RABBITMQ_PORT=${RABBITMQ_PORT}
FLOWER_PORT=${FLOWER_PORT}
FLOWER_BASE_URL=${FLOWER_BASE_URL}
SERVER_BASE_URL=${SERVER_BASE_URL}
API_BASE_URL=${API_BASE_URL}
REACT_APP_BASE_URL=${REACT_APP_BASE_URL}
SDANNCE_SINGULARITY_IMG_PATH=${SDANNCE_SINGULARITY_IMG_PATH}
EOF

echo "SETTING FIXED DIRECTORIES"

#### SET ALL FIXED LOCATIONS WIHTIN THE CONTAINER AS ENV VARIABLES ####
# Every container (docker/singularity) should assume these paths exist
# fixed locations within the container
export APP_DIR="/app"
export APP_SRC_DIR="/app/src"
export APP_RESOURCES_DIR="/app/resources"
export REACT_APP_DIST_FOLDER="/app/resources/react-dist"
# mounted locations

export INSTANCE_DIR="/mnt-data/instance"
export TMP_DIR="/mnt-data/tmp"
export RABBITMQ_LOG_BASE="/mnt-data/logs"
export RABBITMQ_MNESIA_BASE="/mnt-data/rabbitmq_mnesia"
export FLOWER_DB="/mnt-data/flower_db"
export CELERY_BEAT_FILES="/mnt-data/celery-beat"


# variables so python uses the correct TMP directories
export MPLCONFIGDIR="${TMP_DIR}/mpl-cache"        # MatPlotLib requires a cache directory
export TEMPDIR="${TMP_DIR}/python-tmpfiles"       # Python tempfile requires a temporary directory
FAKE_HOME_RABBITMQ="${TMP_DIR}/erlang-fake-home"  # Erlang (for rabbitmq) creates a cookie file in home directory

echo "FAKE_HOME_RMQ: $FAKE_HOME_RABBITMQ"
mkdir -m777 -p $FAKE_HOME_RABBITMQ

mkdir -m777 -p $FLOWER_DB

cd /app/src

echo "Starting processes for dannce-gui..."

echo "FLOWER PORT IS $FLOWER_PORT"

# allow killing all processes with single CTRL+C
(trap 'kill 0' SIGINT; \
    HOME=$FAKE_HOME_RABBITMQ rabbitmq-server &\
    celery -A taskqueue.celery worker --beat --loglevel=INFO &\
    FLOWER_UNAUTHENTICATED_API=true celery -A taskqueue.celery flower --loglevel=INFO &\
    DEBUG=1 python -m uvicorn app.main:app --host 0.0.0.0 --port $FASTAPI_PORT --log-level debug --reload
)    

echo "Done running dannce-gui"

#### attempts to make celery persistent - do not work yet
#  --persistent=True --db="$FLOWER_DB" --save-state-interval=5