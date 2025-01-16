from pydantic_settings import BaseSettings
from pathlib import Path
import os
from app.base_logger import logger

# env variables (*MUST* be defined)
ENV_INSTANCE_DIR = os.environ.get("INSTANCE_DIR")
ENV_TMP_DIR = os.environ.get("TMP_DIR")
ENV_APP_SRC_DIR = os.environ.get("APP_SRC_DIR")
ENV_APP_RESOURCES_DIR = os.environ.get("APP_RESOURCES_DIR")
ENV_REACT_APP_DIST_FOLDER = os.environ.get("REACT_APP_DIST_FOLDER")
ENV_SERVER_BASE_URL = os.environ.get("SERVER_BASE_URL")
ENV_API_BASE_URL = os.environ.get("API_BASE_URL")
ENV_REACT_APP_BASE_URL = os.environ.get("REACT_APP_BASE_URL")
ENV_SDANNCE_SINGULARITY_IMG_PATH = os.environ.get("SDANNCE_SINGULARITY_IMG_PATH")
ENV_CELERY_BEAT_FILES = os.environ.get("CELERY_BEAT_FILES")

ENV_BASE_MOUNT= os.environ.get("BASE_MOUNT")

# slurm env variables (*MAY* be undefined)
ENV_SLURM_NODELIST = os.environ.get("SLURM_NODELIST", "")

class _Settings(BaseSettings):
    SQL_FOLDER: Path = Path(ENV_APP_RESOURCES_DIR, "sql")
    INIT_SQL_FILE: Path = Path(SQL_FOLDER, "schema.sql")

    DATA_FOLDER: Path = Path(ENV_INSTANCE_DIR)
    # Links relative to DATA FOLDER
    DB_FILE: Path = Path(DATA_FOLDER, "db.sqlite3")
    SLURM_TRAIN_FOLDER: Path = Path(DATA_FOLDER, "slurm-cwd")
    SBATCH_DEBUG_FOLDER: Path = Path(DATA_FOLDER, "sbatch-debug")

    # SQLITE BACKING DATA
    WEIGHTS_FOLDER: Path = Path(DATA_FOLDER, "weights")
    PREDICTIONS_FOLDER: Path = Path(DATA_FOLDER, "predictions")
    VIDEO_FOLDERS_FOLDER: Path = Path(DATA_FOLDER, "video_folders")

    CONFIGS_FOLDER: Path = Path(DATA_FOLDER, "configs")
    LOGS_FOLDER: Path = Path(DATA_FOLDER, "logs")
    CELERY_BEAT_FILES: Path = Path(ENV_CELERY_BEAT_FILES)
    LOGS_FOLDER_EXTERNAL: Path = Path(ENV_BASE_MOUNT, "slurm-logs")

    STATIC_TMP_FOLDER: Path = Path(DATA_FOLDER, "static-tmp")
    """A folder to store temporary server resources E.g. generated images, etc."""

    # name of slurm node the backend is running on
    NODE_NAME: str = ENV_SLURM_NODELIST
    # proxy url for webserver

    REACT_APP_BASE_URL: str = ENV_REACT_APP_BASE_URL
    SERVER_BASE_URL: str = ENV_SERVER_BASE_URL
    API_BASE_URL: str = ENV_API_BASE_URL
    FRONTEND_STATIC_URL: str = f"{ENV_SERVER_BASE_URL}/static"

    REACT_APP_DIST_FOLDER: Path = ENV_REACT_APP_DIST_FOLDER

    N_CAMERAS: int = 6

    # Singularity container with sdannce image
    SDANNCE_IMAGE_PATH: Path = Path(ENV_SDANNCE_SINGULARITY_IMG_PATH)

    logger.info(f"USING INSTANCE DATA FOLDER AT: {DATA_FOLDER}")

settings = _Settings()
