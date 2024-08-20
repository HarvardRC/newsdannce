import numpy as np


def calculate_rpe(imgpoints, re_imgpoints):
    """Calculate average reprojection error from image points and re-projected image points"""
    norms = np.linalg.norm(imgpoints - re_imgpoints, axis=1)
    avg = np.mean(norms, axis=0)
    return avg


def triangulate(imgpoints, view_matrices) -> np.ndarray:
    """Returns a 1D array of shape (3,) containing the X, Y, Z coordinates"""
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

    U, S_vec, Vh = np.linalg.svd(A)
    V = Vh.T

    X_homog = V[:, -1]  # final column of V: value for x where Ax is closest to 0
    X = X_homog[:3] / X_homog[3]  # homogoneous (4D) to non-homogenous (3D) coords
    min_sigma = S_vec[-1]  # minimum value of sigma - some metric of error?
    return X


# new version fixes upside-down world points
def get_chessboard_coordinates(
    chessboard_rows: int, chessboard_cols: int, square_size_mm: float
) -> np.ndarray:
    """Return chessboard internal vertex coordinates for calibration.
    Assume that the origin of the chessboard is (0,0,0).

    Rows are y-coordinate
    Columns are the x-coordinate.
    Assume z is zero for chessboard plane.

    Returns a numpy array in the shape (#rows * #cols, 3), scaled by square_size_mm.

    E.g. np.ndarray(
        [0,0,0],
        [1,0,0],
        ...
        [5,0,0],
        [0,1,0],
        ...
        [5,8,0]
    )

    Args:
        square_size_mm: size of each square in mm
        chessboard_rows: number of rows of internal verticies in the chessboard (1 - # squares in a row)
        chessboard_cols: number of columns of internal verticies in the chessboard (1 - # squares in a columns)
    """
    x = np.repeat(np.arange(0, chessboard_rows), chessboard_cols)  # [a a b b c c ...]
    y = np.tile(np.arange(0, chessboard_cols), chessboard_rows)  # [a b c ... a b c ...]
    z = np.zeros(chessboard_rows * chessboard_cols)

    return np.column_stack((x, y, z)).astype(np.float32) * square_size_mm
