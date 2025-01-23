from pathlib import Path
import sqlite3
from typing import Any
import uuid
from fastapi import APIRouter, HTTPException, Header, Response
from fastapi.responses import FileResponse
from app.api.deps import SessionDep
from app.core.db import (
    TABLE_PREDICT_JOB,
    TABLE_PREDICTION,
    TABLE_SLURM_JOB,
    TABLE_VIDEO_FOLDER,
)
from app.models import CreateVideoFolderModel, ImportVideoFoldersModel

from app.utils.dannce_mat_processing import (
    get_labeled_data_in_dir,
)
from app.utils.video import get_one_frame
# from app.utils.video_folders import import_video_folders_from_paths
from app.core.config import settings
import subprocess
from app.base_logger import logger
import taskqueue.video


router = APIRouter()


@router.get("/list")
def list_all_video_folder(session: SessionDep):
    rows = session.execute(
        f"""
SELECT
    t1.name,
    t1.id,
    t1.path,
    t1.com_labels_file,
    t1.dannce_labels_file,
    t1.current_com_prediction,
    t2.name as current_com_prediction_name,
    t1.created_at
FROM {TABLE_VIDEO_FOLDER} t1
LEFT JOIN {TABLE_PREDICTION} t2
    ON t1.current_com_prediction = t2.id

"""
    ).fetchall()
    rows = [dict(x) for x in rows]
    return rows


@router.post("/")
def create_video_folder(data: CreateVideoFolderModel, session: SessionDep) -> Any:
    curr = session.cursor()
    curr.execute(
        f"INSERT INTO {TABLE_VIDEO_FOLDER} (name, path) VALUES (?,?)",
        (data.name, data.path),
    )
    insert_id = curr.lastrowid
    session.commit()

    return {"id": insert_id}


@router.post("/import_from_paths")
def import_video_folders_route(session: SessionDep, data: ImportVideoFoldersModel):
    logger.info("TRYING TO IMPORT FROM PATHS")
    for path in data.paths:
        taskqueue.video.import_video_folder_worker.delay(path)
    # return import_video_folders_from_paths(session, data)


@router.get("/{id}/frame")
def get_frame_route(
    id: int, frame_index: int, camera_name: str, session: SessionDep
) -> Any:
    row = session.execute(
        f"SELECT * FROM {TABLE_VIDEO_FOLDER} WHERE ID=?", (id,)
    ).fetchone()
    if not row:
        raise HTTPException(status_code=404)

    row = dict(row)
    video_path = Path(row["path"], "videos", camera_name, "0.mp4")
    if not video_path.exists():
        raise HTTPException(404, "Video does not exist")

    out_filename = f"frame_{id}_{frame_index}_{camera_name}-{uuid.uuid4().hex}.png"

    try:
        get_one_frame(
            video_path=video_path, frame_index=frame_index, output_name=out_filename
        )
    except Exception as e:
        raise HTTPException(400, f"Unable to extract frame from video {e}")

    return FileResponse(out_filename, status_code=200)


@router.get("/{id}/preview")
def get_preview_route(id: int, camera_name: str, session: SessionDep) -> Any:
    logger.info(f"Video folder preview {id}")
    row = session.execute(
        f"SELECT * FROM {TABLE_VIDEO_FOLDER} WHERE ID=?", (id,)
    ).fetchone()
    if not row:
        raise HTTPException(status_code=404)

    row = dict(row)
    video_path = Path(row["path"], "videos", camera_name, "0.mp4")
    if not video_path.exists():
        raise HTTPException(404, "Video does not exist")

    out_filename = f"preview_{id}_{camera_name}-{uuid.uuid4().hex}.mp4"
    out_path = Path(settings.STATIC_TMP_FOLDER, out_filename).resolve()

    # 50 FPS = 0.02 Sec/Frame = 20ms/frame
    # timestamp = f"{frame_index*20}ms"
    max_time = "5s"

    # With FAST SEEKING
    output = subprocess.run(
        [
            "ffmpeg",
            "-ss",
            "00:00:00.00",
            "-i",
            str(video_path),
            "-an",  # disable audio processing
            "-t",
            max_time,
            "-abort_on",
            "empty_output",
            str(out_path),  # output path
        ],
        capture_output=True,
        text=True,
    )

    logger.warning(f"SUB OUT:{output.stdout}")

    logger.warning(f"SUB ERR:{output.stderr}")

    try:
        output.check_returncode()
    except subprocess.CalledProcessError:
        raise HTTPException(
            400, "FFMPEG frame extraction failed. Perhaps the frame number is invalid?"
        )
    # return {"path": str(out_path)}
    return FileResponse(out_path, status_code=200)


