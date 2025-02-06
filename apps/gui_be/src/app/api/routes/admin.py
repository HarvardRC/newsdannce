"""Admin operations E.g. create database, set fake data
/admin
"""

from fastapi import APIRouter, HTTPException
import sys
from app.api.deps import SessionDep
from app.models import ExecuteSqlModel
from app.base_logger import logger

router = APIRouter()


@router.post("/test")
def test_route():
    return {"message": "tested"}


@router.post("/execute_sql")
def execute_sql(conn: SessionDep, data: ExecuteSqlModel):
    logger.info(f"SQL COMMAND WAS: {data.sql}")
    try:
        curr=  conn.cursor()
        curr.execute("BEGIN")
        rows = curr.execute(data.sql).fetchone()
        curr.execute("COMMIT")
    except Exception as e:
        logger.warning(f"EXCEPTION RUNNING SQL COMMAND: {e}")
        exc_type, exc_value, exc_tb = sys.exc_info()
        return {'status': 'error', 'message': e, 'additional info': f'{exc_type}/{exc_value}'}

    return {"status": "success!", "rows": rows}
