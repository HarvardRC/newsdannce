# How to run
Recommended to run on a cluster compute environment linux using apptainer (singularity). Can also run locally (mac/windows/linux) using docker.

If you are targetting a slurm cluster, since most build steps require root permissions, it is recommended to run all build steps on a local Linux or Windows (with WSL/WSL2) machine and then copy to the cluster.

You also should not need to rebuild the container unless it does not work on your machine. If you have a working `dannce-gui.sif` file or docker container, you can use that.

# Build the frontend
1. Install [node v20 or greater](https://nodejs.org/en/download) or [nvm](https://github.com/nvm-sh/nvm)
2. Go to the frontend directory (`cd ./apps/gui_fe`). **All the following commands must be run from the gui_fe folder.**
3. Install package (`npm install`)
4. Build the frontend (`npm run build`). This should create a folder at /apps/gui_fe/react-dist
5. Copy the react-dist folder to gui_be resources folder (`cp ./react-dist ../resources/`)
6. Done. This build of the frontend will be used when building and running with singularity or docker.

# Build caldannce package:
1. Install conda or mamba (recommended: [micromamba](https://mamba.readthedocs.io/en/latest/installation/micromamba-installation.html))
2. Go to calibration directory (`cd ./apps/calibration`). **All the following commands must be run from the calibration folder.**
3. Create the conda environment: (`mamba env create -f ./environment.yml`)
4. Activate the environment: `mamba activate dannce-dev`
5. Run `python -m build`
6. Copy the caldannce wheel file (caldannce-0.0.1-py3-none-any.whl) to gui_be resources folder: `cp ./caldannce-0.0.1-py3-none-any.whl ../gui_be/resources/`
7. Done. This build of the caldannce will be used when building and running with singularity or docker.

# Build for the slurm cluster or local machine

1. All build steps are run after `cd ./apps/gui_be` and require an **account with root** (i.e. you cannot run these on the cluster unless you are an admin!).
2. Build the frontend and caldannce package (see instructions above)
3. Install Docker on your system [Docker Engine (linux only)](https://docs.docker.com/engine/install/) or [Docker Desktop (cross-platform)](https://www.docker.com/products/docker-desktop/).
4. Build docker container for the dannce-gui
  ```bash
  ./scripts/build-docker.sh
  ```
5. **At this point you can use the docker build to run locally. If you need to build for a slurm cluster, continue with the following steps:**
6. Build singuliarty container for sdannce (follow steps [here](https://gitlab.com/OlveczkyLab/sdannce_container)) TODO: NOTE: may require making this repo public
7. Upload `sdannce.sif` file to the cluster
8. Build singularity container for the dannce-gui
  ```bash
  ./scripts/build-singularity.sh
  ```
1. Upload `dannce-gui.sif` file to the cluster
2. Launch with `run-singularity.sh` or using OOD (example here).
