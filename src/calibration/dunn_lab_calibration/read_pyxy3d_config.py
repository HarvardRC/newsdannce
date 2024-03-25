import toml
import os
import cv2
import numpy as np
import matplotlib.pyplot as plt


class Camera:
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


class CameraParameters:
    def __init__(self, pyxy_config_path, points_path=None, laser_path=None):
        self.config_path = pyxy_config_path
        self.points_path = points_path
        self.laser_path = laser_path
        self.cameras = {}
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(
                f"Base config file {self.config_path} does not exist"
            )

    def get_parameters(self):
        with open(self.config_path, "r") as f:
            config = toml.load(f)

        n_cams = 0
        for section_name in config.keys():
            if section_name.startswith("cam"):
                n_cams += 1
                cam = Camera()
                cam.cam_matrix = config[section_name]["matrix"]
                cam.dist = config[section_name]["distortions"]
                cam.rvec = config[section_name]["rotation"]
                cam.tvec = config[section_name]["translation"]
                cam.exposure = config[section_name]["exposure"]
                cam.resolution = config[section_name]["verified_resolutions"][0]
                self.cameras[section_name] = cam

        print("# of cameras loaded:", n_cams)

    def get_points(self):
        with open(self.points_path, "r") as f:
            points_file = toml.load(f)

        img_points = np.array(points_file["img"])
        obj_points = np.array(points_file["obj"])
        camera_indices = np.array(points_file["camera_indices"])
        obj_indices = np.array(points_file["obj_indices"])

        n_cameras = len(self.cameras)

        img_points = [[] for _ in range(n_cameras)]
        obj_points = [[] for _ in range(n_cameras)]
        points_indices = [[] for _ in range(n_cameras)]

        for point_idx, point in enumerate(img_points):
            # index of the camera corresponding to this image point
            cam_idx = camera_indices[point_idx]
            img_points[cam_idx].append(point)
            # index of the 3d point (object point) corresponding to this image point
            obj_idx = obj_indices[point_idx]
            points_indices[cam_idx].append(obj_idx)
            obj_points[cam_idx].append(obj_points[obj_idx])

        for camera_idx, key in enumerate(self.cameras.keys()):
            self.cameras[key].img_points = img_points[camera_idx]
            self.cameras[key].obj_points = obj_points[camera_idx]
            self.cameras[key].points_indices = points_indices[camera_idx]

        print("Points are loaded")

    def get_laser_points(self):
        n_cams = len(self.cameras)

        video_path = [
            os.path.join(self.laser_path, f"Camera{i+1}", "0.mp4")
            for i in range(n_cams)
        ]

        for i, camera_name in enumerate(self.cameras.keys()):
            self.cameras[camera_name] = find_2d_center_argmax(video_path[i], self.cameras[camera_name])
            print(f"{len(self.cameras[camera_name].img_points)} points are found for {camera_name}")

    def compute(self):
        self.get_parameters()
        if self.points_path and self.laser_path:
            raise ValueError("Both points_path and laser_path provided")
        elif self.points_path and not self.laser_path:
            print("Computing positions from points_path file")
            self.get_points()
        elif not self.points_path and self.laser_path:
            print("Computing positions using laser_points video")
            self.get_laser_points()
        else:
            raise ValueError("must provide either points_path or laser_path")


def find_2d_center(video_path, camera: Camera, down_sample=5):
    """Find the center of the red dot for (every 1 of #down_sample frames) in the video"""
    video_reader = cv2.VideoCapture(video_path)

    centers = []
    count_array = []
    count = -1
    while video_reader.isOpened():
        count += 1
        success, frame = video_reader.read()
        if count == 0:
            im_height, im_width, _ = frame.shape

        # loop over every 5th frame:
        if success and (count % down_sample == 0):
            # undistort the image
            mtx = np.array(camera.cam_matrix)
            dist = np.array(camera.dist)
            # scales the camera matrix so you keep information in the corners
            # roi = region of interest
            newcameramtx, _roi = cv2.getOptimalNewCameraMatrix(
                mtx, dist, (im_width, im_height), 1, (im_width, im_height)
            )
            img = cv2.undistort(frame, mtx, dist, None, newcameramtx)

            # find the center of the dot
            lower_red = np.array([230, 190, 190])
            upper_red = np.array([255, 255, 255])
            mask = cv2.inRange(img, lower_red, upper_red)
            red_dot = cv2.bitwise_and(img, img, mask=mask)
            red_dot = cv2.cvtColor(red_dot, cv2.COLOR_BGR2GRAY)
            if np.sum(red_dot) != 0:
                red_dot = np.where(red_dot != 0)
                center_dot = [
                    red_dot[1].mean(dtype=float),
                    red_dot[0].mean(dtype=float),
                ]
                count_array.append(count)
                centers.append(center_dot)

        elif not success:
            break

    video_reader.release()
    camera.img_points = centers
    camera.points_indices = count_array

    return camera


def find_2d_center_argmax(video_path, camera: Camera, down_sample=5):
    video_reader = cv2.VideoCapture(video_path)

    centers = []
    count_array = []
    count = -1
    while video_reader.isOpened():
        count += 1
        ret, frame = video_reader.read()
        if count == 0:
            im_height, im_weight, _ = frame.shape
        if ret and (count % down_sample == 0):
            # undistort the image
            mtx = np.array(camera.cam_matrix)
            dist = np.array(camera.dist)
            newcameramtx, roi = cv2.getOptimalNewCameraMatrix(
                mtx, dist, (im_weight, im_height), 1, (im_weight, im_height)
            )
            img = cv2.undistort(frame, mtx, dist, None, newcameramtx)
            # convert to gray scale
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            # find the dot with the maximum intensity
            max_intensity = np.max(gray)
            if max_intensity < 50:
                continue
            else:
                red_dot = np.unravel_index(np.argmax(gray, axis=None), gray.shape)
                center_dot = [
                    red_dot[1].mean(dtype=float),
                    red_dot[0].mean(dtype=float),
                ]
                count_array.append(count)
                centers.append(center_dot)

        elif not ret:
            break

    video_reader.release()
    camera.img_points = centers
    camera.points_indices = count_array

    return camera


if __name__ == "__main__":
    base_path = "/Users/caxon/olveczky/dannce_data/CalibrationDataFromJunyu"
    config_path = os.path.join(base_path, "camera_parameter", "config.toml")
    point_path = os.path.join(base_path, "camera_parameter", "point_estimates.toml")
    laser_path = os.path.join(base_path, "laser_calib_1")
    cam_params = CameraParameters(config_path, points_path=None, laser_path=laser_path)
    cam_params.compute()
    print(cam_params.cameras)
