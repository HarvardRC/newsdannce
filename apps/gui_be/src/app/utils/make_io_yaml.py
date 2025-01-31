import json
import sqlite3
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, Field, ConfigDict
from ruamel.yaml import YAML
from pathlib import Path

from app.core.db import (
    JobCommand,
    TrainMode,
)
from app.models import (
    PredictJobSubmitComModel,
    PredictJobSubmitDannceModel,
    TrainJobSubmitComModel,
    TrainJobSubmitDannceModel,
)
from app.utils.video_folders import (
    ComExpEntry,
    DannceExpEntry,
    get_com_file_path,
    get_video_folder_path,
    get_video_folders_for_com,
    get_video_folders_for_dannce,
)
from app.core.config import settings
from app.utils.weights import get_weights_path_from_id
from app.utils.helpers import make_resource_name


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
    lr: float = Field(default=0.0001)
    metric: list = Field(default=[])  # required to provide empty array
    loss: dict = Field(default={"L1Loss": {"loss_weight": 1.0}})
    save_period: int = Field(default=5)
    max_num_samples: int | str = Field(default="max")
    use_npy: bool = Field(default=False)
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
    META_weights_path: str = Field()
    META_config_path: str = Field()
    META_log_path: str = Field()
    n_channels_out: int = Field(default=1)
    crop_height: tuple[int, int] = Field(default=(0, 1152))
    crop_width: tuple[int, int] = Field(default=(0, 1920))
    com_train_dir: Path = Field()  # COM model weights output
    com_exp: list[ComExpEntry]


class ComPredictModel(ConfigModel):
    META_command: JobCommand = JobCommand.PREDICT_COM
    META_prediction_path: str = Field()
    META_log_path: str = Field()
    META_config_path: str = Field()
    n_channels_out: int = Field(default=1)
    crop_height: tuple[int, int] = Field(default=(0, 1152))
    crop_width: tuple[int, int] = Field(default=(0, 1920))
    com_predict_dir: Path = Field()  # COM predictions location
    com_predict_weights: Path = Field()  # COM model weights file


class DannceTrainModel(ConfigModel):
    META_command: JobCommand = JobCommand.TRAIN_DANNCE
    META_prediction_path: str = Field()
    META_weights_path: str = Field()
    META_config_path: str = Field()
    META_log_path: str = Field()
    n_channels_out: int = Field(default=23)
    new_n_channels_out: int = Field(default=23)
    crop_height: tuple[int, int] = Field(default=(0, 1200))
    crop_width: tuple[int, int] = Field(default=(0, 1920))
    dannce_train_dir: Path = Field()  # DANNE model weights output
    exp: list[DannceExpEntry]


class DanncePredictModel(ConfigModel):
    META_command: JobCommand = JobCommand.PREDICT_DANNCE
    META_log_path: str = Field()
    META_config_path: str = Field()
    n_channels_out: int = Field(default=23)
    new_n_channels_out: int = Field(default=23)
    crop_height: tuple[int, int] = Field(default=(0, 1200))
    crop_width: tuple[int, int] = Field(default=(0, 1920))
    dannce_predict_dir: Path = Field()  # DANNCE predictions output
    dannce_predict_model: Path = Field()  # DANNCE model weights to use
    com_file: Path = Field()  # File containing COM predictions
    batch_size: int = Field(default=1)  # default 1 batch size to reduce memory usage


def config_com_train(conn: sqlite3.Connection, data: TrainJobSubmitComModel):
    video_folder_ids = data.video_folder_ids
    com_train_weights_path = make_resource_name("COM_")
    config_path = make_resource_name("TRAIN_COM_", ".yaml")
    log_path = make_resource_name("TRAIN_COM_", ".out")

    # External directory for weights
    com_train_dir_external = Path(
        settings.WEIGHTS_FOLDER_EXTERNAL, com_train_weights_path
    )

    com_exps = get_video_folders_for_com(conn, video_folder_ids)

    data.config["epochs"] = data.epochs
    data.config["vol_size"] = data.vol_size

    cfg = ComTrainModel(
        com_exp=com_exps,
        com_train_dir=com_train_dir_external,
        META_cwd=settings.SLURM_TRAIN_FOLDER_EXTERNAL,
        META_weights_path=com_train_weights_path,
        META_config_path=config_path,
        META_log_path=log_path,
        **data.config,
    )
    return cfg


