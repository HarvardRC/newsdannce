from enum import Enum, nonmember
from pathlib import Path
import typing
import sqlite3
from contextlib import closing


from app.core.config import settings


def does_db_file_exist():
    if Path(settings.DB_FILE).exists():
        return True
    return False


# Database Utility Functions
def get_db() -> typing.Generator[sqlite3.Connection, None, None]:
    conn = sqlite3.connect(settings.DB_FILE, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    # enable foreign keys for sqlite (disabled by default)
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
    finally:
        conn.close()


class SessionContext:
    def __init__(self):
        pass

    def __enter__(self):
        self.connection = sqlite3.connect(settings.DB_FILE, check_same_thread=False)
        self.connection.row_factory = sqlite3.Row
        self.connection.execute("PRAGMA foreign_keys = ON")
        return self.connection

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.connection.close()


def get_db_context():
    """Special function to get a db context for running background tasks
    Note: this returns a context you can use with the "with" statement.

    E.g.:
    with get_db_context() as db:
        do_something
    # auto-closed when context ends
    """
    return closing(sqlite3.connect(settings.DB_FILE, check_same_thread=False))


def init_db():
    print("INIT'ING DB...")
    conn = sqlite3.connect(settings.DB_FILE)
    cursor = conn.cursor()

    with open(settings.INIT_SQL_FILE) as f:
        query = f.read()
    cursor.executescript(query)
    conn.commit()
    conn.close()
    print("DONE INIT'ING DB...")


# def populate_db():
#     conn = sqlite3.connect(settings.DB_FILE)
#     cursor = conn.cursor()

#     with open(settings.POPULATE_SQL_FILE) as f:
#         query = f.read()
#     cursor.executescript(query)
#     conn.commit()
#     conn.close()



########################
# Database Table Names #
########################
TABLE_PREDICT_JOB = "predict_job"
TABLE_TRAIN_JOB = "train_job"
TABLE_VIDEO_FOLDER = "video_folder"
TABLE_PREDICTION = "prediction"
TABLE_WEIGHTS = "weights"
TABLE_TRAIN_JOB_VIDEO_FOLDER = "train_job_video_folder"
TABLE_RUNTIME = "runtime"
TABLE_SLURM_JOB = "slurm_job"
TABLE_MQ = "mq"


# table for global settings
TABLE_GLOBAL_STATE = "global_state"
# metadata columns:
METADATA_LAST_UPDATE_JOBS = "last_update_jobs"


##################################
# Job Status Options (from SLURM)#
##################################


class JobStatus(Enum):
    CANCELLED = ("CANCELLED", "CA")
    COMPLETED = ("COMPLETED", "CD")
    COMPLETING = ("COMPLETING", "CG")
    FAILED = ("FAILED", "F")
    NODE_FAIL = ("NODE_FAIL", "NF")
    OUT_OF_MEMORY = ("OUT_OF_MEMORY", "OOM")
    PENDING = ("PENDING", "PD")
    PREEMPTED = ("PREEMPTED", "PR")
    RUNNING = ("RUNNING", "R")
    SUSPENDED = ("SUSPENDED", "S")
    STOPPED = ("STOPPED", "ST")
    TIMEOUT = ("TIMEOUT", "TO")
    # Custom status meaning the job could not be queried in slurm
    LOST_TO_SLURM = ("LOST_TO_SLURM", "-")

    # SLURM status codes which are not permenantly resolved (i.e. could still change on their own)
    _nonfinal_statuses = nonmember(
        [COMPLETING, PENDING, PREEMPTED, RUNNING, SUSPENDED, STOPPED]
    )
    _success_statuses = nonmember([COMPLETED])
    _failure_statuses = nonmember(
        [CANCELLED, FAILED, NODE_FAIL, OUT_OF_MEMORY, TIMEOUT, LOST_TO_SLURM]
    )

    @staticmethod
    def from_code(code: str):
        for status in JobStatus:
            if status.code == code:
                return status
        raise ValueError(f"No JobStatus with code {code}")

    @classmethod
    def nonfinal_statuses(cls, as_escaped_str=False):
        """List of slurm job statuses where the status could still update (ie. not permenently stuck the status like FINSIHED)"""
        statuses_converted = [JobStatus(x[0]) for x in cls._nonfinal_statuses]
        if not as_escaped_str:
            return statuses_converted
        else:
            return ",".join([f"'{x.value}'" for x in statuses_converted])

    def is_nonfinal(self):
        nonfinal_converted = [JobStatus(x[0]) for x in self._nonfinal_statuses]
        return self in nonfinal_converted

    def is_failure(self):
        statuses_converted = [JobStatus(x[0]) for x in self._failure_statuses]
        return self in statuses_converted

    def is_success(self):
        statuses_converted = [JobStatus(x[0]) for x in self._success_statuses]
        return self in statuses_converted

    def __new__(cls, str_value, code):
        obj = object.__new__(cls)
        obj._value_ = str_value
        obj.code = code
        return obj

    def __str__(self):
        return self.value

    def __repr__(self):
        return f"<JobStatus.{self.name}: '{self.value}' (code='{self.code}') >"


#######################
# Job Command Options #
#######################


class JobMode(Enum):
    COM = "COM"
    DANNCE = "DANNCE"
    SDANNCE = "SDANNCE"


class JobCommand(Enum):
    TRAIN_COM = ("TRAIN.COM", "train com")
    TRAIN_DANNCE = ("TRAIN.DANNCE", "train dannce")
    TRAIN_SDANNCE = ("TRAIN.SDANNCE", "train sdannce")
    PREDICT_COM = ("PREDICT.COM", "predict com")
    PREDICT_DANNCE = ("PREDICT.DANNCE", "predict dannce")
    PREDICT_SDANNCE = ("PREDICT.SDANNCE", "predict sdannce")

    def __new__(cls, str_value, full_command):
        obj = object.__new__(cls)
        obj._value_ = str_value
        obj.full_command = full_command
        return obj

    def get_full_command(self) -> str:
        return self.full_command


########################
# Train Mode Options   #
########################


class TrainMode(Enum):
    NEW = "new"
    CONTINUED = "continued"
    FINETUNE = "finetune"


class WeightsStatus(Enum):
    PENDING = "PENDING"
    FAILED = "FAILED"
    COMPLETED = "COMPLETED"

    def __str__(self):
        return self.value


class PredictionStatus(Enum):
    PENDING = "PENDING"
    FAILED = "FAILED"
    COMPLETED = "COMPLETED"

    def __str__(self):
        return self.value
