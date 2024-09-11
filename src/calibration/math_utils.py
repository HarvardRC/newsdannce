import logging
import numpy as np


def calculate_rpe(imgpoints, re_imgpoints):
    """Calculate average reprojection error from image points and re-projected image points"""
    norms = np.linalg.norm(imgpoints - re_imgpoints, axis=1)
    avg = np.mean(norms, axis=0)
    return avg


def triangulate(
    imgpoints: list[np.ndarray], view_matrices: list[np.ndarray]
) -> np.ndarray:
    """Triangulate a single point in 3D, for N_VIEWS views.

    Returns a 1D array of shape (3,) containing the X, Y, Z coordinates

    imgpoints is a list of length N_VIEWS, containing one point for each view. The point can be shape (2,) or (2,1).
    view_matrices is a list of length N_VIEWS containing one 3x4 matrix for each view.
    view
    """
    # imgpoints: list of either np.ndarray((2,1)) or np.ndarray((2,));
    #     of length n
    # view_matrices: 3x4 camera projection matrices for each view
    logging.info(
        f"imgpoints len: {len(imgpoints)}; imgpoints[0] shape: {imgpoints[0].shape}"
    )
    logging.info(
        f"view_matrices len {len(view_matrices)}; view_matrices[0] shape: {view_matrices[0].shape}"
    )

    assert len(imgpoints) == len(
        view_matrices
    ), "imgpoints and view_matrices must have the same length (first dimension size)"
    assert imgpoints[0].size == 2, "imgpoints must contain 2D elements"
    assert view_matrices[0].shape == (3, 4), "view_matrices must contain 3x4 elements"

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


def triangulate_all(imgpoints_all: np.ndarray, view_matrices: np.ndarray) -> np.ndarray:
    """Triangulate M points in 3D using N cameras/views.

    `imgpoints_all` must have shape: (N, M, 2)
    `view_matrices` must have shape: (N, 3, 4)


    Returns an array of worldpoints in the shape: (M, 3)
    """
    assert (
        imgpoints_all.shape[0] == view_matrices.shape[0]
    ), "imgpoints_all and view_matrices must have same # of views (same first dimension size)"
    n_cameras = imgpoints_all.shape[0]

    m_points = imgpoints_all.shape[1]

    # imgpoints: list of either np.ndarray((2,1)) or np.ndarray((2,));
    #     of length n
    # view_matrices: 3x4 camera projection matrices for each view
    worldpoint_out = np.zeros((m_points, 3))
    for i in range(m_points):
        this_impts = imgpoints_all[:, i, :]
        worldpoint_out[i, :] = triangulate(this_impts, view_matrices)
    return worldpoint_out


def triangulate_simple(points, camera_mats):
    num_cams = len(camera_mats)
    A = np.zeros((num_cams * 2, 4))
    for i in range(num_cams):
        x, y = points[i]
        mat = camera_mats[i]
        A[(i * 2) : (i * 2 + 1)] = x * mat[2] - mat[0]
        A[(i * 2 + 1) : (i * 2 + 2)] = y * mat[2] - mat[1]
    u, s, vh = np.linalg.svd(A, full_matrices=True)
    p3d = vh[-1]
    p3d = p3d[:3] / p3d[3]
    return p3d


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
