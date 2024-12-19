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

# import caldannce


router = APIRouter()


@router.post("/squeue")
def test_squeue():
    output = subprocess.check_output(
        "squeue", universal_newlines=True, cwd=None, timeout=2
    )
    return {"message-output": output}