def config_dannce_train(conn: sqlite3.Connection, data: TrainJobSubmitDannceModel):
    video_folder_ids = data.video_folder_ids
    dannce_train_weights_path = make_resource_name("DANNCE_")
    config_path = make_resource_name("TRAIN_DANNCE_", ".yaml")
    log_path = make_resource_name("TRAIN_DANNCE_", ".out")

    dannce_train_dir = Path(
        settings.WEIGHTS_FOLDER_EXTERNAL, dannce_train_weights_path
    )

    dannce_exps = get_video_folders_for_dannce(conn, video_folder_ids)

    data.config["epochs"] = data.epochs

    cfg = DannceTrainModel(
        exp=dannce_exps,
        dannce_train_dir=dannce_train_dir,
        META_cwd=settings.SLURM_TRAIN_FOLDER_EXTERNAL,
        META_weights_path=dannce_train_weights_path,
        META_config_path=config_path,
        META_log_path=log_path,
        **data.config,
    )
    return cfg


def config_com_predict(conn: sqlite3.Connection, data: PredictJobSubmitComModel):
    video_folder_path = get_video_folder_path(conn, data.video_folder_id)
    weights_path_info = get_weights_path_from_id(conn, data.weights_id)
    weights_latest_filename = weights_path_info.latest_filename
    weights_path = weights_path_info.weights_path

    weights_file_external = Path(settings.WEIGHTS_FOLDER_EXTERNAL, weights_path, weights_latest_filename)

    prediction_path = make_resource_name("PREDICT_COM_")
    config_path = make_resource_name("PREDICT_COM_", ".yaml")
    log_path = make_resource_name("PREDICT_COM_", ".out")

    prediction_path_internal = Path(settings.PREDICTIONS_FOLDER, prediction_path )
    prediction_path_external = Path(settings.PREDICTIONS_FOLDER_EXTERNAL, prediction_path)
    prediction_path_internal.mkdir(exist_ok=False, mode=0o777)

    blank_io_yaml_file = Path(settings.SLURM_TRAIN_FOLDER_EXTERNAL, "io.yaml")

    prediction_path_external = Path(
        settings.PREDICTIONS_FOLDER_EXTERNAL, prediction_path
    )

    video_folder_path_external = Path(settings.VIDEO_FOLDERS_FOLDER_EXTERNAL, video_folder_path)

    cfg = ComPredictModel(
        META_cwd=video_folder_path_external,
        META_config_path=config_path,
        META_log_path=log_path,
        META_prediction_path=prediction_path,
        com_predict_dir=prediction_path_external,
        com_predict_weights=weights_file_external,
        io_config=blank_io_yaml_file,
        **data.config,
    )

    return cfg


def config_dannce_predict(conn: sqlite3.Connection, data: PredictJobSubmitDannceModel):
    video_folder_path = get_video_folder_path(conn, data.video_folder_id)
    weights_path_info = get_weights_path_from_id(conn, data.weights_id)
    weights_latest_filename = weights_path_info.latest_filename
    weights_path = weights_path_info.weights_path

    weights_file_external = Path(settings.WEIGHTS_FOLDER_EXTERNAL, weights_path, weights_latest_filename)

    com_file_path = get_com_file_path(conn, data.video_folder_id)

    config_path = make_resource_name("PREDICT_DANNCE_", ".yaml")
    log_path = make_resource_name("PREDICT_DANNCE_", ".out")
    prediction_path = Path( make_resource_name("PREDICT_DANNCE_"))


    blank_io_yaml_file = Path(settings.SLURM_TRAIN_FOLDER, "io.yaml")

    prediction_path_internal = Path(settings.PREDICTIONS_FOLDER, prediction_path )
    prediction_path_external = Path(settings.PREDICTIONS_FOLDER_EXTERNAL, prediction_path)
    prediction_path_internal.mkdir(exist_ok=False, mode=0o777)

    video_folder_path_external = Path(settings.VIDEO_FOLDERS_FOLDER_EXTERNAL, video_folder_path)

    cfg = DanncePredictModel(
        META_cwd=video_folder_path_external,
        META_config_path=config_path,
        META_log_path=log_path,
        dannce_predict_dir=prediction_path_external,
        dannce_predict_model=weights_file_external,
        io_config=blank_io_yaml_file,
        com_file=com_file_path,
        **data.config,
    )

    return cfg
