from pydantic_settings import BaseSettings
from pathlib import Path, PurePath, PurePosixPath
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

# optional env variables (*MAY* be undefined)
ENV_SLURM_NODELIST = os.environ.get("SLURM_NODELIST", "")
ENV_MAX_CONCURRENT_LOCAL_JOBS = int(os.environ.get("MAX_CONCURRENT_LOCAL_JOBS", 0))

class _Settings(BaseSettings):
    SQL_FOLDER: Path = Path(ENV_APP_RESOURCES_DIR, "sql")
    INIT_SQL_FILE: Path = Path(SQL_FOLDER, "schema.sql")

    DATA_FOLDER: Path = Path(ENV_INSTANCE_DIR)
    # Links relative to DATA FOLDER
    DB_FILE: Path = Path(DATA_FOLDER, "db.sqlite3")
    SLURM_TRAIN_FOLDER: Path = Path(DATA_FOLDER, "slurm-cwd")
    SBATCH_DEBUG_FOLDER: Path = Path(DATA_FOLDER, "sbatch-debug")

    # INTERNAL VERSIONS OF RESOURCE DATA
    # these are the paths within the container (at their mount locations)
    WEIGHTS_FOLDER: Path = Path(DATA_FOLDER, "weights")
    PREDICTIONS_FOLDER: Path = Path(DATA_FOLDER, "predictions")
    VIDEO_FOLDERS_FOLDER: Path = Path(DATA_FOLDER, "video_folders")
    CONFIGS_FOLDER: Path = Path(DATA_FOLDER, "configs")
    LOGS_FOLDER: Path = Path(DATA_FOLDER, "logs")
    # misc. resources e.g. uploaded skeleton files
    RESOURCES_FOLDER: Path = Path(DATA_FOLDER, "resources")

    # EXTERNAL VERSIONS OF RESOURCE DATA
    # e.g. full path to the resource on the host system instead of container
    # code in container MAY NOT have access to these files
    # Use these when calling Slurm or displaying a resource path to the user
    DATA_FOLDER_EXTERNAL: PurePath = PurePosixPath(ENV_BASE_MOUNT, 'instance' )
    WEIGHTS_FOLDER_EXTERNAL: PurePath = PurePosixPath(DATA_FOLDER_EXTERNAL, "weights")
    PREDICTIONS_FOLDER_EXTERNAL: PurePath = PurePosixPath(DATA_FOLDER_EXTERNAL, "predictions")
    VIDEO_FOLDERS_FOLDER_EXTERNAL: PurePath = PurePosixPath(DATA_FOLDER_EXTERNAL, "video_folders")
    CONFIGS_FOLDER_EXTERNAL: PurePath = PurePosixPath(DATA_FOLDER_EXTERNAL, "configs")
    LOGS_FOLDER_EXTERNAL: PurePath = PurePosixPath(DATA_FOLDER_EXTERNAL, "logs")

    CELERY_BEAT_FILES: Path = Path(ENV_CELERY_BEAT_FILES)
    SLURM_LOGS_FOLDER_EXTERNAL: Path = Path(ENV_BASE_MOUNT, "slurm-logs")

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
    SKELETON_FILE: Path = Path(RESOURCES_FOLDER, "skeleton.mat")

    # Singularity container with sdannce image
    SDANNCE_IMAGE_PATH: Path = Path(ENV_SDANNCE_SINGULARITY_IMG_PATH)

    logger.info(f"USING INSTANCE DATA FOLDER AT: {DATA_FOLDER}")

    # max number of jobs running on local machine
    # should usually be 1, unless you have multiple GPUs on local machine
    # should be 0 if running on cluster (always use slurm to submit and manage jobs)
    MAX_CONCURRENT_LOCAL_JOBS: int = ENV_MAX_CONCURRENT_LOCAL_JOBS

settings = _Settings()
