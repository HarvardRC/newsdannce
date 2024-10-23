import json
import sqlite3
from typing import Any
import uuid
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, Field, ConfigDict
from ruamel.yaml import YAML
from pathlib import Path

from app.core.db import (
    JobCommand,
    TrainMode,
)
from app.models import PredictJobSubmitComModel, TrainJobSubmitComModel
from app.utils.video_folders import (
    ComExpEntry,
    DannceExpEntry,
    get_video_folder_path,
    get_video_folders_for_com,
)
from app.core.config import settings
from app.utils.weights import get_weights_path_from_id


class ConfigModel(BaseModel):
    ### MODEL CONFIG
    # pydnatic to use enums string value intead of python class when exporting
    model_config = ConfigDict(use_enum_values=True)
    ### EXTRA METADATA NOT USED BY DANNCE (BUT USED BY DANNCE GUI)
    # cwd to run the train/predict sbatch script from
    META_cwd: Path = Field()
    META_command: JobCommand = Field()

    ### BASE CONFIG ENTRIES ###
    camnames: list[str] = Field(
        default=["Camera1", "Camera2", "Camera3", "Camera4", "Camera5", "Camera6"]
    )
    n_instances: int = Field(default=1)
    n_channels_out: int  # OVERRIDE LATER
    downfac: int = Field(default=8)
    n_channels_in: int = Field(default=3)
    raw_im_h: int = Field(default=1200)
    raw_im_w: int = Field(default=1920)
    train_mode: TrainMode = Field(default=TrainMode.NEW, validate_default=True)
    num_validation_per_exp: int = Field(default=2)
    batch_size: int = Field(default=4)
    epochs: int = Field(default=20)
    lr: float = Field(default=5e-5)
    metric: list[Any] = Field(default=[])  # required to provide empty array
    loss: dict = Field(default={"MSELoss": {"loss_weight": 1.0}})
    save_period: int = Field(default=5)
    max_num_samples: int | str = Field(default="max")
    io_config: Path = Field(Path("./io.yaml"))  # TODO: better solution to inject this

    def to_dict_safe(self):
        return jsonable_encoder(self)

    def to_json_string(self):
        safe_dict = self.to_dict_safe()
        return json.dumps(safe_dict)

    def to_yaml_string(self):
        d = self.to_dict_safe()
        d = {k: v for k, v in d.items() if not k.startswith("META_")}
        yaml = YAML(typ=["rt", "string"])
        yaml_string = yaml.dump_to_string(d)
        return yaml_string


class ComTrainModel(ConfigModel):
    META_command: JobCommand = JobCommand.TRAIN_COM
    n_channels_out: int = Field(default=1)
    crop_height: tuple[int, int] = Field(default=(0, 1152))
    crop_width: tuple[int, int] = Field(default=(0, 1920))
    com_train_dir: Path = Field()  # COM model weights output
    com_exp: list[ComExpEntry]


class ComPredictModel(ConfigModel):
    META_command: JobCommand = JobCommand.PREDICT_COM
    n_channels_out: int = Field(default=1)
    crop_height: tuple[int, int] = Field(default=(0, 1152))
    crop_width: tuple[int, int] = Field(default=(0, 1920))
    com_predict_dir: Path = Field()  # COM predictions location
    com_predict_weights: Path = Field()  # COM model weights file


class DannceTrainModel(ConfigModel):
    META_command: JobCommand = JobCommand.TRAIN_DANNCE
    n_channels_out: int = Field(default=23)
    crop_height: tuple[int, int] = Field(default=(0, 1200))
    crop_width: tuple[int, int] = Field(default=(0, 1920))
    dannce_train_dir: Path = Field()  # DANNE model weights output
    exp: list[DannceExpEntry]


class DanncePredictModel(ConfigModel):
    META_command: JobCommand = JobCommand.PREDICT_DANNCE
    n_channels_out: int = Field(default=23)
    crop_height: tuple[int, int] = Field(default=(0, 1200))
    crop_width: tuple[int, int] = Field(default=(0, 1920))
    dannce_predict_dir: Path = Field()  # DANNCE predictions output
    dannce_predict_model: Path = Field()  # DANNCE model weights to use


def config_com_train(conn: sqlite3.Connection, data: TrainJobSubmitComModel):
    video_folder_ids = data.video_folder_ids
    com_train_dir = Path(settings.WEIGHTS_FOLDER, f"com_train_{uuid.uuid4().hex}")

    com_exps = get_video_folders_for_com(conn, video_folder_ids)
    data.config["epochs"] = data.epochs
    data.config["vol_size"] = data.vol_size
    cfg = ComTrainModel(
        com_exp=com_exps,
        com_train_dir=com_train_dir,
        META_cwd=settings.SLURM_TRAIN_FOLDER,
        **data.config,
    )
    return cfg


def config_com_predict(conn: sqlite3.Connection, data: PredictJobSubmitComModel):
    # com_train_dir = Path(settings.WEIGHTS_FOLDER, data.output_model_name).resolve()
    video_folder_path = get_video_folder_path(conn, data.video_folder_id)
    weights_path = get_weights_path_from_id(conn, data.weights_id)
    prediction_path = Path(
        settings.PREDICTIONS_FOLDER, f"com_predict_{uuid.uuid4().hex}"
    )
    blank_io_yaml_file = Path(settings.SLURM_TRAIN_FOLDER, "io.yaml")

    prediction_path.mkdir(exist_ok=False, mode=0o770)

    cfg = ComPredictModel(
        META_cwd=video_folder_path,
        com_predict_dir=prediction_path,
        com_predict_weights=weights_path,
        io_config=blank_io_yaml_file,
        **data.config,
    )

    return cfg


def config_dannce_train():
    pass


def config_dannce_predict():
    pass


# def make_io_yaml_predict(pred_job_id, training_dir, predict_model_path, video_dir):
#     """Make an io.yaml file for a predict job"""
#     yaml = YAML(typ=["rt", "string"])
#     path = PurePosixPath()


# def make_io_yaml_train(train_job_id, training_dir, video_dirs):
#     """Make an io.yaml file for a train job"""
#     yaml = YAML(typ=["rt", "string"])
