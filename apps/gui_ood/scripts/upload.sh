#!/bin/bash

# NOTE: this script is for chris debugging. Make a similar version for your own user to use it.


# upload the dev package from a local computer to the cluster
echo "TIMING - upload at $(date)"

rsync -avhP ./ caxon@cannon:~/.fasrcood/dev/ood_dannce_test/ --delete

echo "Done!"