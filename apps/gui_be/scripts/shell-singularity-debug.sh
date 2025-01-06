#!/bin/bash

# Minimal example 

# TRY TO make slurm commands availbe within singularity container
SING_BINDS="-B /etc/nsswitch.conf -B /etc/sssd/ -B /var/lib/sss -B /etc/slurm -B /slurm -B /var/run/munge -B `which sbatch ` -B `which srun ` -B `which sacct ` -B `which scontrol ` -B `which salloc ` -B `which squeue` -B /usr/lib64/slurm/ "

# start bash in the container
echo "Running shell within container"
echo "Try running sbatch, sacct, or scontrol"

singularity exec \
    $SING_BINDS \
    docker://ubuntu:22.04 /bin/bash \
    -c sacct

singularity exec -B ./chris_test /abc docker://ubuntu:22.04 /bin/