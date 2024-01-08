import cv2 
import numpy as np
from scipy.io import loadmat,savemat
import scipy.misc

m = loadmat('C:/data/calibration/calPyScratch.mat')
im = m['undistortedIms'][:]

# termination criteria
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

# prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
objp = np.zeros((6*9,3), np.float32)
objp[:,:2] = np.mgrid[0:9,0:6].T.reshape(-1,2)*23

# Arrays to store object points and image points from all the images.
objpoints = [] # 3d point in real world space
imgpoints = [] # 2d points in image plane.
print(im.shape)
failed = False
for i in range(im.shape[3]):
    img = cv2.UMat(im[:,:,:,i].squeeze())
    img = cv2.cvtColor(img,cv2.COLOR_RGB2BGR)

    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)

    # Find the chess board corners
    ret, corners = cv2.findChessboardCorners(img, (9,6), None)
    print(ret)
    # If found, add object points, image points (after refining them)
    if ret:
        objpoints.append(objp)
        corners2 = cv2.cornerSubPix(gray,corners,(11,11),(-1,-1),criteria)
        imgpoints.append(cv2.UMat.get(corners2))
        # Draw and display the corners
        img = cv2.drawChessboardCorners(img, (9,6), corners2,ret)
        cv2.imshow('img', img)
        cv2.waitKey(500)
    else:
        print('Failed to find checkerboard in camera %d (Matlab indexing)' % (i + 1))
        failed = True

if failed:
    raise Exception('Board not found in at least one image.')

# cv2.destroyAllWindows()

mdict = {"objPoints": objpoints, "imgPoints": imgpoints}
savemat('C:/data/calibration/calPyScratchOut.mat',mdict)
