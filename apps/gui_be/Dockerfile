# for base information, see https://micromamba-docker.readthedocs.io/en/latest/
FROM mambaorg/micromamba:ubuntu22.04

# this allows future RUN commands to access conda
ARG MAMBA_DOCKERFILE_ACTIVATE=1

# apt install all required programs as root (vim for testing)
USER root

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
RUN python -m pip install /app/resources/caldannce.whl
# copy scripts used for entrypoint
COPY --chown=$MAMBA_USER:$MAMBA_USER ./scripts /app/scripts

ENTRYPOINT ["/usr/local/bin/_entrypoint.sh", "/app/scripts/start_from_container-dev.sh"]
