import sqlite3


from app.core import db
from app.models import RuntimeData


def get_runtime_data_id(runtime_id: int, conn: sqlite3.Connection):
    runtime_row = conn.execute(
        f"SELECT id, name, partition_list, memory_gb, time_hrs, n_cpus FROM {db.TABLE_RUNTIME} WHERE id=?",
        (runtime_id,),
    ).fetchone()
    runtime_row = dict(runtime_row)
    runtime_data = RuntimeData(
        id=runtime_row["id"],
        name=runtime_row["name"],
        partition_list=runtime_row["partition_list"],
        memory_gb=runtime_row["memory_gb"],
        time_hrs=runtime_row["time_hrs"],
        n_cpus=runtime_row["n_cpus"],
    )
    return runtime_data
