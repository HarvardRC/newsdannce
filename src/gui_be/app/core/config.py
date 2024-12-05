from pydantic_settings import BaseSettings
from pathlib import Path
import os


class _Settings(BaseSettings):
    CODE_FOLDER: Path = Path(
        "/n/holylabs/LABS/olveczky_lab/Lab/dannce-dev/newsdannce/src/gui_be"
    )
    # Links relative to CODE FOLDER
    SQL_FOLDER: Path = Path(CODE_FOLDER, "sql")
    INIT_SQL_FILE: Path = Path(SQL_FOLDER, "schema.sql")
    POPULATE_SQL_FILE: Path = Path(SQL_FOLDER, "populate_db.sql")
    USER_DATA_SQL_FILE: Path = Path(SQL_FOLDER, "user_data.sql")

    DATA_FOLDER: Path = Path(
        "/n/holylabs/LABS/olveczky_lab/Lab/dannce-dev/newsdannce/src/gui_be/instance_data"
    )
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
    NODE_NAME: str = os.environ["SLURM_NODELIST"]
    # proxy url for webserver
    API_BASE_URL: str = (
        f"https://rcood.rc.fas.harvard.edu/rnode/{NODE_NAME}.rc.fas.harvard.edu/8000"
    )
    FRONTEND_HOST: str = "http://localhost:5173"
    STATIC_URL: str = f"{FRONTEND_HOST}/static"
    N_CAMERAS: int = 6


settings = _Settings()
