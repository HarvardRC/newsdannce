import cv2
import numpy as np
from scipy.io import loadmat, savemat

# termination criteria for subpixel corner detection -- constant for now
CORNER_TERMINATION_CRITERIA = (
    cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER,
    30,
    0.001,
)

## IMPORTANT NOTE: findChessboardCorners requires white space (like a 1 square thick, white border, wider is better)
# around board to make detection more robust! This might be a reason why detection was failing for some images.

def compute_extrinsics(
    undistorted_images_path,
    output_matrix_path,
    checkerboard_shape,
    checkerboard_size_mm,
):
    if len(checkerboard_shape) != 2:
        raise Exception("Checkerboard shape must be a 2-tuple E.g. (6, 9)")

    # number of internal points in the checkerboard calibration pattern
    # IMPORTANT NOTE: this is the # of internal vertices - which is 1 less than the # of squares in ea. direction
    CHECKERBOARD_VERTICIES_ROW = checkerboard_shape[0]
    CHECKERBOARD_VERTICIES_COL = checkerboard_shape[1]

    print("CHECKERBOARD SHAPE: ", checkerboard_shape, " ROWS: ", CHECKERBOARD_VERTICIES_ROW, " COLS: ", CHECKERBOARD_VERTICIES_COL, " SIZE: ", checkerboard_size_mm)

    print(f"Reading undistorated images from: {undistorted_images_path}")

    try:
        m = loadmat(undistorted_images_path)
        undistorted_images = m["undistortedIms"][:]
    except FileNotFoundError:
        raise Exception(
            f"Failed to load undistorted images from {undistorted_images_path}. File not found."
        )
    except KeyError:
        raise Exception(
            "Undistorted images file expected to contain field: 'undistortedIms' shape e.g. (1200, 1920, 3, #cameras))"
        )

    # checkerboard vertices without units
    # e.g. (0,0,0), (1,0,0), (2,0,0) ... (0,1,0) ... (3,4,0) ...
    object_points_nounit = np.zeros(
        (CHECKERBOARD_VERTICIES_COL * CHECKERBOARD_VERTICIES_ROW, 3), np.float32
    )
    object_points_nounit[:, 0:2] = (
        np.mgrid[0:CHECKERBOARD_VERTICIES_COL, 0:CHECKERBOARD_VERTICIES_ROW].T.reshape(
            -1, 2
        )
    ) 
    object_points_mm = object_points_nounit * checkerboard_size_mm

    # Arrays to store object points and image points from all the images.
    all_object_points = []  # 3d coordinates of checkerboard vertex in real world (mm)
    image_points = []  # 2d coordinates of checkerboard vertex in image plane (mm)

    num_cameras = undistorted_images.shape[3]

    failed_list = []

    for camera_idx in range(num_cameras):
        camera_name = f"Camera{camera_idx+1}"

        # assume image is stored in RGB format (e.g. from Matlab)
        img_rgb = cv2.UMat(undistorted_images[:, :, :, camera_idx].squeeze())
        img_bgr = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR)
        img_gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)

        # Find the chess board corners
        success, approx_corners = cv2.findChessboardCorners(
            img_bgr, checkerboard_shape, None
        )

        if success:
            print(f"Successfully found checkerboard in camera: {camera_name}")
            all_object_points.append(object_points_mm)

            # find subpixel coordinates
            corner_subpix_coords = cv2.cornerSubPix(
                img_gray,
                approx_corners,
                (checkerboard_size_mm // 2, checkerboard_size_mm // 2),
                (-1, -1),
                CORNER_TERMINATION_CRITERIA,
            )

            image_points.append(cv2.UMat.get(corner_subpix_coords))

            # Draw and display the corners
            img_with_pattern = cv2.drawChessboardCorners(
                img_bgr, checkerboard_shape, corner_subpix_coords, success
            )

            cv2.imshow(f"{camera_name} with pattern", img_with_pattern)
            cv2.waitKey(1000)
        else:  
            failed_list.append(camera_name)

    if len(failed_list) > 0:
        print(f"Failed to find checkerboard in {failed_list}")
        raise Exception(
            f"Board not found in at least one image.\nFailed for cameras: {failed_list}"
        )

    cv2.destroyAllWindows()
    mdict = {"objPoints": all_object_points, "imgPoints": image_points}
    print(f"Saving extrinsics to: {output_matrix_path}")
    savemat(output_matrix_path, mdict)

compute_extrinsics(
    undistorted_images_path="/Users/caxon/olveczky/dannce_data/test_chris_hannah/calPyScratch.mat",
    output_matrix_path="/Users/caxon/olveczky/dannce_data/test_chris_hannah/test_output.mat",
    checkerboard_shape=(6, 9),
    checkerboard_size_mm=23,
)
