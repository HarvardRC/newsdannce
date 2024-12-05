from pathlib import Path
from .celery import app
import shutil
import subprocess
import logging


# @app.task
# def backup_video_folder(video_folder_path: str | Path):
#     p_videos_src = Path(video_folder_path, "videos")
#     p_videos_dst = Path(video_folder_path, "videos-backup")
#     shutil.copytree(p_videos_src, p_videos_dst)


@app.task
def reencode_video_folder(video_folder_path: str | Path, camnames: list[str]):
    """Update video folder with the changes:
    1. Fast-start (metadata at front)
    [NOT IMPLEMENTED] 2. Adds frame numbers to the to right corner of the video
    [NOT IMPLMENETED] 3. More frequent keyframes (e.g. 5 seconds -> 0.5 seconds)
    Should take ~5 mins to run.
    Saves to "videos-reencoded" folder.
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
            logging.warning(f"reencode_video_err: { output.stderr }")
            logging.warning(f"reencode_video_err: { output.stdout }")
            raise Exception(f"Unable to process video file:{vid_file}")


@app.task
@app.task
def add(x, y):
    return x + y


@app.task
def mul(x, y):
    return x * y
