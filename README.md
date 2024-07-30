# Social DANNCE

To use the new calibration GUI for chesssboard targets, please read the calibration [README file](./src/calibration/README.md).


ALL COMMANDS ASSUME YOU'RE RUNNING THEM FROM THE ROOT OF THE REPO, not one of the subfolders!

## Overview

Conda env setup

1. install conda/mamba/micromamba, etc.

```
conda create --name sdannce311 python=3.11
conda activate sdannce311
conda install pytorch torchvision torchaudio pytorch-cuda=12.1 -c pytorch -c nvidia
pip install setuptools

```

## Developer Setup

VSCode recommended.

Recommended vscode extensions:
* Ruff python linter extension: [Link](https://marketplace.visualstudio.com/items?itemName=charliermarsh.ruff)



## Configure git for this repo

Ignore formatting commits when assigning git blame:

`git config --local blame.ignoreRevsFile .git-blame-ignore-revs`

# Testing

Please run the full pytest before submitting a PR:

currently the best command is:

```
py.test --ignore=tests/dannce --ignore=docs  --ignore=src
```

There should be no errors.
