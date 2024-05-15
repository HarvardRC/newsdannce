from dataclasses import dataclass, field
from omegaconf import MISSING
from pathlib import Path
from typing import Optional, Union


@dataclass
class OldConfigFull:
    COM_augmentation: object = MISSING
    allow_valid_replace: bool = MISSING
    augment_bright_val: float = MISSING
    augment_brightness: bool = MISSING
    augment_continuous_rotation: bool = MISSING

    augment_hue: bool = MISSING
    augment_hue_val: float = MISSING
    augment_rotation: bool = MISSING
    augment_rotation_val: float = MISSING
    augment_shear: bool = MISSING
    augment_shear_val: float = MISSING
    augment_shift: bool = MISSING
    augment_shift_val: float = MISSING
    augment_zoom: bool = MISSING
    augment_zoom_val: float = MISSING
    batch_size: int = MISSING
    # cam3_train:
    camnames: list[str] = MISSING
    channel_combo = MISSING
    chunks = MISSING
    # com_debug
    com_exp: list[str] = MISSING
    com_file: str = MISSING
    com_finetune_weights: str = MISSING
    com_fromlabels: bool = MISSING
    com_method: str = MISSING
    com_predict_dir: Path = MISSING
    com_predict_weights: str = MISSING
    # com_thresh
    com_train_dir: Path = MISSING
    comthresh: float = MISSING
    crop_height: int = MISSING
    crop_width: int = MISSING
    cthresh: float = MISSING
    dannce_finetune_weights: Path = MISSING
    dannce_predict_dir: Path = MISSING
    dannce_predict_model: Path = MISSING
    dannce_predict_vol_tifdir: Path = MISSING
    dannce_train_dir: Path = MISSING
    data_split_seed: Optional[int]
    dataset: str = MISSING
    dataset_args: object = MISSING
    debug: bool = MISSING
    debug_train_volume_tifdir: Path = MISSING
    debug_volume_tifdir: Path = MISSING
    depth: bool = MISSING
    downfac: int = MISSING
    downscale_occluded_view: bool = MISSING
    drop_landmark: Optional[list] = MISSING
    dsmode: str = MISSING
    epochs: int = MISSING
    exp: Optional[list[object]] = MISSING
    expval: bool = MISSING
    extension: str = MISSING
    form_batch: bool = MISSING
    form_bs: int = MISSING
    from_weights: bool = MISSING
    gpu_id: str = MISSING
    graph_cfg: object = MISSING
    heatmap_reg: bool = MISSING
    heatmap_reg_coeff: float = MISSING
    immode: str = MISSING
    # inference_ttt:
    interp: str = MISSING
    io_config: Path = MISSING
    label3d_index: int = MISSING
    left_keypoints: list[int] = MISSING
    load_valid: Path = MISSING
    # lockfirst:
    loss: object = MISSING
    lr: float = MISSING
    lr_scheduler: object = MISSING
    max_num_samples: int = MISSING
    medfilt_window: int = MISSING
    metric: list[str] = MISSING
    mirror: bool = False
    mirror_augmentation: bool = False
    mono: bool = False
    multi_gpu_train: bool = False
    n_channels_in: int = MISSING
    n_channels_out: int = MISSING
    n_instances: int = MISSING
    n_layers_locked: int = MISSING
    n_rand_views: int = MISSING
    n_support_chunks: int = MISSING
    n_views: int = MISSING
    net: str = MISSING
    net_type: str = MISSING
    new_n_channels_out: int = MISSING
    norm_method: str = MISSING
    num_train_per_exp: int = MISSING
    num_validation_per_exp: int = MISSING
    nvox: int = MISSING
    predict_labeled_only: bool = MISSING
    rand_view_replace: bool = MISSING
    random_seed: int = MISSING
    raw_im_h: int = MISSING
    raw_im_w: int = MISSING
    replace_view: bool = MISSING
    right_keypoints: list = MISSING
    rotate: bool = MISSING
    save_period: int = MISSING
    save_pred_targets: bool = MISSING
    sigma: float = MISSING
    skeleton: str = MISSING
    slurm_config: Path = MISSING
    # social_big_volume:
    # social_joint_training
    social_training: bool = MISSING
    start_batch: int = MISSING
    start_sample: int = MISSING
    # support_exp:
    train_mode: str = MISSING
    training_fraction: float = MISSING
    unlabeled_fraction: float = MISSING
    unlabeled_sampling: Union[float, str] = MISSING
    # unlabeled_temp:
    use_npy: bool = MISSING
    # use_silhouette
    # use_silhouette_in_volume
    # use_temporal:
    valid_exp: list[int] = MISSING
    verbose: int = MISSING
    vid_dir_flag = MISSING
    viddir: str = MISSING
    vmax: int = MISSING
    vmin: int = MISSING
    vol_size: int = MISSING
    weighted: bool = MISSING
    write_npy: bool = MISSING
    # write_visual_hull:
    n_samples_per_gpu: int = MISSING
    only_unfinished: bool = MISSING
    predict_path: Path = MISSING
    test: bool = MISSING
    dannce_file: Path = MISSING
    multi_mode: bool = MISSING
