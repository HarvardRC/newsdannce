"""
/runtime
"""
from typing import Any
from fastapi import APIRouter, HTTPException

from app.api.deps import SessionDep
from app.core.db import TABLE_RUNTIME
from app.models import CreateRuntimeModel

router = APIRouter()


@router.post("/")
def create_runtime(conn: SessionDep, data: CreateRuntimeModel, ) -> Any:
    curr = conn.cursor()
    curr.execute(
        f"INSERT INTO {TABLE_RUNTIME} (name, runtime_type, partition_list, memory_gb, time_hrs, n_cpus, n_gpus) VALUES (?,?,?,?,?,?,?)",
        (
            data.name,
            "SLURM",
            data.partition_list,
            data.memory_gb,
            data.time_hrs,
            data.n_cpus,
            1,
        ),
    )
    insert_id = curr.lastrowid
    conn.commit()
    return {"id": insert_id}


@router.get("/list")
def list_all_runtime(conn: SessionDep):
    rows = conn.execute(f"SELECT * FROM {TABLE_RUNTIME}").fetchall()
    rows = [dict(x) for x in rows]
    return rows


@router.get("/{id}")
def get_runtime(id: int, conn: SessionDep) -> Any:
    row = conn.execute(f"SELECT * FROM {TABLE_RUNTIME} WHERE ID=?", (id,)).fetchone()
    if not row:
        raise HTTPException(status_code=404)
    return dict(row)
