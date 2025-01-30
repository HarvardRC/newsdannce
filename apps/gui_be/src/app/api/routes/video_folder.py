"""
/video_folder
"""

from pathlib import Path
import sqlite3
from typing import Any
from fastapi import APIRouter, HTTPException, Header, Response
from fastapi.responses import FileResponse
from app.api.deps import SessionDep
from app.core.db import (
    TABLE_GPU_JOB,
    TABLE_PREDICT_JOB,
    TABLE_PREDICTION,
    TABLE_VIDEO_FOLDER,
)
from app.models import  ImportVideoFoldersModel

from app.utils.dannce_mat_processing import (
    get_labeled_data_in_dir,
)
from app.utils.video import get_one_frame

from app.core.config import settings
from app.base_logger import logger
from app.utils.video_processing import check_video_folder_source_not_exists, check_video_folder_already_imported
import taskqueue.video
from app.utils.helpers import make_resource_name

router = APIRouter()


@router.get("/list")
def list_all_video_folder(conn: SessionDep):
    rows = conn.execute(
        f"""
SELECT
    t1.name,
    t1.id,
    t1.path,
    t1.com_labels_file,
    t1.dannce_labels_file,
    t1.current_com_prediction,
    t2.name AS current_com_prediction_name,
    t1.created_at,
    t1.status AS status
FROM {TABLE_VIDEO_FOLDER} t1
LEFT JOIN {TABLE_PREDICTION} t2
    ON t1.current_com_prediction = t2.id
"""
    ).fetchall()
    rows = [dict(x) for x in rows]
    return rows


@router.post("/import_from_paths")
def import_video_folders_route(conn: SessionDep, data: ImportVideoFoldersModel):
    """
    Queue task to import video folder.
    Checks if video folder is likely valid before queueing; checks if there is another resource with same source id.
    Create a "PENDING" entry in the VIDEO_FOLDER table if initial checks passed.
    """
    curr = conn.cursor()
    for video_folder_path in data.paths:
        video_folder_path_src = Path(video_folder_path)

        # 1. before queueing check if folder actually exists or is likely valid
        if check_video_folder_source_not_exists(video_folder_path_src):
            logger.warning(f"Tried to import video folder {video_folder_path_src}, but the folder does not appear to be valid")
            raise HTTPException(400, f"Video folder: {video_folder_path_src} does not appear to exist")

        # 2. check if the folder has already been imported
        if check_video_folder_already_imported(conn, video_folder_path_src):
            logger.warning("Video folder has already been imported and added to db")
            raise HTTPException(400, f"Video folder with src: {video_folder_path_src} has already been imported")


        # 3. make the dest folder
        resource_path = make_resource_name()
        logger.info(f"Importing video folder: {video_folder_path_src}")
        video_folder_path_dest = Path(settings.VIDEO_FOLDERS_FOLDER ,resource_path)
        video_folder_path_dest.mkdir(mode=0o777,parents=True, exist_ok=False)
        logger.info(f"Created new dest folder: {video_folder_path_dest}")
        video_folder_path_dest.joinpath("metadata.txt").write_text(f"src: {video_folder_path_src}")

        # 4. insert PENDING entry into video_folder table
        curr.execute(
            f"INSERT INTO {TABLE_VIDEO_FOLDER} (status, name, path, src_path) VALUES ('PENDING',?,?,?)",
            (
                video_folder_path_src.name, # name
                resource_path, # [dest] path
                str(video_folder_path_src), # src path
            )
        )
        rowid = curr.lastrowid # id of the imported video_folder
        curr.execute("COMMIT")

        logger.info(f"QUEUEING video folder with id: {rowid}")
        taskqueue.video.import_video_folder_worker.delay(rowid)

    logger.info("TRYING TO IMPORT FROM PATHS")


@router.get("/{id}/frame")
def get_frame_route(
    conn: SessionDep,
    id: int,
    frame_index: int,
    camera_name: str,
) -> Any:
    row = conn.execute(
        f"SELECT * FROM {TABLE_VIDEO_FOLDER} WHERE ID=?", (id,)
    ).fetchone()
    if not row:
        raise HTTPException(status_code=404)

    row = dict(row)
    video_path = Path(row["path"], "videos", camera_name, "0.mp4")
    if not video_path.exists():
        raise HTTPException(404, "Video does not exist")

    out_filename = make_resource_name(f"frame_{id}_{frame_index}_{camera_name}_", ".png")

    try:
        get_one_frame(
            video_path=video_path, frame_index=frame_index, output_name=out_filename
        )
    except Exception as e:
        raise HTTPException(400, f"Unable to extract frame from video {e}")

    return FileResponse(out_filename, status_code=200)


