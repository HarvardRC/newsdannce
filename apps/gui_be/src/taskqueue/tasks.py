from pathlib import Path
from app.core.db import get_db, get_db_context
from taskqueue.celery import celery_app
import subprocess
from app.base_logger import logger
import time


@celery_app.task
def reencode_video_folder(video_folder_path: str | Path, camnames: list[str]):
    """Update video folder with the changes:
    1. Fast-start (metadata at front)
    [NOT IMPLEMENTED] 2. Adds frame numbers to the to right corner of the video
    [NOT IMPLMENETED] 3. More frequent keyframes (e.g. 5 seconds -> 0.5 seconds)
    Should take ~5 mins to run.
    Saves to "videos-reencoded" folder.'
    """
    p = Path(video_folder_path)
    for camname in camnames:
        vid_file = p.joinpath("videos", camname, "0.mp4")
        p.joinpath("videos-reencoded", camname).mkdir(exist_ok=True)

        output = subprocess.run(
            [
                "ffmpeg",
                "-i",
                str(vid_file),
                "-c",
                "copy",
                "-map",
                "0",
                "-movflags",
                "+faststart",
                str(p.joinpath("videos-reencoded", camname, "0.mp4")),
            ],
            capture_output=True,
            text=True,
        )

        try:
            output.check_returncode()
        except subprocess.CalledProcessError:
            logger.warning(f"reencode_video_err: { output.stderr }")
            logger.warning(f"reencode_video_err: { output.stdout }")
            raise Exception(f"Unable to process video file:{vid_file}")


@celery_app.task
def submit_com_train(x, y):
    return x + y

@celery_app.task
def submit_dannce_train(x, y):
    return x * y

@celery_app.task
def submit_com_predict(x, y):
    return x * y


@celery_app.task
def submit_dannce_predict(x, y):
    return x * y


# periodic task to poll slurm
@celery_app.task
def task_refresh_job_list():
    from app.utils.job import refresh_job_list
    with get_db_context() as conn:
        _data = refresh_job_list(conn)
        logger.info(f"Data: {_data}")

        logger.info("Refreshed jobs list.")
