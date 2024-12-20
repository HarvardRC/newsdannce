import json
from pathlib import Path
import sqlite3
import re

from app.core.db import TABLE_TRAIN_JOB, TABLE_WEIGHTS, WeightsStatus


def get_latest_checkpoint(weights_path: Path) -> Path:
    """Assuming training checkpoint files are in the format checkpoint-epochX.pth, return the highest X number checkpoint file
    Or return checkpoint-final.pth if it exists"""
    checkpoint_final = Path(weights_path, "checkpoint-final.pth")
    print(checkpoint_final)
    if checkpoint_final.exists() or checkpoint_final.is_symlink():
        return checkpoint_final

    checkpoint_files = weights_path.glob("checkpoint-epoch*.pth")
    try:
        checkpoint_files = (
            (x, int(re.match(r"checkpoint-epoch(\d+).pth", x.name).group(1)))
            for x in checkpoint_files
        )
        checkpoint_files = sorted(checkpoint_files, key=lambda x: x[1], reverse=True)
        return checkpoint_files[0][0]
    except Exception as e:
        raise Exception(f"No checkpoint file exists. Error msg={e}")


def get_weights_path_from_id(conn: sqlite3.Connection, weights_id) -> Path:
    row = conn.execute(
        f"""
SELECT path,status FROM {TABLE_WEIGHTS} WHERE id=?
                 """,
        (weights_id,),
    ).fetchone()
    if not row:
        raise Exception(f"Weights column not found for id: {weights_id}")
    if row["status"] == "FAILED" or row["status"] == "PENDING":
        raise Exception(
            f"Weights column for id={weights_id} has non-COMPLETED status of {row['status']}"
        )
    base_path = Path(row["path"])
    latest_checkpoint = get_latest_checkpoint(base_path)
    return latest_checkpoint


def update_weights_status_by_job_id(
    conn: sqlite3.Connection, train_job_id: int, status: WeightsStatus
):
    """Update weights status to a give status value (e.g. COMPLETED) given the id of the corresponding train job
    NOTE: does not commit transaction! expected to commit by containing function.
    """
    conn.execute(
        f"""
UPDATE {TABLE_WEIGHTS}
SET status=?
FROM (
    SELECT t1.id AS wid,
            t2.id as tid
    FROM {TABLE_WEIGHTS} t1
        LEFT JOIN {TABLE_TRAIN_JOB} t2
        ON t2.weights = t1.id
    WHERE tid=?
) AS tmp
WHERE tmp.wid = {TABLE_WEIGHTS}.id;
                 """,
        (
            status.value,
            train_job_id,
        ),
    )
