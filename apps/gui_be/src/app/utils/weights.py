from dataclasses import dataclass
import json
from pathlib import Path
import sqlite3
import re
import string

from app.core.db import TABLE_GPU_JOB, TABLE_TRAIN_JOB, TABLE_WEIGHTS, WeightsStatus
from app.core.config import settings
from app.base_logger import logger


def get_latest_checkpoint_filename(weights_path: Path) -> Path:
    """Assuming training checkpoint files are in the format checkpoint-epochX.pth, return the highest X number checkpoint file
    Or return checkpoint-final.pth if it exists

    NOTE: this returns the filename only. Must be appended to "WEIGHTS_FOLDER[_EXTERNAL]" to get full path.
    """
    checkpoint_final = Path(
        settings.WEIGHTS_FOLDER, weights_path, "checkpoint-final.pth"
    )
    logger.info(f"Final checkpoint: {checkpoint_final}")
    if checkpoint_final.exists() or checkpoint_final.is_symlink():
        return 'checkpoint_final.pth'

    checkpoint_files = Path(settings.WEIGHTS_FOLDER, weights_path).glob(
        "checkpoint-epoch*.pth"
    )

    try:
        checkpoint_files = (
            (x, int(re.match(r"checkpoint-epoch(\d+).pth", x.name).group(1)))
            for x in checkpoint_files
        )
        checkpoint_files = sorted(checkpoint_files, key=lambda x: x[1], reverse=True)
        first_checkpoint_filename = checkpoint_files[0][0].name

        return first_checkpoint_filename

    except Exception as e:
        raise Exception(f"No checkpoint file exists. Error msg={e}")


@dataclass
class WeightsPathDataType:
    weights_path: string
    latest_filename: string


def get_weights_path_from_id(conn: sqlite3.Connection, weights_id) -> WeightsPathDataType:
    row = conn.execute(
        f"""
SELECT
    path,
    status
FROM {TABLE_WEIGHTS}
WHERE id=?
        """,
        (weights_id,),
    ).fetchone()
    if not row:
        raise Exception(f"Weights column not found for id: {weights_id}")
    if row["status"] == "FAILED" or row["status"] == "PENDING":
        raise Exception(
            f"Weights column for id={weights_id} has non-COMPLETED status of {row['status']}"
        )

    weights_path = row["path"]

    base_path = Path(settings.WEIGHTS_FOLDER, weights_path)

    latest_checkpoint_filename = get_latest_checkpoint_filename(base_path)

    return WeightsPathDataType(
        weights_path=weights_path,
        latest_filename=latest_checkpoint_filename
    )


def update_weights_status_by_job_id(
    conn: sqlite3.Connection, gpu_job_id: int, status: WeightsStatus
):
    """Update weights status to a give status value (e.g. COMPLETED) given the id of the corresponding train job
    NOTE: does not commit transaction! expected to commit by containing function.
    """

        #  get mode and path given GPU job id:
    row = conn.execute(
        f"""
SELECT
    t_wts.id AS weights_id, t_wts.mode, t_wts.path
FROM
    {TABLE_WEIGHTS} t_wts
LEFT JOIN {TABLE_TRAIN_JOB} t_train_j
    ON t_train_j.weights = t_train_j.id
LEFT JOIN {TABLE_GPU_JOB} t_gpu_j
    ON t_gpu_j.id = t_train_j.gpu_job WHERE t_gpu_j.id = ?
""", (gpu_job_id,)).fetchone()
    row = dict(row)
    weights_id = row['weights_id']
    mode = row['mode']
    path = row['path']

    filename = get_latest_checkpoint_filename(path)

    conn.execute(
        f"""
UPDATE {TABLE_WEIGHTS}
SET
    status = ?,
    filename = ?
WHERE id = ?;
                 """,
        (
            status.value,
            filename,
            weights_id,
        ),
    )

