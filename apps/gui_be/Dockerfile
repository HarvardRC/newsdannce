# website::tag::1:: Build a simple Docker image that contains a text file with the contents "Hello, World!"
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
WORKDIR /code
COPY --chown=$MAMBA_USER:$MAMBA_USER . .

# this allows future RUN commands to access conda
# install caldannce package
ARG MAMBA_DOCKERFILE_ACTIVATE=1
RUN python -m pip install ./resources/caldannce-0.0.1-py3-none-any.whl

# copy webserver dist
COPY --chown=$MAMBA_USER:$MAMBA_USER  ./resources/dist /dist

EXPOSE 8000

ENTRYPOINT ["/usr/local/bin/_entrypoint.sh", "/code/start_from_container.sh"]
