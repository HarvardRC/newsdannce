from omegaconf import MISSING
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional

REQUIRED = MISSING


class TrainMode(Enum):
    new = "new"
    finetune = "finetune"


@dataclass
class DannceAugmentations:
    # If brightness augmentation is True, chooses random brightness delta in [-val, +val]. Range = [0,1].
    brightness: bool = False
    brightness_value: float = 0.05
    # If continuous rotation enabled, rotate all images in each sample of the training set by a random value between [-5 deg, 5 deg] during training
    continuous_rotation: bool = False
    # If hue enabled, randomly augment hue of each image in training set during training
    hue: bool = False
    hue_value: float = 0.05
    # Rotation augmentation: TODO description
    rotation: bool = False
    rotation_value: float = 0.05  # TODO default value
    # Shear augmentaiton # TODO description
    shear: bool = False
    shear_value: float = 0.05  # TODO default value
    # translation augmention (prev: shift) TODO description
    translate: bool = False
    translate_value: float = 0.05  # TODO default value
    # zoom augmentation: TODO description
    zoom: bool = False
    zoom_value: float = 0.05  # TODO default value
    # mirror augmentation: TODO description
    mirror: bool = False
    # random view repalce # TODO description
    random_view_replace: bool = False
    # rotate augmentation # TODO description
    replace_view: bool = False
    # rotation augmentation TODO description
    rotation: bool = False


@dataclass
class DannceOptions:
    epochs: int = 10
    lr: float = 0.0001
    bounding_vol_size: int = 120
    finetune: bool = False
    finetune_weights: Optional[Path] = None
    augmentations: DannceAugmentations = field(default_factory=DannceAugmentations)


@dataclass
class ComOptions:
    epochs: int = 10
    lr: float = 0.0001
    finetune: bool = False
    train_dir = REQUIRED


@dataclass
class BaseConfig:
    n_animals: int = REQUIRED
    # if no random seed is provided, will use current time system
    random_seed: Optional[int] = None
    dannce: DannceOptions = field(default_factory=DannceOptions)
    com: ComOptions = field(default_factory=ComOptions)


@dataclass
class ComExperimentEntry:
    com_label_file: Path = MISSING


@dataclass
class DannceExperimentEntry:
    dannce_label_file: Path = MISSING
    com_prediction_file: Path = MISSING


@dataclass
class IoConfig:
    com_train_dir = MISSING
    com_predict_dir = MISSING
    com_predict_weights = MISSING

    com_experiment_list: list[ComExperimentEntry] = field(default_factory=lambda: [])

    dannce_train_dir = MISSING
    dannce_predict_dir = MISSING
    dannce_predict_weights = MISSING
    dannce_predict_model = MISSING

    dannce_experiments_list: list[DannceExperimentEntry] = field(
        default_factory=lambda: []
    )


@dataclass
class Context:
    pass
