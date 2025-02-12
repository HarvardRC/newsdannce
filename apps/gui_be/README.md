# How to run
Recommended to run on a cluster compute environment linux using apptainer (singularity). Can also run locally (mac/windows/linux) using docker.

If you are targetting a slurm cluster, since most build steps require root permissions, it is recommended to run all build steps on a local Linux or Windows (with WSL/WSL2) machine and then copy to the cluster.

You also should not need to rebuild the container unless it does not work on your machine. If you have a working `dannce-gui.sif` file or docker container, you can use that.

