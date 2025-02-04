"""
/prediction
"""
from fastapi import APIRouter, HTTPException
from pathlib import Path, PurePath

from app.api.deps import SessionDep
from app.core.db import TABLE_PREDICTION, TABLE_VIDEO_FOLDER
from app.models import MakePredictionPreviewModel
from app.utils.dannce_mat_processing import (
    get_com_pred_data_3d,
    get_dannce_pred_data_3d,
)
from app.utils.video import get_one_frame
from app.core.config import settings
from caldannce.calibration_data import CameraParams
from app.base_logger import logger
from app.utils.predictions import get_com_deltas, get_com_prediction_file, get_prediction_filename, get_prediction_metadata
import scipy.io

router = APIRouter()


@router.post("/{id_str}/make_preview")
def make_preview_route(
    conn: SessionDep, data: MakePredictionPreviewModel, id_str: str
):
    if len(data.frames) > 10 or len(data.frames) < 1:
        raise HTTPException(400, "Can fetch between 1-10 frames for preview")
    id = int(id_str)
    row = conn.execute(
        f"""
SELECT
    t1.path AS prediction_path,
    t1.video_folder AS video_folder_id,
    t1.mode AS mode,
    t2.path AS video_folder_path,
    t2.calibration_params AS calibration_params
FROM {TABLE_PREDICTION} t1
LEFT JOIN {TABLE_VIDEO_FOLDER} t2
    ON t1.video_folder = t2.id
WHERE t1.id=?
""",
        (id,),
    ).fetchone()
    row = dict(row)

    mode = row["mode"]  # COM | DANNCE | SDANNCE
    calibration_params = CameraParams.load_list_from_json_string(
        row["calibration_params"]
    )
    cam1_params = calibration_params[0]
    cam2_params = calibration_params[1]

    prediction_path = row['prediction_path']
    video_folder_id = row["video_folder_id"]
    video_folder_path = Path(settings.VIDEO_FOLDERS_FOLDER, row["video_folder_path"])
    logger.info(f"PREDICTION PATH {prediction_path}")

    frame_info = []

    if mode == "COM":
        com3d_filename = get_prediction_filename('COM', prediction_path)
        com3d_file = Path(settings.PREDICTIONS_FOLDER, prediction_path, com3d_filename)
        pred_3d = get_com_pred_data_3d(com3d_file, data.frames)
    elif mode == "DANNCE":
        dannce3d_filename = get_prediction_filename('DANNCE', prediction_path)
        dannce3d_file = Path(settings.PREDICTIONS_FOLDER, prediction_path, dannce3d_filename)
        pred_3d = get_dannce_pred_data_3d(dannce3d_file, data.frames)
    else:
        raise Exception("Prediction is unsupported")

    # pred_3d: N_FRAMES, N_JOINTS, N_DIMS[3]
    n_joints = pred_3d.shape[1]
    n_frames = len(data.frames)

    pred_3d_unrolled = pred_3d.reshape(n_joints * n_frames, 3)

    im_cam1_unrolled = cam1_params.project_multiple_world_points(pred_3d_unrolled)
    im_cam2_unrolled = cam2_params.project_multiple_world_points(pred_3d_unrolled)
    im_cam1 = im_cam1_unrolled.reshape(n_frames, n_joints, 2)
    im_cam2 = im_cam2_unrolled.reshape(n_frames, n_joints, 2)

    for frame_idx, f in enumerate(data.frames):
        # SLOW STEP TO EXTRACT SINGLE FRAME
        frame_image_file_1 = get_one_frame(
            Path(video_folder_path, "videos", data.camera_name_1, "0.mp4"), f
        )
        frame_image_file_2 = get_one_frame(
            Path(video_folder_path, "videos", data.camera_name_2, "0.mp4"), f
        )
        frame_info.append(
            {
                "absolute_frameno": data.frames[frame_idx],
                "frame_idx": frame_idx,
                # "filename_cam1": frame_image_file_1,
                "static_url_cam1": f"{settings.FRONTEND_STATIC_URL}/{frame_image_file_1}",
                "pts_cam1": im_cam1[frame_idx, :, :].tolist(),
                # "filename_cam2": frame_image_file_2,
                "static_url_cam2": f"{settings.FRONTEND_STATIC_URL}/{frame_image_file_2}",
                "pts_cam2": im_cam2[frame_idx, :, :].tolist(),
            }
        )

    skeleton_data = None
    if (mode != 'COM' and settings.SKELETON_FILE.exists()):
        m = scipy.io.loadmat(settings.SKELETON_FILE)
        joint_names = [x[0] for x in m['joint_names'][0]]
        joints_idx = m['joints_idx'].tolist()
        skeleton_data = {
            'joint_names' : joint_names,
            'joints_idx' : joints_idx
        }


    return {
        "frames": frame_info,
        "n_frames": n_frames,
        "frame_width": 1920,
        "frame_height": 1200,
        "n_joints": n_joints,
        "skeleton_data": skeleton_data
    }


@router.get("/list")
def list_all_predictions_route(conn: SessionDep):
    rows = conn.execute(
        f"""
SELECT
    id AS prediction_id,
    name AS prediction_name,
    path AS prediction_path,
    status,
    video_folder AS video_folder_id,
    mode,
    created_at
FROM {TABLE_PREDICTION}"""
    ).fetchall()
    rows = [dict(x) for x in rows]
    return rows


@router.get("/{id_str}/com_preview")
def get_com_preview_route(conn: SessionDep,id_str: str,  samples:int ):
    id_int = int(id_str)
    return get_com_prediction_file(conn, id_int, samples)

@router.get("/{id_str}/com_histogram")
def get_com_histogram_route(conn: SessionDep, id_str: str,  ):
    id_int = int(id_str)
    return get_com_deltas(conn, id_int)


@router.get("/{id}")
def get_prediction_details_route(conn: SessionDep, id: str):
    id_int = int(id)
    row = conn.execute(
        f"""
SELECT
    name AS prediction_name,
    path AS prediction_path,
    status AS status,
    video_folder AS video_folder_id,
    filepath AS filepath,
    mode AS mode,
    created_at
FROM {TABLE_PREDICTION}
WHERE id=?
""",
        (id_int,),
    ).fetchone()
    if not row:
        raise HTTPException(404)

    row = dict(row)
    prediction_name = row['prediction_name']
    prediction_path = row['prediction_path']
    status = row['status']
    video_folder_id = row['video_folder_id']
    mode = row['mode']
    created_at = row ['created_at']

    metadata = get_prediction_metadata(status, mode, prediction_path)

    return {
        'prediction_path': row['prediction_path'],
        'path_external': PurePath(settings.PREDICTIONS_FOLDER_EXTERNAL, prediction_path, get_prediction_filename(mode, prediction_path)),
        'path_internal': PurePath(settings.PREDICTIONS_FOLDER, prediction_path, get_prediction_filename(mode, prediction_path)),
        'prediction_name': prediction_name,
        'status': status,
        'video_folder_id': video_folder_id,
        'mode': mode,
        'created_at': created_at,
        'n_joints': metadata.n_joints,
        'n_frames': metadata.n_frames,
        'filepath': row['filepath'],
    }

