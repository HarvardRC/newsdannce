import numpy as np


def calculate_rpe(imgpoints, re_imgpoints):
    """Calculate average reprojection error from image points and re-projected image points"""
    norms = np.linalg.norm(imgpoints - re_imgpoints, axis=1)
    avg = np.mean(norms, axis=0)
    return avg


def triangulate(imgpoints, view_matrices):
    # imgpoints: list of either np.ndarray((2,1)) or np.ndarray((2,));
    #     of length n
    # view_matrices: 3x4 camera projection matrices for each view

    assert len(imgpoints) == len(view_matrices)
    assert imgpoints[0].size == 2
    assert view_matrices[0].shape == (3, 4)

    for ipt in imgpoints:
        ipt.reshape((2, 1))

    n_views = len(imgpoints)
    A = np.zeros((n_views * 3, 4), dtype=np.float64)
    for i in range(n_views):
        P = view_matrices[i]
        u = imgpoints[i]
        A[3 * i + 0, :] = u[1] * P[2, :] - P[1, :]
        A[3 * i + 1, :] = -1 * u[0] * P[2, :] + P[0, :]
        A[3 * i + 2, :] = u[0] * P[1, :] - u[1] * P[0, :]
    print("MATRIX A\n", A)

    U, S_vec, Vh = np.linalg.svd(A)
    V = Vh.T

    X_homog = V[:, -1]  # final column of V: value for x where Ax is closest to 0
    X = X_homog[:3] / X_homog[3]  # homogoneous (4D) to non-homogenous (3D) coords
    min_sigma = S_vec[-1]  # minimum value of sigma - some metric of error?
    print("Min sigma", min_sigma)
    return X
