#!/bin/bash

#### Custom script for Chris devleopment
# does not contain any secret information
# TODO: remove from repo 

OUTPUT_TARGET=./dannce-gui-1.sif

echo "building docker"
./scripts/build-docker.sh

echo "building singularity"
./scripts/build-singularity.sh

mv ./dannce-gui.sif $OUTPUT_TARGET

echo "Uploading to luster"

rsync -avzP \
    $OUTPUT_TARGET \
    caxon@cannon:/n/holylabs/LABS/olveczky_lab/Lab/dannce-dev/containers/
