from src.dannce.sdannce.dannce.param_defaults import (
    param_defaults_com,
    param_defaults_dannce,
    param_defaults_shared,
)

import yaml

all_params = {}

# read params from config files
dupes = {}
for key in param_defaults_shared:
    print("KEY [shared]", key)
    value = param_defaults_shared[key]
    value = str(value)

    if key in dupes:
        raise Exception("Duplicate param in shared params")
    dupes[key] = 1

    all_params[key] = {"shared": value}

dupes = {}
for key in param_defaults_dannce:
    print("KEY [dannce]", key)

    value = param_defaults_dannce[key]
    value = str(value)

    if key in dupes:
        raise Exception("Duplicate param in dannce params")
    dupes[key] = 1

    all_params[key] = {"dannce": value}

dupes = {}
for key in param_defaults_com:
    print("KEY [com]", key)
    value = param_defaults_com[key]
    value = str(value)

    if key in dupes:
        raise Exception("Duplicate param in com params")
    dupes[key] = 1

    all_params[key] = {"com": value}

# print(all_params)

# load from yaml files

yaml_list = [
    "src/dannce/sdannce/configs/com_mouse_config.yaml",
    "src/dannce/sdannce/configs/dannce_mouse_config.yaml",
    "src/dannce/sdannce/configs/dannce_rat_config.yaml",
    "src/dannce/sdannce/configs/dannce_rat7m_finetune.yaml",
    "src/dannce/sdannce/configs/sdannce_rat_config.yaml",
]


loaded_yamls = []

for file in yaml_list:
    with open(file) as stream:
        try:
            loaded = yaml.safe_load(stream)
            loaded_yamls.append(loaded)
        except yaml.YAMLError as exc:
            print("ERROR PARSING YAML FILE", exc)

for loaded in loaded_yamls:
    for key in loaded:
        value = loaded[key]
        if key not in all_params:
            raise Exception(f"Key: {key} not in all_params")

        param_dict = all_params[key]
        if "other" not in param_dict:
            param_dict["other"] = set()

        try:
            param_dict["other"].add(value)
        except TypeError:
            param_dict["other"].add(str(value))

# replace sets with list (they print nicer to strings)
for key in all_params:
    value = all_params[key]
    if "other" in value:
        othervalue = value["other"]
        if isinstance(othervalue, set):
            value["other"] = list(othervalue)

import pprint

pprint.pp(all_params)

import pandas as pd

df = pd.DataFrame(data=all_params).transpose()
df.sort_index(inplace=True)
df.index.name = "param_name"


df = df.reindex(columns=["shared", "dannce", "com", "other"])

df.to_csv("./out/all_params2.csv")
