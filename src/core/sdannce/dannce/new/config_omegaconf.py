from omegaconf import OmegaConf, DictConfig, MISSING, ValidationError
import sys
import yaml
import hydra

from dannce.old_config_omegaconf import OldConfigFull


def make_params(config_path, omegaconf_args):
    """Make config object from yaml config path and cli arguments"""

    conf = load_configs(config_path, omegaconf_args)
    return conf


def load_configs(core_config_path: str, omegaconf_args: list[str]):
    """Load config files from specified paths.
    Throw exceptions at particular points to help locate invalid config file errors"""

    print(f"CORE CONFIG PATH {core_config_path} , OMEGACONF_ARGS {omegaconf_args}\n\n")
    schema = OmegaConf.structured(OldConfigFull)
    core_config = OmegaConf.load(core_config_path)

    cli_config = OmegaConf.from_cli(args_list=omegaconf_args)

    print(f"CLI Options provided  {cli_config}\n\n")

    try:
        conf = OmegaConf.merge(schema, core_config)
    except ValidationError as e:
        print(f"Validation error in core config: {e.msg}")
        sys.exit(1)
    except Exception as e:
        raise Exception(
            f"Unknown error with core config [file={core_config_path}]. msg={e.msg} "
        )

    try:
        conf = OmegaConf.merge(conf, cli_config)
    except ValidationError as e:
        print(f"Validation error in cli config: {e.msg}")
        sys.exit(1)
    except Exception as e:
        raise Exception(
            f"Unknown error merging cli config: [cli args={omegaconf_args}]. msg={e.msg}"
        )
    # OmegaConf.set_readonly(conf, True)

    # missing_keys = OmegaConf.missing_keys(conf)
    # if missing_keys:
    #     raise Exception(
    #         "The following keys are missing from config files and must be specified:",
    #         missing_keys,
    #     )

    print(OmegaConf.to_yaml(conf, resolve=True))
    return conf


def validate_params():
    pass