@router.get("/{id}")
def get_video_folder_details(
    conn: SessionDep,
    id: int,
) -> Any:
    row = conn.execute(
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
            t1.status AS status,
            t2.name AS current_com_prediction_name
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
    return_dict["name"] = row["name"]
    return_dict["path"] = row["path"]
    return_dict['status'] = row['status']
    return_dict["src_path"] = row["src_path"]
    return_dict["com_labels_file"] = row["com_labels_file"]
    return_dict["dannce_labels_file"] = (row["dannce_labels_file"],)
    return_dict["current_com_prediction_id"] = row["current_com_prediction_id"]
    return_dict["camera_names"] = row["camera_names"]
    return_dict["video_width"] = row["video_width"]
    return_dict["video_height"] = row["video_height"]
    return_dict["n_cameras"] = row["n_cameras"]
    return_dict["n_animals"] = row["n_animals"]
    return_dict["n_frames"] = row["n_frames"]
    return_dict["duration_s"] = row["duration_s"]
    return_dict["fps"] = row["fps"]
    return_dict["created_at"] = row["created_at"]
    return_dict["current_com_prediction_name"] = row["current_com_prediction_name"]

    # derived data
    return_dict["path_external"] = Path(
        settings.VIDEO_FOLDERS_FOLDER_EXTERNAL, return_dict["path"]
    )
    return_dict["path_internal"] = Path(
        settings.VIDEO_FOLDERS_FOLDER, return_dict["path"]
    )

    label_data = get_labeled_data_in_dir(id, return_dict["path"])

    # Exclude label file params: do not need to return to user
    label_data = [x.without_params() for x in label_data]

    return_dict["label_files"] = label_data

    # get predictions involving this video folder
    row_predictions = conn.execute(
        f"""
SELECT
    id, name, status, mode, created_at
FROM
    {TABLE_PREDICTION}
WHERE
    video_folder = ?
ORDER BY
    created_at DESC
        """,
        (id,),
    )
    row_predictions = [dict(x) for x in row_predictions]
    return_dict["prediction_data"] = row_predictions

    # get predct jobs (e.g. slurm/local jobs) involving this video folder
    row_predict_job = conn.execute(
        f"""
SELECT
    *
FROM
    {TABLE_PREDICT_JOB} t1
LEFT JOIN
    {TABLE_GPU_JOB} t2
ON t1.gpu_job = t2.id
WHERE video_folder = ?
""",
        (id,),
    ).fetchmany()
    row_predict_job = [dict(x) for x in row_predict_job]

    return_dict["predict_jobs"] = row_predict_job

    return return_dict


CHUNK_SIZE = 4 * 1024 * 1024


@router.get("/{id}/stream")
def stream_video(
    conn: SessionDep, id: int, camera_name: str, range: str = Header(None)
) -> Any:
    logger.info(f"Video folder preview {id}")
    row = conn.execute(
        f"SELECT * FROM {TABLE_VIDEO_FOLDER} WHERE ID=?", (id,)
    ).fetchone()

    if not row:
        raise HTTPException(status_code=404)

    row = dict(row)
    video_path = Path(
        settings.VIDEO_FOLDERS_FOLDER, row["path"], "videos", camera_name, "0.mp4"
    )

    if not video_path.exists():
        raise HTTPException(
            status_code=404, detail="Cannot locate file on local machine"
        )

    start, end = range.replace("bytes=", "").split("-")
    start = int(start)
    end = int(end) if end else start + CHUNK_SIZE

    with open(video_path, "rb") as video:
        video.seek(start)
        data = video.read(end - start)
        filesize = str(video_path.stat().st_size)
        headers = {
            "Content-Range": f"bytes {str(start)}-{str(end)}/{filesize}",
            "Accept-Ranges": "bytes",
        }
        return Response(data, status_code=206, headers=headers, media_type="video/mp4")


@router.delete("/{id}")
def delete_video_folder_route(
    conn: SessionDep,
    id: int,
) -> Any:
    logger.info(f"Delete video folder: {id}")
    try:
        conn.execute(f"DELETE FROM {TABLE_VIDEO_FOLDER} WHERE id=?", (id,))
    except sqlite3.IntegrityError:
        return {
            "Result": "error",
            "Message": "Delete dependent video predictions first",
        }

    return {"Result": "success"}
