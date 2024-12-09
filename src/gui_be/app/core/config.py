from pydantic_settings import BaseSettings
from pathlib import Path
import os
import logging


class _Settings(BaseSettings):
    CODE_FOLDER: Path = Path(
        "."
    )
    # Links relative to CODE FOLDER
    SQL_FOLDER: Path = Path(CODE_FOLDER, "sql")
    INIT_SQL_FILE: Path = Path(SQL_FOLDER, "schema.sql")
    POPULATE_SQL_FILE: Path = Path(SQL_FOLDER, "populate_db.sql")
    USER_DATA_SQL_FILE: Path = Path(SQL_FOLDER, "user_data.sql")

    DATA_FOLDER: Path = Path('/instance_dir')
    logging.info(f"USING DATA FOLDER AT: {DATA_FOLDER}")
    # Links relative to DATA FOLDER
    DB_FILE: Path = Path(DATA_FOLDER, "db.sqlite3")
    SLURM_TRAIN_FOLDER: Path = Path(DATA_FOLDER, "slurm-cwd")
    SBATCH_DEBUG_FOLDER: Path = Path(DATA_FOLDER, "sbatch-debug")
    WEIGHTS_FOLDER: Path = Path(DATA_FOLDER, "weights")
    PREDICTIONS_FOLDER: Path = Path(DATA_FOLDER, "predictions")
    CONFIGS_FOLDER: Path = Path(DATA_FOLDER, "configs")
    LOGS_FOLDER: Path = Path(DATA_FOLDER, "logs")
    STATIC_TMP_FOLDER: Path = Path(DATA_FOLDER, "static-tmp")
    """A folder to store temporary server resources E.g. generated images, etc."""

    # name of slurm node the backend is running on
    NODE_NAME: str = os.environ.get("SLURM_NODELIST",'')
    # proxy url for webserver
    API_BASE_URL: str = os.environ.get("GUI_API_URL" , (
        f"https://rcood.rc.fas.harvard.edu/rnode/{NODE_NAME}.rc.fas.harvard.edu/8000"
    ))
    FRONTEND_HOST: str = os.environ.get("GUI_APP_URL", "http://localhost:5173")
    STATIC_URL: str = f"{FRONTEND_HOST}/static"
    N_CAMERAS: int = 6


settings = _Settings()
