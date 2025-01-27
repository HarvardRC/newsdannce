import json
from pathlib import Path
import sqlite3
import re

from app.core.db import TABLE_TRAIN_JOB, TABLE_WEIGHTS, WeightsStatus
from app.core.config import settings
from app.base_logger import logger

def get_latest_checkpoint(weights_path: Path) -> Path:
    """Assuming training checkpoint files are in the format checkpoint-epochX.pth, return the highest X number checkpoint file
    Or return checkpoint-final.pth if it exists

    NOTE: this returns the full EXTERNAL filepath
    """
    checkpoint_final = Path(settings.WEIGHTS_FOLDER, weights_path, "checkpoint-final.pth")
    logger.info(f"Final checkpoint: {checkpoint_final}")
    if checkpoint_final.exists() or checkpoint_final.is_symlink():
        return Path(settings.WEIGHTS_FOLDER_EXTERNAL, weights_path, "checkpoint-final.pth")

    checkpoint_files = Path(settings.WEIGHTS_FOLDER, weights_path).glob("checkpoint-epoch*.pth")
    try:
        checkpoint_files = (
            (x, int(re.match(r"checkpoint-epoch(\d+).pth", x.name).group(1)))
            for x in checkpoint_files
        )
        checkpoint_files = sorted(checkpoint_files, key=lambda x: x[1], reverse=True)
        first_checkpoint_filename = checkpoint_files[0][0].name
        return Path(settings.WEIGHTS_FOLDER_EXTERNAL, weights_path, first_checkpoint_filename)

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
    base_path = Path(settings.WEIGHTS_FOLDER, row["path"])
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
