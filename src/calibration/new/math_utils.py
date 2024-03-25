import numpy as np


def calculate_rpe(imgpoints, re_imgpoints):
    norms = np.linalg.norm(imgpoints - re_imgpoints, axis=1)
    avg = np.mean(norms, axis=0)
    return avg
