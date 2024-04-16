# AUTHOR: Chris Axon (christopher_axon@harvard.edu)
# 2024-04-15

# PROBLEM THIS SOLVES: some label3d .mat files are exported with the incorrect incides
# i.e. they start at 1 instead of 0. This script searches in a directory rescursively for
# label3d .mat files and updates the sync struct as needed.

# label3d file -> labelData -> data_frame & data_sampleID

import argparse
import os
import sys
import pathlib
from pprint import pp
import re
import scipy.io as sio

match_regex = r"(?i)Label3D\w*\.mat$"


def runscript(base_dir, confirm):
    candidate_files = []

    print("Walking directory, looking for matlab files", base_dir)
    for root, dirs, files in os.walk(base_dir):
        for filename in files:
            if re.search(match_regex, filename):
                candidate_files.append(f"{root}/{filename}")

    print(f"\nCandidate files based on name only ({len(candidate_files)})")

    for i, f in enumerate(candidate_files):
        print(f"    {i}. {f}")

    correct_format_files = []

    for fname in candidate_files:
        try:
            mat = sio.loadmat(fname)

            cam_idx = 0

            data_frame = mat["labelData"][cam_idx, 0]["data_frame"][0, 0]
            data_sampleID = mat["labelData"][cam_idx, 0]["data_sampleID"][0, 0]
            if data_frame[0, 0] == 1 and data_sampleID[0, 0] == 1:
                correct_format_files.append(fname)
            else:
                print(f"File is already fixed: {fname}")

        except Exception:
            pass

    print(f"\nCandidate files based on content ({len(correct_format_files)})")

    for i, f in enumerate(correct_format_files):
        print(f"    {i}. {f}")

    if not confirm:
        raise Exception(
            "DRY RUN ONLY. TO MODIFY LISTED FILES, USE THE --confirm OR -y FLAG"
        )

    print(
        "\nRE-SAVING LISTED FILES WITH data_sampleID AND data_frame STARTING AT 0 INSTEAD OF 1"
    )

    output_files = []
    for fname in correct_format_files:
        try:
            mat = sio.loadmat(fname)
            for cam_idx in range(6):
                data_frame = mat["labelData"][cam_idx, 0]["data_frame"][0, 0]
                data_sampleID = mat["labelData"][cam_idx, 0]["data_sampleID"][0, 0]

                # numpy in-place operations
                data_frame -= 1
                data_sampleID -= 1
        except Exception:
            raise Exception(f"Unknown error modifying file content: {fname}")

        try:
            filepart_name, filepart_ext = os.path.splitext(fname)
            newname = filepart_name + "_fixed" + filepart_ext
            sio.savemat(newname, mat)
            output_files.append(newname)
            print(f"Original file: {fname}")
            print(f"Saved to: {newname}")
        except Exception as e:
            print(
                f"Unable to save file to new path:\n--Original file: {fname}\n--New Path: {newname}"
            )
            raise e

    print(f"\nDone processing ({len(output_files)}) files!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--base-dir",
        "-d",
        required=False,
        help="base directory to search in",
        default=".",
    )
    parser.add_argument(
        "--confirm",
        "-y",
        required=False,
        help="Actually the operation on the list of candidates",
        default=False,
        action="store_true",
    )

    args = parser.parse_args()

    runscript(**vars(args))
