# tar czf archive_folder_name folder_to_copy
# zip -r archive.zip folder
# unzip test.zip [sudo apt-get install unzip]

# first extract file

set -euxo pipefail # bash (unofficial) strict mode
# set -e: exit on command has non-zero status
# set -x: print all executed commands to the terminal
# set -u: error if referencing an undefined $variable
# set -o pipefail: if any command in a pipeline (|) fails, the whole command throws an error


ROOT_DIR=$(pwd -P)

TEST_DIR=./workdir-test
TEST_DATA_FILE=data-m7.tgz

mkdir -p $TEST_DIR

cp "./tests/data/$TEST_DATA_FILE" "$TEST_DIR/"

cd $TEST_DIR

# extract tarball into current directory (specified by $TEST_DIR)
tar -xvzf $TEST_DATA_FILE

rm $TEST_DATA_FILE



# conda activate sdannce311

# echo "Step 1. Train COM [STARTED at $(date)]"

# dannce train com ./com_config.yaml

# echo "Step 1. Train COM [FINISHED at $(date)]"

# echo "Step 2. Predict COM [STARTED at $(date)]"

# dannce predict com ./com_config.yaml

# echo "Step 2. Predict COM [FINSIHED at $(date)]"

# echo "Step 3. Train DANNCE [STARTED at $(date)]"

# dannce train dannce ./dannce_config.yaml

# echo "Step 3. Train DANNCE [FINISHED at $(date)]"

# echo "Step 4. Predict DANNCE [STARTED at $(date)]"

# dannce predict dannce ./dannce_config.yaml

# echo "Step 4. Predict DANNCE [FINISHED at $(date)]"

# echo "ALL STEPS FINISHED"