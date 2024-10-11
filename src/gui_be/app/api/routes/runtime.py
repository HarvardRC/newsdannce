from typing import Any
from fastapi import APIRouter, HTTPException

from app.api.deps import SessionDep
from app.core.db import TABLE_RUNTIME
from app.models import CreateRuntimeModel

router = APIRouter()


@router.post("/")
def create_runtime(data: CreateRuntimeModel, session: SessionDep) -> Any:
    curr = session.cursor()
    curr.execute(
        f"INSERT INTO {TABLE_RUNTIME} (name, partition_list, memory_gb, time_hrs, n_cpus) VALUES (?,?,?,?,?)",
        (
            data.name,
            data.partition_list,
            data.memory_gb,
            data.time_hrs,
            data.n_cpus,
        ),
    )
    insert_id = curr.lastrowid
    session.commit()
    return {"id": insert_id}


@router.get("/list")
def list_all_runtime(session: SessionDep):
    rows = session.execute(f"select * from {TABLE_RUNTIME}").fetchall()
    rows = [dict(x) for x in rows]
    return rows


@router.get("/{id}")
def get_runtime(id: int, session: SessionDep) -> Any:
    row = session.execute(f"select * from {TABLE_RUNTIME} where id=?", (id,)).fetchone()
    if not row:
        raise HTTPException(status_code=404)
    return dict(row)
