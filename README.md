# NewsDANNCE: DANNCE and Utilities

## Introduction
This repository contains code to facilite running DANNCE.

There is documentation for buildling a dannce recording rig, for chosing 

## Building DANNCE Rig

[Dannce Rig Tutorial](docs/tutorials/DANNCE%20Rig%20Building%20Tutorial.pdf)
[Bill of Materials](docs/tutorials/DANNCE%20Tutorial%20Bill%20of%20Materials.xlsx)

## Calibration

[Calibration Docs](apps/calibration/README.md)

## DANNCE GUI

User Guide: See [user guide (pdf)](docs/tutorials/DANNCE%20GUI%20User%20Manual.pdf)

Running on OpenOnDemand - see [guide here](apps/gui_ood/README.md)

### Build

Install docker and singularity.

Run the following scripts:

```bash
./scripts/build-docker.sh 
./scripts/build-singularity.sh
```

Upload the .SIF file to a location accessible from the cluster.


## Developer
**What do the dannce parameters mean?** 
See [Parameter Explanation Spreadsheet](docs/tutorials/DANNCE%20Parameter%20Cleanup.xlsx)

**Configure git for the repo**

Ignore formatting commits when assigning git blame:

`git config --local blame.ignoreRevsFile .git-blame-ignore-revs`

Developer suggestions - see [here](docs/tutorials/Dannce%20Features%20Development%20Guide.md)
