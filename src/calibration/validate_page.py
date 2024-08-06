import logging
import time
from pathlib import Path
import cv2

import numpy as np
import PySide6.QtWidgets as QtWidgets

# matplotlib tools
from matplotlib.backends.backend_qtagg import FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar

# from matplotlib.backends.qt_compat import QtWidgets
from matplotlib.figure import Figure

# from matplotlib.backends.qt_compat import QtWidgets
from PySide6.QtCore import Slot

from src.calibration.calibration_data import CalibrationData
from src.calibration.math_utils import triangulate
from src.calibration.project_utils import get_verification_files
from src.calibration.video_utils import load_image_or_video, ImageFormat


class CustomNavToolbar(NavigationToolbar):
    toolitems = [
        t for t in NavigationToolbar.toolitems if t[0] in ("Home", "Pan", "Zoom")
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class ValidationManager:
    """Provides context data and functions for running camera validation"""

    validation_image_paths: list[str]
    """list of len [n_cameras] where each entry is a path to the camera of that index used for calibration"""
    keypoints_2d: list[tuple[float, float]]
    """2D keypoints for each camera image, picked by the GUI"""
    scatter_paths: list
    """List of matplotlib paths used to redraw user-selected keypoints in gui"""
    static_axes: list
    """List of matplotlib axes for each of the n cameras"""
    calibration_data: CalibrationData

    def __init__(self, calibration_data: CalibrationData):
        n_cameras = calibration_data.n_cameras
        self.calibration_data = calibration_data
        self.validation_image_paths = [None for _ in range(n_cameras)]
        self.keypoints_2d = [None for _ in range(n_cameras)]
        self.scatter_paths = [None for _ in range(n_cameras)]
        self.reproj_paths = [None for _ in range(n_cameras)]
        self.static_axes = [None for _ in range(n_cameras)]
        self.output_dir = calibration_data.output_dir

    def load_image(self, img_path, camera_idx):
        """Load image by path for a particular camera and plot it on that camera's axes"""
        axes = self.static_axes[camera_idx]

        axes.clear()

        logging.debug(
            f"Loading image at filepath: {img_path} for camera idx: {camera_idx}"
        )
        try:
            # img = np.asarray(image_f)
            img = load_image_or_video(
                media_path=img_path, output_image_format=ImageFormat.RGB
            )
            # UNDISTORT THE IMAGE to undo lens distortions (e.g. radial, tangential dist parameters)
            img_undistorted = cv2.undistort(
                img,
                self.calibration_data.camera_params[camera_idx].camera_matrix,
                distCoeffs=self.calibration_data.camera_params[camera_idx].dist,
            )

            self.validation_image_paths[camera_idx] = img_path
            axes.imshow(img_undistorted)

        except Exception:
            logging.warning(f"Unable to load image at path: {img_path}")
            self.validation_image_paths[camera_idx] = None

        self.keypoints_2d[camera_idx] = None
        self.scatter_paths[camera_idx] = None
        axes.figure.canvas.draw()


def browse_validation_image(parentWidget, camera_idx, manager: ValidationManager):
    @Slot(None)
    def handleBrowse():
        filepath, _filter = QtWidgets.QFileDialog.getOpenFileName(
            parentWidget, "Select file", str(Path(manager.output_dir).parent)
        )
        manager.load_image(camera_idx=camera_idx, img_path=filepath)

    return handleBrowse


def browse_validation_folder(parentWidget, manager: ValidationManager):
    @Slot(None)
    def handleBrowse():
        dirpath = QtWidgets.QFileDialog.getExistingDirectory(
            parentWidget, "Select Folder", str(Path.home())
        )
        if dirpath is None or dirpath == "":
            logging.info("No file selected")
            return

        try:
            files = get_verification_files(
                dirpath, manager.calibration_data.camera_names
            )
        except Exception:
            logging.error("Unable to load verification files")
            return
        logging.debug(f"verification files to load: {files}")
        # try to load individual camera pictures from dirpath
        # e.g. "[dirpath/Camera1/0.jpg, ..., dirpath/Camera6/0.jpg]"
        for camera_idx in range(manager.calibration_data.n_cameras):
            manager.load_image(img_path=files[camera_idx], camera_idx=camera_idx)

    return handleBrowse


def setup_validation_window(
    root_frame: QtWidgets.QFrame, calibration_data: CalibrationData
):
    window = root_frame.window()
    layout = QtWidgets.QVBoxLayout(root_frame)

    camera_names = calibration_data.camera_names

    tab_widget = QtWidgets.QTabWidget()

    validation_manager = ValidationManager(calibration_data=calibration_data)

    load_all_button: QtWidgets.QPushButton = window.findChild(
        QtWidgets.QPushButton, "validation_loadAllButton"
    )
    validation_button: QtWidgets.QPushButton = window.findChild(
        QtWidgets.QPushButton, "runValidateButton"
    )

    for idx, name in enumerate(camera_names):
        camera_page = QtWidgets.QWidget()
        camera_page_layout = QtWidgets.QVBoxLayout()
        camera_page.setLayout(camera_page_layout)

        fig = Figure()
        static_canvas = FigureCanvas(fig)
        customNavToolbar = CustomNavToolbar(static_canvas, root_frame)
        camera_page_layout.setSpacing(0)
        camera_page_layout.addWidget(customNavToolbar)
        camera_page_layout.addWidget(static_canvas)
        static_ax = fig.subplots()
        validation_manager.static_axes[idx] = static_ax

        static_ax.get_xaxis().set_visible(False)
        static_ax.get_yaxis().set_visible(False)

        static_ax.margins(0)
        fig.tight_layout()

        add_image_button = QtWidgets.QPushButton(f"Select Image for {name}")
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(add_image_button)
        button_layout.addStretch()
        camera_page_layout.addSpacing(10)
        camera_page_layout.addLayout(button_layout)

        tab_widget.addTab(camera_page, name)

        # create all connections
        add_image_button.clicked.connect(
            browse_validation_image(window, idx, validation_manager)
        )

        def onclick_with_context(camera_idx, this_canvas, this_ax):
            """Binds important context variables to this instance of onclick"""

            def onclick(event):
                # NOTE: callback will use the most recent variable binding in loop unless provided in args
                # local_canvas = event.
                if event.canvas.toolbar.mode != "":
                    return
                if validation_manager.validation_image_paths[camera_idx] is None:
                    # don't allow markers if there is not a loaded image
                    return
                xdata = event.xdata
                ydata = event.ydata

                if xdata is None and ydata is None:
                    return
                scatter_path_new = this_ax.scatter(
                    np.array([xdata]), np.array([ydata]), 10, c="red"
                )

                validation_manager.keypoints_2d[camera_idx] = (xdata, ydata)
                scatter_path_old = validation_manager.scatter_paths[camera_idx]
                if scatter_path_old:
                    scatter_path_old.remove()
                validation_manager.scatter_paths[camera_idx] = scatter_path_new

                this_canvas.draw()

            return onclick

        cid = static_canvas.mpl_connect(
            "button_press_event",
            onclick_with_context(idx, this_canvas=static_canvas, this_ax=static_ax),
        )

    results_page = QtWidgets.QWidget()
    results_page_layout = QtWidgets.QVBoxLayout()
    results_page.setLayout(results_page_layout)

    results_label = QtWidgets.QLabel()
    results_label.setText(
        'Select a keypoint on each view, then click "Run Validation" to continue'
    )

    results_page_layout.addWidget(results_label)
    tab_widget.addTab(results_page, "Results")

    load_all_button.clicked.connect(
        browse_validation_folder(window, validation_manager)
    )

    validation_button.clicked.connect(
        lambda: do_validation_samethread(
            manager=validation_manager,
            tab_widget=tab_widget,
            results_label=results_label,
        )
    )

    layout.addWidget(tab_widget)


def do_validation_samethread(
    manager: ValidationManager,
    tab_widget: QtWidgets.QTabWidget,
    results_label: QtWidgets.QLabel,
):
    for point in manager.keypoints_2d:
        if point is None:
            logging.info("Must select a keypoint for all cameras")
            return

    start_time = time.time()

    image_pts = []
    proj_matrices = []

    for cam_idx in range(manager.calibration_data.n_cameras):
        image_pt = np.array(manager.keypoints_2d[cam_idx])
        proj_mtx = manager.calibration_data.camera_params[
            cam_idx
        ].make_projection_matrix()
        image_pts.append(image_pt)
        proj_matrices.append(proj_mtx)

    world_pt = triangulate(imgpoints=image_pts, view_matrices=proj_matrices)

    end_time = time.time()
    logging.info(
        f"Triangulation calculation took in {(end_time-start_time)*1000:.2f} ms"
    )

    reproj_errs = []

    for cam_idx in range(manager.calibration_data.n_cameras):
        this_ax = manager.static_axes[cam_idx]

        reproj_point = manager.calibration_data.camera_params[
            cam_idx
        ].project_world_point(world_point=world_pt)

        orig_point = np.array(manager.keypoints_2d[cam_idx])
        dist = np.linalg.norm(reproj_point - orig_point)
        reproj_errs.append(dist)
        logging.info(f"CAMERA IDX({cam_idx}) REPROJ NORM IS: {dist}")

        reproj_path_new = this_ax.scatter(
            np.array([reproj_point[0]]),
            np.array([reproj_point[1]]),
            s=10,
            c="b",
        )

        reproj_path_old = manager.reproj_paths[cam_idx]
        if reproj_path_old:
            reproj_path_old.remove()
        manager.reproj_paths[cam_idx] = reproj_path_new

        this_ax.figure.canvas.draw()

    avg_rpe = sum(reproj_errs) / len(reproj_errs)

    results_label.setText(
        f"Avg. Reprojection error: {avg_rpe:.2f} px\n\nClick on other camera tabs to see original keypoint (red dot) and reprojected point (blue dot)"
    )

    # show the final page which has results
    tab_widget.setCurrentIndex(manager.calibration_data.n_cameras)
