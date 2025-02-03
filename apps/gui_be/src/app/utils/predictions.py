from calendar import c
from dataclasses import dataclass
from pathlib import Path, PurePath
import sqlite3
from typing import Literal

from app.base_logger import logger
from fastapi import HTTPException
import numpy as np

from app.core.db import (
    TABLE_PREDICT_JOB,
    TABLE_PREDICTION,
    PredictionStatus,
)
from app.core.config import settings
from scipy.io import loadmat


def update_prediction_status_by_job_id(
    conn: sqlite3.Connection, predict_job_id: int, status: PredictionStatus
):
    logger.info(f"UPDATE PRED. STAT BY JOB ID: {predict_job_id}; Status value: {status.value}, status: {status}")
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

def get_com_prediction_file(conn: sqlite3.Connection, predict_job_id: int, samples: int, to_list= True):
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
""", (predict_job_id,)
    ).fetchone()

    if not row:
        raise HTTPException(404, "Prediction id not found")
    row = dict(row)

    path = row['path']
    status = row['status']
    mode = row['mode']

    if mode != 'COM':
        raise HTTPException(400, "Prediction id must reference a COM prediction (not DANNCE)")

    if status != 'COMPLETED':
        raise HTTPException(400, "Prediction must be completed. Not pending or failed.")

    pred_data_file= Path(settings.PREDICTIONS_FOLDER, path, 'com3d.mat')

    m = loadmat(pred_data_file)

    # Number of datapoints to return

    # shape: 90000x3
    com_data = m['com']
    if samples == -1:
        # return all samples
        frame_samples = np.arange(0,com_data.shape[0])
    else:
        frame_samples = np.linspace(0,com_data.shape[0]-1, samples).astype(np.int32)
    com_data = com_data[frame_samples]

    idxs = frame_samples.reshape(-1, 1)
    com_data = np.hstack([idxs, com_data])
    if to_list:
        return com_data.tolist()
    else:
        return com_data

def get_prediction_file_path(mode: Literal['COM','DANNCE','SDANNCE'], prediction_path:str, is_external:bool=False):
    base_folder = settings.PREDICTIONS_FOLDER_EXTERNAL if is_external else settings.PREDICTIONS_FOLDER

    if mode == "COM":
        return PurePath(base_folder, prediction_path, "com3d.mat")
    elif mode == "DANNCE":
        return PurePath(base_folder, prediction_path, "save_data_AVG0.mat")
    else:
        raise HTTPException("Invalid prediction path")


@dataclass
class COMDeltasData:
    hist: list[int]
    bin_edges: list[float]

def get_com_deltas(conn: sqlite3.Connection, predict_job_id: int):
    com_data = get_com_prediction_file(conn, predict_job_id=predict_job_id, samples=-1,to_list=False)
    subsequent_diffs = np.diff(com_data[:,1:4],axis=0)
    norms = np.linalg.norm(subsequent_diffs, axis=1)
    hist, bin_edges = np.histogram(norms, bins=15)
    return COMDeltasData(hist=hist.tolist(), bin_edges=bin_edges.tolist())

@dataclass
class PredictionMetadata:
    n_joints: int
    n_frames: int

def get_prediction_metadata(status, mode: Literal["COM","DANNCE","SDANNCE"], prediction_path: str) -> PredictionMetadata:

    if status != 'COMPLETED':
        n_joints= -1
        n_frames= -1
    elif mode == "COM":
        path = get_prediction_file_path(mode, prediction_path)
        m = loadmat(path)
        n_frames = m['com'].shape[0]
        n_joints = 1
    elif mode == "DANNCE":
        path = get_prediction_file_path(mode, prediction_path)
        m = loadmat(path)
        n_frames = m['pred'].shape[0]
        n_joints = m['pred'].shape[3]
    else:
        raise HTTPException(500, f"Unsupported prediciton mode:{mode}" )

    return PredictionMetadata(n_joints=n_joints, n_frames= n_frames)

