# for base information, see https://micromamba-docker.readthedocs.io/en/latest/
FROM mambaorg/micromamba:ubuntu20.04

# apt install all required programs as root
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

# this allows future RUN commands to access conda
# install caldannce package
ARG MAMBA_DOCKERFILE_ACTIVATE=1
RUN python -m pip install /app/resources/caldannce-0.0.1-py3-none-any.whl

COPY --chown=$MAMBA_USER:$MAMBA_USER ./scripts /app/scripts

# EXPOSE 8000 0-- removed: not known what port the app will run on

ENTRYPOINT ["/usr/local/bin/_entrypoint.sh", "/app/scripts/start_from_container.sh"]
