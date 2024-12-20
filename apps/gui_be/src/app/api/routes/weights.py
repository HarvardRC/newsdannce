from fastapi import APIRouter

from app.api.deps import SessionDep
from app.core.db import TABLE_WEIGHTS

router = APIRouter()


@router.get("/list")
def list_all_weights(session: SessionDep):
    rows = session.execute(f"SELECT * FROM {TABLE_WEIGHTS}").fetchall()
    rows = [dict(x) for x in rows]
    return rows
