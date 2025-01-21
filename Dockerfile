##############################
### build frontend (react) ###
##############################

FROM node:22-bookworm-slim AS build_fe

WORKDIR /app

COPY ./apps/gui_fe /app
RUN npm install
RUN npm run build


###############################
### build caldannce package ###
###############################

FROM mambaorg/micromamba:ubuntu22.04 AS build_caldannce

# this allows future RUN commands to access conda
ARG MAMBA_DOCKERFILE_ACTIVATE=1

# apt install all required programs as root (vim for testing)
USER root

RUN apt-get update && apt-get install -y --no-install-recommends \
  vim \
  && rm -rf /var/lib/apt/lists/*

# setup conda environment from environment.yml file
USER $MAMBA_USER
COPY --chown=$MAMBA_USER:$MAMBA_USER ./apps/calibration/environment.yml /tmp/environment.yml
RUN micromamba install -y -n base -f /tmp/environment.yml && \
  micromamba clean --all --yes

WORKDIR /app
COPY --chown=$MAMBA_USER:$MAMBA_USER ./apps/calibration /app
RUN pip wheel . -w /app/packages

###############################
### build backend (fastapi) ###
###############################

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
COPY --chown=$MAMBA_USER:$MAMBA_USER ./apps/gui_be/environment.yml /tmp/environment.yml
RUN micromamba install -y -n base -f /tmp/environment.yml && \
  micromamba clean --all --yes

# copy code directory
WORKDIR /app
COPY --chown=$MAMBA_USER:$MAMBA_USER ./apps/gui_be/src /app/src
# resources includes wheels and webserver dist
COPY --from=build_fe --chown=$MAMBA_USER:$MAMBA_USER /app/react-dist /app/resources/react-dist
COPY --from=build_caldannce --chown=$MAMBA_USER:$MAMBA_USER /app/packages /app/resources/packages
COPY --chown=$MAMBA_USER:$MAMBA_USER ./apps/gui_be/resources/sql /app/resources/sql

# install caldannce package
RUN python -m pip install /app/resources/packages/*.whl
# copy scripts used for entrypoint
COPY --chown=$MAMBA_USER:$MAMBA_USER ./apps/gui_be/scripts /app/scripts

RUN cat /app/scripts/start_from_container-dev.sh  > ./echod.txt

ENTRYPOINT ["/usr/local/bin/_entrypoint.sh", "/app/scripts/start_from_container-dev.sh"]
