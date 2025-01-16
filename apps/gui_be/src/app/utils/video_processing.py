from dataclasses import dataclass
import subprocess
from pathlib import Path
import re
import json
import math
import shutil


def process_video_folder_faststart(video_folder_path, camera_names, backup_video=True):
    """Update video with the changes:
    1. Fast-start (metadata at front)
    [NOT IMPLEMENTED] 2. Adds frame numbers to the to right corner of the video
    [NOT IMPLMENETED] 3. More frequent keyframes (e.g. 5 seconds -> 0.5 seconds)
    Should be moderately fast to run (<5 sec) if just adding faststart (no re-encoding required)
    """
    p = Path(video_folder_path)
    for camname in camera_names:
        vid_file = p.joinpath("videos", camname, "0.mp4")

        output = subprocess.run(
            [
                "ffmpeg",
                "-i",
                str(vid_file),
                "-c",
                "copy",
                "-movflags",
                "+faststart",
                "-abort_on",
                "empty_output",
                str(p.joinpath("videos-reencoded", camname, "0.mp4")),
            ],
            capture_output=True,
            text=True,
        )

        try:
            output.check_returncode()
        except subprocess.CalledProcessError:
            raise Exception(f"Unable to process video file:{vid_file}")


#  example ffmpeg command to add frame numbers to top of video
# ffmpeg -i 0.mp4 -vf "drawtext=fontfile=Arial.ttf: text=%{n}: x=(w-tw): y=0: fontcolor=white: box=1: boxcolor=0x00000099" with-frames.mp4


@dataclass
class VideoStats:
    width: int
    height: int
    fps: float
    duration_s: float
    n_frames: int
    n_cameras: int
    camera_names: list[str]


def get_video_metadata(video_folder: str | Path):
    # get camera names/video folders:
    # first check the "videos" folder:
    p = Path(video_folder, "videos")

    # find all folders within "videos/" which contain at least one mp4
    camera_folder_names = {x.parent.name for x in p.glob("*/*.mp4")}
    camera_folder_names = sorted(camera_folder_names)

    vid0 = Path(video_folder, "videos", camera_folder_names[0], "0.mp4")

    # get stats for first video (assuming all videso are same size,duration,framerate)
    output = subprocess.run(
        (
            "ffprobe",
            "-v",
            "error",
            "-select_streams",
            "v",
            "-of",
            "json",
            "-show_entries",
            "stream=r_frame_rate,width,height,duration",
            str(vid0),
        ),
        capture_output=True,
        text=True,
    )

    data = json.loads(output.stdout)

    width = int(data["streams"][0]["width"])
    height = int(data["streams"][0]["height"])
    duration_s = float(data["streams"][0]["duration"])

    match_fps_fraction = re.match(r"(\d+)/(\d+)", data["streams"][0]["r_frame_rate"])
    fps_numerator = int(match_fps_fraction.group(1))
    fps_denominator = int(match_fps_fraction.group(2))
    fps = fps_numerator / fps_denominator
    n_frames = math.ceil(duration_s * fps)

    return VideoStats(
        width=width,
        height=height,
        duration_s=duration_s,
        fps=fps,
        n_frames=n_frames,
        n_cameras=len(camera_folder_names),
        camera_names=camera_folder_names,
    )
    # ffprobe -v error -select_streams v -of json -show_entries stream=r_frame_rate,width,height,duration 0.mp4
