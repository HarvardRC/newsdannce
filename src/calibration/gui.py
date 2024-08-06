import argparse
import logging
import sys
from enum import Enum
from pathlib import Path
import signal

import numpy as np

# from matplotlib.backends.qt_compat import QtWidgets
from PySide6.QtCore import QFile, QIODevice, QObject, QSettings, QThread, Signal, Slot
from PySide6.QtGui import QFont
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import (
    QApplication,
    QDoubleSpinBox,
    QFileDialog,
    QFrame,
    QLabel,
    QLineEdit,
    QMainWindow,
    QProgressBar,
    QPushButton,
    QSpinBox,
    QStackedWidget,
    QTextBrowser,
    QWidget,
)

from src.calibration.validate_page import setup_validation_window
from src.calibration.calibrate import CalibrationData, do_calibrate
from src.calibration.logger import init_logger
from src.calibration.report_utils import get_calibration_report


class GuiPage(Enum):
    CALIBRATE = 0
    CALIBRATE_FINISHED = 1
    VALIDATE = 2


ORGANIZATION_NAME = "OlveczkyLab"
APPLICATION_NAME = "CalibrationGui"

# path the QT Designer UI file
UI_FILE_NAME = "src/calibration/ui_files/calibration.ui"

settings = QSettings(ORGANIZATION_NAME, APPLICATION_NAME)

# close application immediately on SIGINT (CTRL + C)
signal.signal(signal.SIGINT, signal.SIG_DFL)


class CalibrateWorker(QObject):
    finished = Signal(object)
    progress = Signal(int)

    def __init__(self, **arg_dict):
        super().__init__()
        self.arg_dict = arg_dict

    def run(self):
        logging.debug(f"Running calibration: Args: {self.arg_dict}")
        calibration_data = do_calibrate(
            on_progress=lambda pct: self.progress.emit(pct), **self.arg_dict
        )
        self.finished.emit({"calibration_data": calibration_data})


