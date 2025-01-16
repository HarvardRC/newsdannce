"""Testing routes -- should not be available in prod"""

from fastapi import APIRouter
from app.core.db import (
    init_db,
)

# TRAINING
from pathlib import Path
import re
from sqlite3 import Connection
import sqlite3
import subprocess

# from taskqueue.tasks import add, stall

# import caldannce


router = APIRouter()


@router.post("/squeue")
def test_squeue():
    output = subprocess.check_output(
        "squeue", universal_newlines=True, cwd=None, timeout=2
    )
    return {"message-output": output}

TEST_IMPORT_FOLDER="/Users/caxon/olveczky/dannce_data/ALONE/240625_143814_M5"

@router.post('/test-import')
def test_import_route():
    from taskqueue.video import import_video_folder_worker

    import_video_folder_worker.delay(TEST_IMPORT_FOLDER)

    return {"status" : "import queued"}

@router.post('/test-dotask')
def test_dotask_route():
    from taskqueue.video import dummy_task_me
    dummy_task_me.delay()
    return {"hello" : "world"}


@router.post("/check-celery")
def check_celery_route():
    from taskqueue.celery import celery_app, MAIN_QUEUE_NAME
    with celery_app.connection_or_acquire() as conn:
        client = conn.channel().client

        # ct = conn.default_channel.queue_declare(queue=None, passive=True).message_count
        return {
            "message_count": client.llen(MAIN_QUEUE_NAME)
        }