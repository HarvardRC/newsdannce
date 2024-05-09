import toml
import os
import cv2
import numpy as np
import matplotlib.pyplot as plt
from time import time

class Camera:

    amount = 0

    def __init__(self):
        self.cam_matrix = None
        self.dist = None
        self.rvec = None
        self.tvec = None
        self.exposure = None
        self.resolution = None
        self.img_points = None
        self.obj_points = None
        self.points_indices = None
        self.rpes = None
        self.extrinsic_opt = None
        Camera.amount += 1

    def __repr__(self):
        if self.cam_matrix and self.obj_points is None:
            output_message = f"""cam_matrix={self.cam_matrix},
                                dist={self.dist},
                                rvec={self.rvec},
                                tvec={self.tvec},
                                exposure={self.exposure},
                                resolution={self.resolution},
                                img_points={self.img_points},
                                point_indices = {self.points_indices}\n
                                obj_points={self.obj_points}\n"""
        else:
                        output_message = f"""cam_matrix={self.cam_matrix},
                                dist={self.dist},
                                rvec={self.rvec},
                                tvec={self.tvec},
                                exposure={self.exposure},
                                resolution={self.resolution},
                                length of img_points: {len(self.img_points)},
                                length of point_indices: {len(self.points_indices)},
                                length of obj_points: {len(self.obj_points)}\n"""
        return output_message

    def __del__(self):
        Camera.amount -= 1
        print("Camera is deleted, amount of cameras is ", Camera.amount)

class CameraParameters:
    def __init__(self, path, points_path=None, laser_path=None):
        self.path = path
        self.points_path = points_path
        self.laser_path = laser_path
        self.cameras = dict()
        if not os.path.exists(self.path):
            raise FileNotFoundError(f"Point Estimate File {self.path} does not exist")

    def get_parameters(self):
        with open(self.path, 'r') as f:
            config = toml.load(f)

        n_cams = 0
        for i in config.keys():
            if i.startswith('cam'):
                n_cams += 1
                cam = Camera()
                cam.cam_matrix = config[i]['matrix']
                cam.dist = config[i]['distortions']
                cam.rvec = config[i]['rotation']
                cam.tvec = config[i]['translation']
                cam.exposure = config[i]['exposure']
                cam.resolution = config[i]['verified_resolutions'][0]
                self.cameras[i] = cam

        print(f"Found {n_cams} cameras")
        print("Camera amount is ", Camera.amount)
        return 0

    def get_points(self):

        with open(self.points_path, 'r') as f:
            points_file = toml.load(f)

        img_points = points_file['img']
        obj_points = points_file['obj']
        camera_indices = points_file['camera_indices']
        obj_indices = points_file['obj_indices']

        points_2d = [list() for i in range(6)]
        points_3d = [list() for i in range(6)]
        points_indices = [list() for i in range(6)]

        for i, pts in enumerate(img_points):
            points_2d[camera_indices[i]].append(pts)
            index_3d_pts = obj_indices[i]
            points_indices[camera_indices[i]].append(index_3d_pts)
            points_3d[camera_indices[i]].append(obj_points[index_3d_pts])

        for i, key in enumerate(self.cameras.keys()):
            self.cameras[key].img_points = points_2d[i]
            self.cameras[key].obj_points = points_3d[i]
            self.cameras[key].points_indices = points_indices[i]

        print("Points are loaded")
        return 0

    def get_laser_points(self):
        n_cams = len(self.cameras)
        video_path = [os.path.join(self.laser_path, f"Camera{i+1}", "0.mp4") for i in range(n_cams)]
        for i, key in enumerate(self.cameras.keys()):
            self.cameras[key] = find_2d_center_argmax(video_path[i], self.cameras[key])
            print(f"{len(self.cameras[key].img_points)} points are found for {key}")

    def __call__(self):
        self.get_parameters()
        if self.points_path:
            self.get_points()
        elif self.points_path is None and self.laser_path is not None:
            self.get_laser_points()
        elif self.points_path is not None and self.laser_path is not None:
             raise ValueError("Both points_path and laser_path are not None")
        return 0


def find_2d_center(video_path, camera: Camera, down_sample=5):

    cap = cv2.VideoCapture(video_path)

    centers = []
    count_array = []
    count = -1
    while cap.isOpened():
        count += 1
        ret, frame = cap.read()
        if count == 0:
            im_height, im_weight, _ = frame.shape
        if ret and (count%down_sample == 0) :
            # undistort the image
            mtx = np.array(camera.cam_matrix)
            dist = np.array(camera.dist)
            newcameramtx, roi = cv2.getOptimalNewCameraMatrix(mtx, dist, (im_weight,im_height), 1, (im_weight,im_height))
            img = cv2.undistort(frame, mtx, dist, None, newcameramtx)
            # find the center of the dot
            lower_red = np.array([230, 190, 190])
            upper_red = np.array([255, 255, 255])
            mask = cv2.inRange(img, lower_red, upper_red)
            red_dot = cv2.bitwise_and(img, img, mask=mask)
            red_dot = cv2.cvtColor(red_dot, cv2.COLOR_BGR2GRAY)
            if np.sum(red_dot) != 0:
                red_dot = np.where(red_dot != 0)
                center_dot = [red_dot[1].mean(dtype=float), red_dot[0].mean(dtype=float)]
                count_array.append(count)
                centers.append(center_dot)

        elif not ret:
            break


    cap.release()
    camera.img_points = centers
    camera.points_indices = count_array

    return camera


def find_2d_center_argmax(video_path, camera: Camera, down_sample=5):

    cap = cv2.VideoCapture(video_path)

    centers = []
    count_array = []
    count = -1
    while cap.isOpened():
        count += 1
        ret, frame = cap.read()
        if count == 0:
            im_height, im_weight, _ = frame.shape
        if ret and (count%down_sample == 0) :
            # undistort the image
            mtx = np.array(camera.cam_matrix)
            dist = np.array(camera.dist)
            newcameramtx, roi = cv2.getOptimalNewCameraMatrix(mtx, dist, (im_weight,im_height), 1, (im_weight,im_height))
            img = cv2.undistort(frame, mtx, dist, None, newcameramtx)
            # convert to gray scale
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            # find the dot with the maximum intensity
            max_intensity = np.max(gray)
            if max_intensity < 50:
                continue
            else:
                red_dot = np.unravel_index(np.argmax(gray, axis=None), gray.shape)
                center_dot = [red_dot[1].mean(dtype=float), red_dot[0].mean(dtype=float)]
                count_array.append(count)
                centers.append(center_dot)

        elif not ret:
            break


    cap.release()
    camera.img_points = centers
    camera.points_indices = count_array

    return camera


if __name__ == "__main__":
    config_path = os.path.join("/Users/junyunan/Desktop/tDunn Lab/Laser_Validation/","2023_11_13","calib_to_cam5",'config.toml')
    point_path = os.path.join("/Users/junyunan/Desktop/tDunn Lab/Laser_Validation/","2023_11_13","calib_to_cam5",'point_estimates.toml')
    laser_path = os.path.join("/Users/junyunan/Desktop/tDunn Lab/Laser_Validation/","2023_11_13","laser_calib_1")
    cam_para = CameraParameters(config_path, points_path=None, laser_path=laser_path)
    cam_para()
    print(cam_para.cameras)
