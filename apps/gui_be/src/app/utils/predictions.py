from dataclasses import dataclass
from pathlib import Path
import sqlite3
from typing import Literal

from app.base_logger import logger
from fastapi import HTTPException
import numpy as np

from app.core.db import (
    TABLE_GPU_JOB,
    TABLE_PREDICT_JOB,
    TABLE_PREDICTION,
    TABLE_VIDEO_FOLDER,
    PredictionStatus,
)
from app.core.config import settings
from scipy.io import loadmat


def update_prediction_status_by_job_id(
    conn: sqlite3.Connection, gpu_job_id: int, status: PredictionStatus
):
    logger.info(
        f"UPDATE PRED. STAT BY JOB ID: {gpu_job_id}; Status value: {status.value}, status: {status}"
    )

    #  get mode and path given GPU job id:
    row = conn.execute(
        f"""
SELECT
    t_pred.id AS prediction_id,
    t_pred.mode,
    t_pred.path,
    t_pred.video_folder AS video_folder_id
FROM
    {TABLE_PREDICTION} t_pred
LEFT JOIN {TABLE_PREDICT_JOB} t_pred_j
    ON t_pred_j.prediction = t_pred.id
LEFT JOIN {TABLE_GPU_JOB} t_gpu_j
    ON t_gpu_j.id = t_pred_j.gpu_job WHERE t_gpu_j.id = ?
""",
        (gpu_job_id,),
    ).fetchone()
    row = dict(row)
    prediction_id = row["prediction_id"]
    video_folder_id = row["video_folder_id"]
    mode = row["mode"]
    path = row["path"]

    if status.value == "COMPLETED":
        filename = get_prediction_filename(mode, path)
        conn.execute(
            f"""
UPDATE {TABLE_PREDICTION}
SET
    status = ?,
    filename = ?
WHERE id = ?
            """,
            (
                status.value,
                filename,
                prediction_id,
            ),
        )
        conn.execute(
            f"""
UPDATE {TABLE_VIDEO_FOLDER}
SET
    current_com_prediction = ?
WHERE
    id = ?
""", (prediction_id, video_folder_id))

    # status=failed
    else:
        conn.execute(
            f"""
UPDATE {TABLE_PREDICTION}
SET
    status = ?
WHERE id = ?
            """,
            (
                status.value,
                prediction_id,
            ),
        )

    conn.execute("COMMIT")


def get_com_prediction_file(
    conn: sqlite3.Connection, predict_job_id: int, samples: int, to_list=True
):
    """
    samples: # of samples to return (sampled evenly across recording)
    """
    row = conn.execute(
        f"""
SELECT
    t1.path AS path,
    t1.status AS status,
    t1.mode AS mode

FROM {TABLE_PREDICTION} t1
WHERE t1.id=?
""",
        (predict_job_id,),
    ).fetchone()

    if not row:
        raise HTTPException(404, "Prediction id not found")
    row = dict(row)

    path = row["path"]
    status = row["status"]
    mode = row["mode"]

    if mode != "COM":
        raise HTTPException(
            400, "Prediction id must reference a COM prediction (not DANNCE)"
        )

    if status != "COMPLETED":
        raise HTTPException(400, "Prediction must be completed. Not pending or failed.")

    pred_data_file = Path(
        settings.PREDICTIONS_FOLDER, path, get_prediction_filename("COM", path)
    )

    m = loadmat(pred_data_file)

    # Number of datapoints to return

    # shape: 90000x3
    com_data = m["com"]
    if samples == -1:
        # return all samples
        frame_samples = np.arange(0, com_data.shape[0])
    else:
        frame_samples = np.linspace(0, com_data.shape[0] - 1, samples).astype(np.int32)
    com_data = com_data[frame_samples]

    idxs = frame_samples.reshape(-1, 1)
    com_data = np.hstack([idxs, com_data])
    if to_list:
        return com_data.tolist()
    else:
        return com_data


def get_prediction_filename(
    mode: Literal["COM", "DANNCE", "SDANNCE"], prediction_path: str
):
    base_path = Path(settings.PREDICTIONS_FOLDER, prediction_path)

    if mode == "COM":
        filenames = [x.name for x in base_path.glob("com3d*.mat")]
        if "com3d.mat" in filenames:
            return "com3d.mat"
        elif len(filenames) > 0:
            return filenames[0]
        else:
            raise Exception(
                f"[COM] PREDICTION FILENAME NOT FOUND FOR path {prediction_path}"
            )
    elif mode == "DANNCE":
        filenames = [x.name for x in base_path.glob("save_data_AVG*.mat")]
        if "save_data_AVG0.mat" in filenames:
            return "save_data_AVG0.mat"
        elif len(filenames) > 0:
            return filenames[0]
        else:
            raise Exception(
                f"[DANNCE] PREDICTION FILENAME NOT FOUND FOR path {prediction_path}"
            )
    else:
        raise Exception(f"PREDICITON MODE {mode} NOT SUPPORTED FOR MIGRATION")


@dataclass
class COMDeltasData:
    hist: list[int]
    bin_edges: list[float]


def get_com_deltas(conn: sqlite3.Connection, predict_job_id: int):
    com_data = get_com_prediction_file(
        conn, predict_job_id=predict_job_id, samples=-1, to_list=False
    )
    subsequent_diffs = np.diff(com_data[:, 1:4], axis=0)
    norms = np.linalg.norm(subsequent_diffs, axis=1)
    hist, bin_edges = np.histogram(norms, bins=15)
    return COMDeltasData(hist=hist.tolist(), bin_edges=bin_edges.tolist())


@dataclass
class PredictionMetadata:
    n_joints: int
    n_frames: int


def get_prediction_metadata(
    status, mode: Literal["COM", "DANNCE", "SDANNCE"], prediction_path: str
) -> PredictionMetadata:
    if status != "COMPLETED":
        n_joints = -1
        n_frames = -1
    elif mode == "COM":
        path = Path(
            settings.PREDICTIONS_FOLDER,
            prediction_path,
            get_prediction_filename("COM", prediction_path),
        )
        m = loadmat(path)
        n_frames = m["com"].shape[0]
        n_joints = 1
    elif mode == "DANNCE":
        path = Path(
            settings.PREDICTIONS_FOLDER,
            prediction_path,
            get_prediction_filename("DANNCE", prediction_path),
        )
        m = loadmat(path)
        n_frames = m["pred"].shape[0]
        n_joints = m["pred"].shape[3]
    else:
        raise HTTPException(500, f"Unsupported prediciton mode:{mode}")

    return PredictionMetadata(n_joints=n_joints, n_frames=n_frames)
