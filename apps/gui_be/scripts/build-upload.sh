#!/bin/bash

# custom script for Chris building containers and uploading to the cluster
# TODO: remove from repo

set -e 

./scripts/build-docker.sh 
./scripts/build-singularity.sh

SOURCE_EP=2cfae25e-cd1a-11ef-a529-1beea83a8f52
SOURCE_PATH=/home/caxon/projects/newsdannce/apps/gui_be/dannce-gui.sif

DEST_EP=1156ed9e-6984-11ea-af52-0201714f6eab
DEST_PATH=/n/holylabs/LABS/olveczky_lab/Lab/dannce-dev/containers/dannce-gui.sif

task_id="$(globus transfer $SOURCE_EP:$SOURCE_PATH $DEST_EP:$DEST_PATH --jmespath 'task_id' --format=UNIX --notify=off)"

echo "Waiting on 'globus transfer' task '$task_id'"

globus task wait "$task_id" --timeout 30
if [ $? -eq 0 ]; then
    echo "$task_id completed successfully";
else
    echo "$task_id failed!";
fi

echo "Done!"
