from src.calibration.new.extrinsics import compute_extrinsics
from scipy.io import loadmat, savemat
import numpy as np

def test_compute_extrinsics():

    mat = loadmat("./src/calibration/new/test/test_data.mat")
    undistorted_images = mat["undistortedIms"]
    chessboard_cols = mat['param_chessboard_cols'][0][0]
    chessboard_rows = mat['param_chessboard_rows'][0][0]
    chessboard_square_mm = mat['param_chessboard_square_mm'][0][0]

    # will throw an exception if unable to find a chessboard in any image (no exception expected)
    maybe_object_vertex_coords, maybe_image_vertex_coords = compute_extrinsics(
        undistorted_images_rgb=undistorted_images,
        chessboard_rows=chessboard_rows,
        chessboard_cols=chessboard_cols,
        chessboard_square_mm=chessboard_square_mm,
        display_image=False
    )
    
    ### Sort maybe arrays
    maybe_combined = np.concatenate((maybe_object_vertex_coords, maybe_image_vertex_coords), axis=2)
    maybe_arg_order = np.expand_dims(np.argsort(maybe_combined[:, :, 0], axis=1), axis=2)
    maybe_combined_sorted = np.take_along_axis(maybe_combined, maybe_arg_order, axis=1)
    maybe_object_vertex_coords = maybe_combined_sorted[:, :, :3]
    maybe_image_vertex_coords = maybe_combined_sorted[:, :, 3:]

    # squeeze to remove additional dimension that legacy code expects (6, 54, 1, 2) => (6, 54, 2)
    true_object_vertex_coords = mat['true_objPoints']
    true_image_vertex_coords = mat['true_imgPoints'].squeeze()

    ### Sort true arrays
    # sort by x-coordinate of true coords. Make sure the comparison is order-invariant.
    # first combine the two arrays together
    true_combined = np.concatenate((true_object_vertex_coords, true_image_vertex_coords), axis=2)
    # argsort by x-coordinate then reshape back to original shape
    true_arg_order = np.expand_dims(np.argsort(true_combined[:, :, 0], axis=1), axis=2)
    true_combined_sorted = np.take_along_axis(true_combined, true_arg_order, axis=1)
    # sorted versions of original arrays
    true_image_vertex_coords = true_combined_sorted[:, :, 3:]
    true_object_vertex_coords = true_combined_sorted[:, :, :3]

    # should be obviously be equal unless chessboard generation code changes
    assert np.all(true_object_vertex_coords == maybe_object_vertex_coords)
    assert np.allclose(true_image_vertex_coords, maybe_image_vertex_coords, atol=0.01)