class CalibrationWindow(QMainWindow):
    calibration_data: CalibrationData = None

    def __init__(self):
        super().__init__()
        self.ui_file_name = UI_FILE_NAME
        self.loadUi()
        # link self properties to useful widgets
        self.makeAliases()
        # set up all slots & signals
        self.makeConnections()
        # python code additional GUI setup
        self.setInitialState()

    def findByName(self, object_name):
        """Find an child object by name (matches all objects)
        Assume all names are unique
        Throw an error if the widget is not found"""
        widget = self.findChild(QWidget, object_name)
        if widget is None:
            raise Exception(f"Widget not found with objectName=<{object_name}>")
        return widget

    def loadUi(self):
        ui_file = QFile(self.ui_file_name)
        if not ui_file.open(QIODevice.ReadOnly):
            logging.critical(
                f"Cannot open {self.ui_file_name}: {ui_file.errorString()}"
            )
            sys.exit(-1)
        loader.load(ui_file, self)
        ui_file.close()

    def makeAliases(self):
        """Link all important widgets to aliases on the main app object"""
        # CALIBRATE PAGE:
        self.root_widget_stacked: QStackedWidget = self.findByName("rootWidgetStacked")
        self.calibrate_button: QPushButton = self.findByName("calibrateButton")
        # Parameter Output Directory
        self.output_dir_edit: QLineEdit = self.findByName("paramOutEdit")
        self.output_dir_browse: QPushButton = self.findByName("paramOutBrowse")
        # Intrinsics Directory
        self.intrinsics_dir_edit: QLineEdit = self.findByName("intrinsicsDirEdit")
        self.intrinsics_dir_browse: QPushButton = self.findByName("intrinsicsDirBrowse")
        # Extrinsics Directory
        self.extrinsics_dir_edit: QLineEdit = self.findByName("extrinsicsDirEdit")
        self.extrinsics_dir_browse: QPushButton = self.findByName("extrinsicsDirBrowse")
        # Calibration Target Parameters
        self.chessboard_rows: QSpinBox = self.findByName("chessboardRows")
        self.chessboard_cols: QSpinBox = self.findByName("chessboardColumns")
        self.chessboard_size: QDoubleSpinBox = self.findByName("squareSizeMM")
        self.progress_bar: QProgressBar = self.findByName("progressBar")

        # TODO: DEBUG ITEM REMOVE
        self.skip_calibration_button: QPushButton = self.findByName(
            "skipCalibrationButton"
        )
        self.skip_calibration_button.setVisible(False)

        # CALIBRATION FINISHED PAGE:
        self.calibration_log: QTextBrowser = self.findByName("calibrationLog")
        self.calibration_report: QLabel = self.findByName("calibrationReport")
        self.continue_to_validation_button: QPushButton = self.findByName(
            "continueToValidationButton"
        )

        # Validation Page
        self.image_frame: QFrame = self.findByName("imageWidget")

        # mapping used to set/load widget state from settings
        self.mappings = []
        self.mappings.append(("extrinsics_dir", str, self.extrinsics_dir_edit))
        self.mappings.append(("intrinsics_dir", str, self.intrinsics_dir_edit))
        self.mappings.append(("output_dir", str, self.output_dir_edit))
        self.mappings.append(("chessboard_rows", int, self.chessboard_rows))
        self.mappings.append(("chessboard_cols", int, self.chessboard_cols))
        self.mappings.append(("chessboard_size", float, self.chessboard_size))

    def setInitialState(self):
        self.root_widget_stacked.setCurrentIndex(GuiPage.CALIBRATE.value)
        """Set up any intitial state required to be done in pytho vn"""
        self.progress_bar.setVisible(False)
        monofont = QFont("Monospace")
        monofont.setStyleHint(QFont.StyleHint.Monospace)
        self.calibration_log.setFont(monofont)

        try:
            for key, type, object in self.mappings:
                if settings.contains(key):
                    setting_value = settings.value(key, type)
                    logging.debug(
                        f"LOADING SETTING FOR {key} of type: {type}. Value to be loaded: {setting_value}"
                    )
                    if type == str:
                        object.setText(setting_value)
                    elif type == int:
                        object.setValue(int(setting_value))
                    elif type == float:
                        object.setValue(float(setting_value))
                    elif type == bool:
                        object.setChecked(setting_value)
                    else:
                        raise Exception(f"Not sure how to load setting of type: {type}")
        except Exception:
            logging.error("Unable to load previous settings. Clearing settings.")
            settings.clear()

    def makeConnections(self):
        """Connect all slots and signals. E.g. Button presses, etc."""
        # calibrate page
        self.calibrate_button.clicked.connect(self.handleCalibrate)

        self.output_dir_browse.clicked.connect(
            self.handleBrowseDirPartial(self.output_dir_edit, "Parameter Output")
        )
        self.intrinsics_dir_browse.clicked.connect(
            self.handleBrowseDirPartial(self.intrinsics_dir_edit, "Intrinsics")
        )
        self.extrinsics_dir_browse.clicked.connect(
            self.handleBrowseDirPartial(self.extrinsics_dir_edit, "Extrinsics")
        )

        self.continue_to_validation_button.clicked.connect(self.handleGoToValidatePage)

    def checkCalibrationPage(self):
        if len(self.output_dir_edit.text()) == 0:
            return False
        if len(self.intrinsics_dir_edit.text()) == 0:
            return False
        if len(self.extrinsics_dir_edit.text()) == 0:
            return False
        if self.chessboard_size.value() < 1.0:
            return False
        return True

    def switchStackToCalibrationFinishedPage(self):
        """Switch root stacked panel from the initial page (calibration) to the verification page.
        Does this gracefully and update with calibration data if provided"""
        self.root_widget_stacked.setCurrentIndex(GuiPage.CALIBRATE_FINISHED.value)

    def switchStackToValidatePage(self):
        self.root_widget_stacked.setCurrentIndex(GuiPage.VALIDATE.value)
        setup_validation_window(
            self.image_frame, calibration_data=self.calibration_data
        )

    @Slot(None)
    def handleGoToValidatePage(self):
        self.switchStackToValidatePage()

    @Slot(None)
    def handleSkipCalibration(self):
        self.switchStackToCalibrationFinishedPage()

    @Slot(None)
    def handleCalibrate(self):
        valid = self.checkCalibrationPage()
        if not valid:
            return
        # disable the button immediately so it cannot be pressed multiple times
        self.calibrate_button.setEnabled(False)
        intrinsics_dir = self.intrinsics_dir_edit.text()
        extrinsics_dir = self.extrinsics_dir_edit.text()
        output_dir = self.output_dir_edit.text()

        method_options = {}

        # chessboard calibration
        method_options["rows"] = self.chessboard_rows.value()
        method_options["cols"] = self.chessboard_cols.value()
        method_options["square_size_mm"] = self.chessboard_size.value()

        settings.setValue("extrinsics_dir", extrinsics_dir)
        settings.setValue("intrinsics_dir", intrinsics_dir)
        settings.setValue("output_dir", output_dir)
        settings.setValue("chessboard_rows", method_options["rows"])
        settings.setValue("chessboard_cols", method_options["cols"])

        settings.setValue("chessboard_size", method_options["square_size_mm"])

        self.progress_bar.setVisible(True)
        self.calibrateInThread(
            intrinsics_dir=intrinsics_dir,
            extrinsics_dir=extrinsics_dir,
            output_dir=output_dir,
            **method_options,
        )

    @Slot(int)
    def reportProgress(self, pct: int):
        self.progress_bar.setValue(pct)

    @Slot(object)
    def handleCalibrateFinished(self, output_object):
        self.calibration_data = output_object["calibration_data"]

        logging.info("Calibration done")
        self.switchStackToCalibrationFinishedPage()

        logs_text = logging.getLogger().log_stream.getvalue()

        self.calibration_log.setText(logs_text)
        report_text = get_calibration_report().make_summary()
        self.calibration_report.setText(report_text)

        logging.debug("Telling thread1 to quit after calibration")
        self.thread1.quit()
        logging.debug("Waiting for thread1 to quit after calibration")
        self.thread1.wait()
        logging.debug(
            "Killed thread1 and resuming main thread execution after calibrate"
        )
        del self.thread1
        del self.worker

    def calibrateInThread(self, **arg_dict):
        if hasattr(self, "thread1"):
            raise Exception("Error: Calibration thread already exists")
        self.thread1 = QThread()
        self.worker = CalibrateWorker(**arg_dict)
        self.worker.moveToThread(self.thread1)
        self.thread1.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread1.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread1.finished.connect(self.thread1.deleteLater)
        self.worker.progress.connect(self.reportProgress)
        self.worker.finished.connect(self.handleCalibrateFinished)
        self.thread1.start()

    def handleBrowseDirPartial(self, target_edit, name, default_dir=None):
        """function generator for any QLineEdit widget to open a directory browse OS window"""

        @Slot(None)
        def _handleBrowseDir():
            # default to current value of field if not specified
            if default_dir is None:
                new_default_dir = target_edit.text()
            else:
                new_default_dir = default_dir
            # try to load deafult_dir, if it does not exist then deafult to user's home directory
            if (
                new_default_dir is None
                or new_default_dir == ""
                or not Path(new_default_dir).is_dir()
            ):
                new_default_dir = str(Path.home())

            folder_path = QFileDialog.getExistingDirectory(
                self,
                f"Select {name} Folder",
                # Open the user's home directory by default. This should work on mac/windows.
                default_dir,
            )
            if folder_path is not None and folder_path != "":
                target_edit.setText(folder_path)

        return _handleBrowseDir


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", action="store_true", default=False)
    args = parser.parse_args()

    init_logger(log_level=logging.DEBUG if args.verbose else logging.INFO)

    logging.info("Running as GUI")
    global loader
    loader = QUiLoader()
    app = QApplication([])
    window = CalibrationWindow()
    window.setWindowTitle("DANNCE Calibration GUI")
    # start window as a larger size inititally
    window.resize(1200, 900)
    window.show()
    sys.exit(app.exec())
