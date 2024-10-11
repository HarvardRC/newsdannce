from dataclasses import dataclass
import sqlite3

from fastapi import HTTPException
from pydantic import BaseModel

from app.core.db import TABLE_VIDEO_FOLDER
from pathlib import Path


@dataclass
class VideoFolderComData:
    path: str
    com_labels_file: str


@dataclass
class VideoFolderDannceData:
    path: str
    dannce_labels_file: str


class ComExpEntry(BaseModel):
    label3d_file: Path


class DannceExpEntry(BaseModel):
    label3d_file: Path
    com_file: Path


def get_video_folders_for_com(
    conn: sqlite3.Connection, video_folder_ids: list[int]
) -> list[ComExpEntry]:
    question_string = ",".join(["?"] * len(video_folder_ids))
    rows = conn.execute(
        f"SELECT path, com_labels_file FROM {TABLE_VIDEO_FOLDER} WHERE id IN ({question_string})",
        video_folder_ids,
    ).fetchall()

    if len(rows) < len(video_folder_ids):
        raise Exception("Did not return all video folders requested for coms")
    rows = [dict(row) for row in rows]

    for row in rows:
        print("ROW IS ", row)

    rows = [
        ComExpEntry(label3d_file=Path(row["path"], row["com_labels_file"]))
        for row in rows
    ]

    return rows


def get_video_folder_path(conn: sqlite3.Connection, video_folder_id: int) -> list[Path]:
    row = conn.execute(
        f"SELECT path from {TABLE_VIDEO_FOLDER} WHERE id=?", (video_folder_id,)
    ).fetchone()
    if not row:
        raise HTTPException(400, f"Video folder for id {id} not found")
    path = Path(row["path"])
    return path
