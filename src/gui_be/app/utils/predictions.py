import sqlite3

from app.core.db import (
    TABLE_PREDICT_JOB,
    TABLE_PREDICTION,
    PredictionStatus,
)


def update_prediction_status_by_job_id(
    conn: sqlite3.Connection, predict_job_id: int, status: PredictionStatus
):
    conn.execute(
        f"""
UPDATE {TABLE_PREDICTION}
SET status=?
FROM (
    SELECT t1.id AS pid,
            t2.id as jid
    FROM {TABLE_PREDICTION} t1
        LEFT JOIN {TABLE_PREDICT_JOB} t2
        ON t2.prediction = t1.id
    WHERE jid=?
) AS tmp
WHERE tmp.pid = {TABLE_PREDICTION}.id;
                 """,
        (
            status.value,
            predict_job_id,
        ),
    )
