# matplotlib tools
from matplotlib.backends.backend_qtagg import FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
import matplotlib as mpl
from matplotlib.axes import Axes
import logging

# from matplotlib.backends.qt_compat import QtWidgets
from PySide6.QtCore import QFile, QIODevice, QObject, QSettings, QThread, Signal, Slot

# from matplotlib.backends.qt_compat import QtWidgets
from matplotlib.figure import Figure
import PySide6.QtWidgets as QtWidgets

from src.calibration.calibration_data import CalibrationData

import numpy as np
from PIL import Image


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
    calibration_data: CalibrationData

    def __init__(self, calibration_data: CalibrationData):
        n_cameras = calibration_data.n_cameras
        self.calibration_data = calibration_data
        self.validation_image_paths = [None for _ in range(n_cameras)]
        self.keypoints_2d = [None for _ in range(n_cameras)]
        self.scatter_paths = [None for _ in range(n_cameras)]
        self.output_dir = calibration_data.output_dir


def browse_validation_image(
    parentWidget, camera_idx, manager: ValidationManager, axes: Axes
):
    @Slot(None)
    def handleBrowse():
        axes.clear()

        filepath, _filter = QtWidgets.QFileDialog.getOpenFileName(
            parentWidget, "Select file", manager.output_dir
        )
        print("FILEPATH IS <<<", filepath, ">>>")
        print("FILTER IS ", _filter)
        logging.debug(f"Selected filepath: {filepath} for camera idx: {camera_idx}")
        try:
            with Image.open(filepath) as image_f:
                img = np.asarray(image_f)
                manager.validation_image_paths[camera_idx] = filepath
                axes.imshow(img)

        except Exception:
            logging.warning(f"Unable to load image at path: {filepath}")
            manager.validation_image_paths[camera_idx] = None

        manager.keypoints_2d[camera_idx] = None
        manager.scatter_paths[camera_idx] = None
        axes.figure.canvas.draw()

    return handleBrowse


def setup_validation_window(root_frame, calibration_data: CalibrationData):
    layout = QtWidgets.QVBoxLayout(root_frame)

    camera_names = calibration_data.camera_names

    tab_widget = QtWidgets.QTabWidget()

    validation_manager = ValidationManager(calibration_data=calibration_data)

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

        static_ax.get_xaxis().set_visible(False)
        static_ax.get_yaxis().set_visible(False)

        static_ax.margins(0)
        fig.tight_layout()

        # path = image_paths[idx]
        # try:
        #     img = np.asarray(Image.open(path))
        # except Exception:
        #     img = [[1]]
        # static_ax.imshow(img)

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
            browse_validation_image(root_frame, idx, validation_manager, static_ax)
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
                print(f"CAMERA NAME/IDX: {camera_idx}")
                print("PLOTTED: ", xdata, ydata)

            return onclick

        cid = static_canvas.mpl_connect(
            "button_press_event",
            onclick_with_context(idx, this_canvas=static_canvas, this_ax=static_ax),
        )

    layout.addWidget(tab_widget)
