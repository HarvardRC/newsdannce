# for base information, see https://micromamba-docker.readthedocs.io/en/latest/
FROM mambaorg/micromamba:ubuntu20.04

# File structure in container:
# NOTE: singularity default mounts: $HOME, /tmp, /proc, /sys, /dev, /$PWD (+ others)
######
# /data-mmt 							-- runtime mounts
# 	  /instance  					-- instance data folder (contains db, predictions, etc.)
# 	  /runtime.env  			-- contains internal ports, etc; sourced at runtime
#			/tmp								-- tmp files (e.g. static files generated during rumtime)
# /app
# 		/environment.yml		-- mamba environemt definition file
# 		/src								-- main app source code
#			/resources 					-- non-source resources
#					/react-dist			-- frontend build
#			/scripts						-- shell scripts for running/building/etc.


# this allows future RUN commands to access conda
ARG MAMBA_DOCKERFILE_ACTIVATE=1

# apt install all required programs as root (vim for testing)
USER root
# folder where data will be mounted
# RUN mkdir -p /data-mnt && chown $MAMBA_USER /data-mnt

RUN apt-get update && apt-get install -y --no-install-recommends \
	vim \
	&& rm -rf /var/lib/apt/lists/*

# setup conda environment from environment.yml file
USER $MAMBA_USER
COPY --chown=$MAMBA_USER:$MAMBA_USER environment.yml /tmp/environment.yml
RUN micromamba install -y -n base -f /tmp/environment.yml && \
	micromamba clean --all --yes

# copy code directory
WORKDIR /app
COPY --chown=$MAMBA_USER:$MAMBA_USER ./src /app/src
# resources includes wheels and webserver dist
COPY --chown=$MAMBA_USER:$MAMBA_USER  ./resources /app/resources
# install caldannce package
RUN python -m pip install /app/resources/caldannce-0.0.1-py3-none-any.whl
# copy scripts used for entrypoint
COPY --chown=$MAMBA_USER:$MAMBA_USER ./scripts /app/scripts


# EXPOSE 8000 0-- removed: not known what port the app will run on

ENTRYPOINT ["/usr/local/bin/_entrypoint.sh", "/app/scripts/start_from_container-dev.sh"]
