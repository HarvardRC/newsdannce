from dataclasses import dataclass

# from enum import Enum
from typing import Any, Literal
import typing

from pydantic import BaseModel, Field, Json

from app.core.db import JobMode, JobStatus, PredictionStatus, WeightsStatus


class TrainJobSubmitComModel(BaseModel):
    name: str = Field(default="[none]")
    output_model_name: str
    video_folder_ids: list[int]
    config: Json[Any] = Field(default="{}", validate_default=True)
    epochs: int
    vol_size: int
    runtime_id: int


class TrainJobSubmitDannceModel(BaseModel):
    name: str = Field(default="[none]")
    output_model_name: str
    video_folder_ids: list[int]
    config: Json[Any] = Field(default="{}", validate_default=True)
    epochs: int
    # vol_size: int
    runtime_id: int


class PredictJobSubmitComModel(BaseModel):
    name: str = Field(default="[none]")
    prediction_name: str
    weights_id: int
    video_folder_id: int
    runtime_id: int
    config: Json[Any] = Field(default="{}", validate_default=True)


class PredictJobSubmitDannceModel(BaseModel):
    name: str = Field(default="[none]")
    prediction_name: str
    weights_id: int
    video_folder_id: int
    runtime_id: int
    config: Json[Any] = Field(default="{}", validate_default=True)


class CancelJobModel(BaseModel):
    train_or_predict:Literal["TRAIN","PREDICT"]= Field()
    train_or_predict_job_id: int

class DeleteJobModel(BaseModel):
    job_id: int

@dataclass
class RuntimeData:
    id: int
    name: str
    partition_list: str
    memory_gb: int
    time_hrs: int
    n_cpus: int
    runtime_type: Literal["SLURM", "LOCAL"]


class CreateTrainingFolderModel(BaseModel):
    name: str
    path: str
    mode: JobMode


class CreateVideoFolderModel(BaseModel):
    name: str
    path: str


class CreateRuntimeModel(BaseModel):
    name: str
    partition_list: str
    memory_gb: int
    time_hrs: int
    n_cpus: int


class JobStatusDataObject(BaseModel):
    """Data object containing job status (enum) and job_id"""

    train_predict_job_id: int
    gpu_job_id: int
    train_or_predict: typing.Literal["TRAIN", "PREDICT"]
    job_status: JobStatus
    slurm_job_id: int
    created_at: int


class WeightsDataObject(BaseModel):
    weights_id: int
    weights_status: WeightsStatus


class PredictionDataObjet(BaseModel):
    prediction_id: int
    prediction_status: PredictionStatus


class ImportVideoFoldersModel(BaseModel):
    paths: list[str]


class MakePredictionPreviewModel(BaseModel):
    frames: list[int]
    camera_name_1: str
    camera_name_2: str