@router.get("/{id}")
def get_video_folder_details(id: int, session: SessionDep) -> Any:
    row = session.execute(
        f"""
        SELECT
            t1.id AS id,
            t1.name AS name,
            t1.path AS path,
            t1.src_path AS src_path,
            t1.com_labels_file AS com_labels_file,
            t1.dannce_labels_file AS dannce_labels_file,
            t1.current_com_prediction AS current_com_prediction_id,
            t1.camera_names AS camera_names,
            t1.video_width AS video_width,
            t1.video_height AS video_height,
            t1.n_cameras AS n_cameras,
            t1.n_animals AS n_animals,
            t1.n_frames AS n_frames,
            t1.duration_s AS duration_s,
            t1.fps AS fps,
            t1.created_at AS created_at,
            t2.name as current_com_prediction_name
        FROM {TABLE_VIDEO_FOLDER} t1
        LEFT JOIN {TABLE_PREDICTION} t2
        ON t1.current_com_prediction = t2.id
        WHERE t1.id=?""",
        (id,),
    ).fetchone()
    if not row:
        raise HTTPException(status_code=404)
    row = dict(row)

    # return_dict = dict(row_video_folder)
    return_dict = {}
    return_dict['name'] = row['name']
    return_dict['path'] = row['path']
    return_dict['src_path'] = row['src_path']
    return_dict['com_labels_file'] = row['com_labels_file']
    return_dict['dannce_labels_file'] = row['dannce_labels_file'],
    return_dict['current_com_prediction_id'] = row['current_com_prediction_id']
    return_dict['camera_names'] = row['camera_names']
    return_dict['video_width'] = row['video_width']
    return_dict['video_height'] = row['video_height']
    return_dict['n_cameras'] = row['n_cameras']
    return_dict['n_animals'] = row['n_animals']
    return_dict['n_frames'] = row['n_frames']
    return_dict['duration_s'] = row['duration_s']
    return_dict['fps'] = row['fps']
    return_dict['created_at'] = row['created_at']
    return_dict['current_com_prediction_name'] = row['current_com_prediction_name']

    # derived data
    return_dict['path_external'] = Path(settings.VIDEO_FOLDERS_FOLDER_EXTERNAL, return_dict['path'])
    return_dict['path_internal'] = Path(settings.VIDEO_FOLDERS_FOLDER, return_dict['path'])


    label_data = get_labeled_data_in_dir(id, return_dict["path"])

    # Exclude label file params: do not need to return to user
    label_data = [x.without_params() for x in label_data]

    return_dict["label_files"] = label_data

    # get predictions involving this video folder
    row_predictions = session.execute(
        f"""
SELECT
    id,name, status, mode, created_at
FROM
    {TABLE_PREDICTION}
WHERE
    video_folder=?
ORDER BY
    created_at DESC
        """,
        (id,),
    )
    row_predictions = [dict(x) for x in row_predictions]
    return_dict["prediction_data"] = row_predictions

    # get predct jobs (e.g. slurm/local jobs) involving this video folder
    row_predict_job = session.execute(
        f"""
SELECT
    *
FROM
    {TABLE_PREDICT_JOB} t1
LEFT JOIN
    {TABLE_SLURM_JOB} t2
ON t1.slurm_job = t2.slurm_job_id
WHERE video_folder=?""",
        (id,),
    ).fetchmany()
    row_predict_job = [dict(x) for x in row_predict_job]

    return_dict["predict_jobs"] = row_predict_job

    return return_dict


CHUNK_SIZE=4*1024*1024

@router.get("/{id}/stream")
def stream_video(id: int, camera_name: str, session: SessionDep, range: str=Header(None)) -> Any:
    logger.info(f"Video folder preview {id}")
    row = session.execute(
        f"SELECT * FROM {TABLE_VIDEO_FOLDER} WHERE ID=?", (id,)
    ).fetchone()

    if not row:
        raise HTTPException(status_code=404)

    row = dict(row)
    video_path = Path(settings.VIDEO_FOLDERS_FOLDER, row["path"], "videos", camera_name, "0.mp4")


    if not video_path.exists():
        raise HTTPException(status_code=404, detail="Cannot locate file on local machine")

    start,end = range.replace("bytes=", "").split("-")
    start = int(start)
    end = int(end) if end else start + CHUNK_SIZE

    with open(video_path, "rb") as video:
        video.seek(start)
        data = video.read(end-start)
        filesize= str(video_path.stat().st_size)
        headers = {
            'Content-Range': f'bytes {str(start)}-{str(end)}/{filesize}',
            'Accept-Ranges': 'bytes'
        }
        return Response(data, status_code=206, headers=headers, media_type="video/mp4")

    # out_filename = f"preview_{id}_{camera_name}-{uuid.uuid4().hex}.mp4"
    # out_path = Path(settings.STATIC_TMP_FOLDER, out_filename).resolve()

    # 50 FPS = 0.02 Sec/Frame = 20ms/frame
    # timestamp = f"{frame_index*20}ms"
    # max_time = "5s"

    # With FAST SEEKING
    # output = subprocess.run(
    #     [
    #         "ffmpeg",
    #         "-ss",
    #         "00:00:00.00",
    #         "-i",
    #         str(video_path),
    #         "-an",  # disable audio processing
    #         "-t",
    #         max_time,
    #         "-abort_on",
    #         "empty_output",
    #         str(out_path),  # output path
    #     ],
    #     capture_output=True,
    #     text=True,
    # )
    # ffmpeg -accurate_seek -ss 0.00 -i "/net/holy-nfsisilon/ifs/rc_labs/olveczky_lab_tier1/Lab/dannce_rig2/data/M1-M7_photometry/Alone/Day2_wk2/240625_143814_M5/videos/Camera1/0.mp4" -frames:v 1 instance_data/tmp/out

    # logger.warning(f"SUB OUT:{output.stdout}")

    # logger.warning(f"SUB ERR:{output.stderr}")

    # logging.warning(f"SUB CODE:{output.returncode}")
    # try:
    #     output.check_returncode()
    # except subprocess.CalledProcessError:
    #     raise HTTPException(
    #         400, "FFMPEG frame extraction failed. Perhaps the frame number is invalid?"
    #     )
    # # return {"path": str(out_path)}
    # return FileResponse(out_path, status_code=200)

@router.delete("/{id}")
def delete_video_folder_route(id: int, session: SessionDep)-> Any:
    logger.info(f"Delete video folder: {id}")
    try:
        session.execute(
            f"DELETE FROM {TABLE_VIDEO_FOLDER} WHERE id=?", (id,)
        )
    except sqlite3.IntegrityError:
        return {"Result": "error", "Message": "Delete dependent video predictions first"}

    return {"Result": "success"}
