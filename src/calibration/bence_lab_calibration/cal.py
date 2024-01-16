import cv2
import numpy as np
from scipy.io import loadmat, savemat

# size of a single checkboard tile in mm
CHECKBOARD_SQUARE_SIZE_MM = 23

# number of internal points in the checkboard calibration pattern
# IMPORTANT NOTE: this is the # of internal vertices - which is 1 less than the # of squares in ea. direction
CHECKBOARD_VERTICIES_ROW = 6
CHECKBOARD_VERTICIES_COL = 9

# hard-coded locaiton of the calibration matrix - make sure this is configured before running
HARDCODED_MATRIX_LOCATION = "C:/data/calibration/calPyScratch.mat"
HARDCODED_MATRIX_OUTPUT_LOCATION = "C:/data/calibration/calPyScratchOut.mat"

print(f"Using calibration matrix location: {HARDCODED_MATRIX_LOCATION}")
print(f"Outputing calibration file to location: {HARDCODED_MATRIX_OUTPUT_LOCATION}")

m = loadmat(HARDCODED_MATRIX_LOCATION)
im = m["undistortedIms"][:]

# termination criteria (2 + 1, 30, 0.001)
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

# prepare object points, like (0,0,0), (1,0,0), (2,0,0) ...,(6,5,0)
objp = np.zeros((CHECKBOARD_VERTICIES_COL * CHECKBOARD_VERTICIES_ROW, 3), np.float32)
objp[:, :2] = (
    np.mgrid[0:CHECKBOARD_VERTICIES_COL, 0:CHECKBOARD_VERTICIES_ROW].T.reshape(-1, 2)
) * CHECKBOARD_SQUARE_SIZE_MM

# Arrays to store object points and image points from all the images.
objpoints = []  # 3d coordinates of checkboard vertex in real world (mm)
imgpoints = []  # 2d coordinates of checkboard vertex in image plane (mm)

print(f"Undistorted ims matrix shape: {im.shape}")

num_cameras = im.shape[3]

failed = False
failed_list = []
for i in range(num_cameras):
    img = cv2.UMat(im[:, :, :, i].squeeze())
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Find the chess board corners
    ret, corners = cv2.findChessboardCorners(
        img, (CHECKBOARD_VERTICIES_COL, CHECKBOARD_VERTICIES_ROW), None
    )

    print(f"Camera {i + 1}(matlab indicing) result:", ret)
    # If found, add object points, image points (after refining them)
    if ret:
        objpoints.append(objp)
        corners2 = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
        imgpoints.append(cv2.UMat.get(corners2))
        # Draw and display the corners
        img = cv2.drawChessboardCorners(
            img, (CHECKBOARD_VERTICIES_COL, CHECKBOARD_VERTICIES_ROW), corners2, ret
        )
        cv2.imshow("img", img)
        cv2.waitKey(500)
    else:
        print(f"Failed to find checkerboard in camera {i+1} (Matlab indexing)'")
        failed = True
        failed_list.append(i + 1)

if failed:
    raise Exception(
        f"Board not found in at least one image.\nFailed for cameras (matlab indicing): {failed_list}"
    )

# cv2.destroyAllWindows()

mdict = {"objPoints": objpoints, "imgPoints": imgpoints}

savemat(HARDCODED_MATRIX_OUTPUT_LOCATION, mdict)
