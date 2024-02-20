from dataclasses import dataclass

import cv2
import numpy as np
import matplotlib.pyplot as plt


@dataclass(frozen=True)
class VideoFileStats:
    """Video file information"""

    n_frames: int
    width: int
    height: int
    n_channels: int

    def __repr__(self) -> str:
        return f"VideoInfo <\n  n_frames: {self.n_frames}\n  (width, height): ({self.width}, {self.height})\n>"


def get_video_stats(video_path: str):
    """
    Return stats given a video file
    E.g. n_farmes, width, height, n_channels
    """
    vcap = cv2.VideoCapture(video_path)
    n_frames = int(vcap.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(vcap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(vcap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    # always 3 channels for video
    n_channels = 3
    vcap.release()
    stats = VideoFileStats(
        n_frames=n_frames, width=width, height=height, n_channels=n_channels
    )
    return stats


def get_first_frame_video(video_path: str):
    """Returns a cv2 image from the first frame of a video, specified by path"""
    vcap = cv2.VideoCapture(video_path)
    success, image = vcap.read()
    vcap.release()
    if not success:
        raise Exception(f"Failed to read video at {video_path}")
    return image


def get_chessboard_coordinates(
    chessboard_rows: int, chessboard_cols: int, square_size_mm: float
) -> np.ndarray:
    """Return chessboard internal vertex coordinates for calibration.
    Assume that the origin of the chessboard is (0,0,0).

    Rows are y-coordinate
    Columns are the x-coordinate.
    Assume z is zero for chessboard plane.

    Returns a numpy array in the shape (#rows * #cols, 3), scaled by square_size_mm.

    E.g. np.ndarray(
        [0,0,0],
        [1,0,0],
        ...
        [5,0,0],
        [0,1,0],
        ...
        [5,8,0]
    )

    Args:
        square_size_mm: size of each square in mm
        chessboard_rows: number of rows of internal verticies in the chessboard (1 - # squares in a row)
        chessboard_cols: number of columns of internal verticies in the chessboard (1 - # squares in a columns)
    """
    x = np.repeat(np.arange(0, chessboard_rows), chessboard_cols)  # [a a b b c c ...]
    y = np.tile(np.arange(0, chessboard_cols), chessboard_rows)  # [a b c ... a b c ...]
    z = np.zeros(chessboard_rows * chessboard_cols)

    # Note: col_stack(y,x,...) instead of col_stack(x,y...) means that the returning list will increase the first
    # dimension first, then the second, etc. Shouldn't make a difference, but maintains consistency with old cal.py code
    return np.column_stack((y, x, z)).astype(np.float32) * square_size_mm


# helper funciton to quickly show an image
def imshow(img, scale=1):
    (h, w) = img.shape[0:2]
    aspect = w / h
    default_w = 6.4  # inches
    w2 = scale * default_w
    h2 = scale * default_w / aspect
    figsize = (w2, h2)
    _f = plt.figure(figsize=figsize)

    if len(img.shape) > 2:
        img_bgr = img
        img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
        plt.imshow(img_rgb)
    elif np.min(img) == 0 and np.max(img) == 1:
        # binary image
        img_binary = img
        plt.imshow(img_binary, cmap="gray", vmin=0, vmax=1)
    else:
        # grayscale image
        img_gray = img
        plt.imshow(img_gray, cmap="gray", vmin=0, vmax=255)


def imshow_cv2(img, timeout=5000):
    cv2.imshow("img", img)
    cv2.waitKey(timeout)
    cv2.destroyAllWindows()
    cv2.waitKey(1)
