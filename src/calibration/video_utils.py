# custom utilities/wrappers for handling media files (e.g. video & image)

import logging
from dataclasses import dataclass
from pathlib import Path

import cv2
import matplotlib.pyplot as plt
import numpy as np
from enum import Enum


class ImageFormat(Enum):
    CV2_BGR = "cv2_bgr"
    """OpenCV BGR (blue,green,red) image"""
    RGB = "rgb"
    """Standard RGB image (e.g. matplotlib, PIL)"""


@dataclass(frozen=True, slots=True, kw_only=True)
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
    E.g. n_frames, width, height, n_channels
    """
    vcap = cv2.VideoCapture(video_path)
    n_frames = int(vcap.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(vcap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(vcap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    # always 3 channels for video (B, R, G)
    n_channels = 3
    vcap.release()
    stats = VideoFileStats(
        n_frames=n_frames, width=width, height=height, n_channels=n_channels
    )
    return stats


def load_image(image_path) -> np.ndarray:
    this_img = cv2.imread(image_path)
    return this_img


def load_images(image_paths, image_width, image_height) -> np.ndarray:
    """Load a list of images with uniform width, height into a numpy array
    of dimension [n_images, height, width, 3]"""
    n_images = len(image_paths)
    # intitialize np array
    raw_images = np.zeros((n_images, image_height, image_width, 3), dtype=np.uint8)

    logging.info(f"Loading {n_images} into memory. May take a few seconds")
    for idx, img_filepath in enumerate(image_paths):
        this_img = cv2.imread(img_filepath)
        raw_images[idx] = this_img
    return raw_images


def get_first_frame_video(video_path: str):
    """Returns a cv2 image from the first frame of a video, specified by path"""
    vcap = cv2.VideoCapture(video_path)
    success, image = vcap.read()
    vcap.release()
    if not success:
        raise Exception(f"Failed to read video at {video_path}")
    return image


def load_image_or_video(media_path: str, output_image_format=ImageFormat.RGB):
    """If the media path is an image, load the image using cv2. If it is a video, load the first frame"""
    suffix = Path(media_path).suffix
    if suffix in [".mp4"]:
        img = get_first_frame_video(media_path)
    elif suffix in [".jpeg", ".jpg", ".bmp", ".tif", ".tiff", ".png"]:
        img = load_image(media_path)
    else:
        raise Exception(
            f"Image or video path suffix is not in the list of image or video file extensions: {suffix}"
        )
    # possibly convert BGR to RGB
    if output_image_format == ImageFormat.RGB:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    return img


# helper funciton to quickly show an image
def imshow(img, scale=1):
    """Helper function to show an image with matplotlib (works inline for jupyter)"""
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
    """Helper function to show an image as an OpenCV window"""
    cv2.imshow("img", img)
    cv2.waitKey(timeout)
    cv2.destroyAllWindows()
    cv2.waitKey(1)
