"""Entrypoints for dannce training and prediction."""

import sys
import argparse
from pathlib import Path

from dannce.config_omegaconf import make_params

com_train = lambda: 0
com_predict = lambda: 0
dannce_train = lambda: 0
dannce_predict = lambda: 0


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "target",
        choices=["train-com", "predict-com", "train-dannce", "predict-dannce"],
    )
    parser.add_argument(
        "config_path",
        help="config path",
    )
    args, unparsed_args = parser.parse_known_args()
    return args, unparsed_args


def validate_config_path(config_path):
    p = Path(config_path)
    if not p.exists():
        raise Exception("Config does not exist at path")


def main():
    """Entry point for the command line interface."""
    args, omegaconf_args = parse_args()
    target = args.target
    config_path = args.config_path

    validate_config_path(config_path)

    make_params(config_path, omegaconf_args)

    print(f"TARGET/CONFIG_PATH: {target}/{config_path}")

    match target:
        case "train-com":
            com_train()
        case "predict-com":
            com_predict()
        case "train-dannce":
            dannce_train()
        case "predict-dannce":
            dannce_predict()
        case _:
            raise Exception("Invalid dannce target specified")


if __name__ == "__main__":
    main()
