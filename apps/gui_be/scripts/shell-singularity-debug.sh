#!/bin/bash


SING_BINDS=\
'-B /etc/nsswitch.conf '\
'-B /etc/slurm '\
'-B /lib64/libnss_sss.so.2:/lib/libnss_sss.so.2 '\
'-B /run/munge '\
'-B /slurm '\
'-B /usr/bin/sacct '\
'-B /usr/bin/salloc '\
'-B /usr/bin/sbatch '\
'-B /usr/bin/scancel '\
'-B /usr/bin/scontrol '\
'-B /usr/bin/scrontab '\
'-B /usr/bin/seff '\
'-B /usr/bin/sinfo '\
'-B /usr/bin/squeue '\
'-B /usr/bin/srun '\
'-B /usr/bin/sshare '\
'-B /usr/bin/sstat '\
'-B /usr/bin/strace '\
'-B /usr/lib64/libmunge.so.2 '\
'-B /usr/lib64/slurm '\
'-B /var/lib/sss '

# singularity exec --cleanenv ubuntu_22.04.sif squeue
singularity exec $SING_BINDS docker://ubuntu:22.04 /bin/bash -c squeue
