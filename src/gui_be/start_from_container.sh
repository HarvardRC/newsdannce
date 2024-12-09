#!/bin/bash

echo "Running from container start script"

echo "RABBTIMQ_NODE_PORT=$RABBITMQ_NODE_PORT"
echo "FASTAPI_PORT=$FASTAPI_PORT"

echo "INSTANCE_DIR=$INSTANCE_DIR"

(trap 'kill 0' SIGINT; \
    rabbitmq-server &\
    celery -A taskqueue.celery worker --loglevel=INFO &\
    python -m uvicorn app.main:app --host 0.0.0.0 --port $FASTAPI_PORT --log-level debug
)

