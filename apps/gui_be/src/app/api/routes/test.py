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


# @router.post("/enqueue")
# def route_enqueue():
#     print("HELOOOO")
#     result = add.delay(3,4)
#     value =result.get(timeout=10)
#     return {"message": "done", "result": value}

# @router.post("/stall")
# def route_stall():
#     print("stalling")
#     result = stall.delay(999)
#     return {"message": "done"}
