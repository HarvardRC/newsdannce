# AUTHOR: Chris Axon (christopher_axon@harvard.edu)
# 2024-04-15

# PROBLEM THIS SOLVES: some label3d .mat files are exported with the incorrect incides
# i.e. they start at 1 instead of 0. This script searches in a directory rescursively for
# label3d .mat files and updates the sync struct as needed.

# label3d file -> labelData -> data_frame & data_sampleID

import argparse
import os
import scipy.io as sio
import numpy as np


# Assume it's always 6 for now
N_CAMERAS = 6


def runscript(filename, n_frames, n_keypoints):
    print(
        f"Trying to add the `sync` field to file: {filename}. n_frames={n_frames}, n_keypoints={n_keypoints}"
    )

    if n_frames < 1:
        raise Exception(f"n_frames must be integer >= 1. n_frames={n_frames}")

    if n_keypoints < 1 or n_keypoints >= 100:
        raise Exception(
            f"n_keypoints must be >= 1. It is also probably < 100. This is NOT the # of frames in the recording! n_keypoints={n_keypoints}"
        )

    _, ext_part = os.path.splitext(filename)
    if ext_part != ".mat":
        raise Exception("File must have .mat extension")

    mat = sio.loadmat(filename)

    if "sync" in mat:
        try:
            print("`sync` field exists. Checking for structure...")
            # this should raise an error if data_2d is not populated
            mat["sync"][0, 0].dtype.fields["data_2d"]

            # if no TypeError, we raise a generic exeption
            raise Exception("Mat already contains a non-empty `sync` field")
        except TypeError:
            print("`sync` field is empty")

    sync_arr = np.ndarray((N_CAMERAS, 1), dtype=object)

    shape_data_2d = (n_frames, n_keypoints * 2)
    shape_data_3d = (n_frames, n_keypoints * 3)
    shape_data_frame = (1, n_frames)
    shape_data_sampleID = (1, n_frames)

    print("Using the following array shapes")
    print(f" - data_2d: {shape_data_2d}")
    print(f" - data_3d: {shape_data_3d}")
    print(f" - data_frame: {shape_data_frame}")
    print(f" - data_sample_ID: {shape_data_sampleID}")

    for i in range(N_CAMERAS):
        this_cam_array = np.ndarray(
            (1, 1),
            dtype=[
                ("data_2d", object),
                ("data_3d", object),
                ("data_frame", object),
                ("data_sampleID", object),
            ],
        )

        this_cam_array[0, 0]["data_2d"] = np.zeros(shape=shape_data_2d, dtype=np.double)

        this_cam_array[0, 0]["data_3d"] = np.zeros(shape=shape_data_3d, dtype=np.double)

        this_cam_array[0, 0]["data_frame"] = np.arange(
            n_frames, dtype=np.double
        ).reshape(shape_data_frame)

        this_cam_array[0, 0]["data_sampleID"] = np.arange(
            n_frames, dtype=np.double
        ).reshape(shape_data_sampleID)

        sync_arr[i, 0] = this_cam_array

    print("Done making sync array")
    mat["sync"] = sync_arr

    try:
        filepart_name, filepart_ext = os.path.splitext(filename)
        newname = filepart_name + "_sync" + filepart_ext
        sio.savemat(newname, mat)
        print(f"Original file: {filename}")
        print(f"Saved to: {newname}")

    except Exception as e:
        print(
            f"Unable to save file to new path:\n--Original file: {filename}\n--New Path: {newname}"
        )
        raise e


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--filename",
        "-f",
        required=True,
        help="label3d .mat file to add `sync` matrix to",
    )

    parser.add_argument(
        "--n-frames",
        "-s",
        required=True,
        type=int,
        help="Number of frames/samples in the corresponding video (e.g. 90000)",
    )

    parser.add_argument(
        "--n-keypoints",
        "-k",
        required=True,
        type=int,
        help=(
            "Number of keypoints in the label3d data (e.g. 2, 23, 46)"
            + ". For 1x COM this is 1, for 2x COM's this is 2, for 2x rat23"
            + " this is 46, etc."
        ),
    )

    args = parser.parse_args()

    runscript(**vars(args))
