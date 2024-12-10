import app.core.db as db
from app.utils.time import now_timestamp


def get_metadata(conn):
    result = conn.execute(
        f"SELECT * FROM {db.TABLE_GLOBAL_STATE}",
    ).fetchone()
    return dict(result)


def update_metadata(conn, column_name, value):
    conn.execute(
        f"UPDATE {db.TABLE_GLOBAL_STATE} SET {column_name}=? WHERE id=0",
        [value],
    )
    conn.commit()


def get_last_jobs_refresh(conn):
    return get_metadata(conn)[db.METADATA_LAST_UPDATE_JOBS]


def update_last_jobs_refresh(conn):
    update_metadata(conn, db.METADATA_LAST_UPDATE_JOBS, now_timestamp())
