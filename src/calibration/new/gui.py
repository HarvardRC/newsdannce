from PySide6.QtCore import QFile, QIODevice, Signal, Slot, QObject, QThread, QSettings
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import (
    QWidget,
    QProgressBar,
    QApplication,
    QMainWindow,
    QLineEdit,
    QPushButton,
    QFileDialog,
    QGroupBox,
    QComboBox,
    QSpinBox,
    QDoubleSpinBox,
    QStackedWidget,
)
import sys
from pathlib import Path
import logging

from src.calibration.new.calibrate import do_calibrate, CalibrationData
from src.calibration.new.validate import do_validate

from src.calibration.new.logger import init_logger

# constant enums representing "pick calibration method" comboBox
METHOD_IDX_CHESSBOARD = 0
METHOD_IDX_APRILTAG = 1
METHOD_IDX_CHARUCO = 2

# page indices for root stacked widget
PAGE_IDX_CALIBRATE = 0
PAGE_IDX_VALIDATE = 1

ORGANIZATION_NAME = "OlveczkyLab"
APPLICATION_NAME = "CalibrationGui"

settings = QSettings(ORGANIZATION_NAME, APPLICATION_NAME)


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


class ValidateWorker(QObject):
    finished = Signal(object)

    def __init__(self, **arg_dict):
        super().__init__()
        self.arg_dict = arg_dict

    def run(self):
        logging.debug(f"Running validation: Args: {self.arg_dict}")
        do_validate(**self.arg_dict)
        self.finished.emit("Too bad soo sad")


class CalibrationWindow(QMainWindow):
    calibration_data: CalibrationData = None

    def __init__(self):
        super().__init__()
        self.ui_file_name = "src/calibration/new/ui/calibration_stacked.ui"
        self.loadUi()
        # link self properties to useful widgets
        self.makeAliases()
        # python code additional GUI setup
        self.setInitialState()
        # set up all slots & signals
        self.makeConnections()

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
        # first page (CALIBRATE)
        self.root_widget_stacked: QStackedWidget = self.findByName("rootWidgetStacked")
        self.calibrate_button: QPushButton = self.findByName("calibrateButton")
        self.project_dir_edit: QLineEdit = self.findByName("projectDirEdit")
        self.project_dir_browse: QPushButton = self.findByName("projectDirBrowse")
        self.intrinsics_dir_edit: QLineEdit = self.findByName("intrinsicsDirEdit")
        self.intrinsics_dir_browse: QPushButton = self.findByName("intrinsicsDirBrowse")
        self.output_dir_browse: QPushButton = self.findByName("outputDirBrowse")
        self.output_dir_edit: QLineEdit = self.findByName("outputDirEdit")
        self.intrinsics_group_box: QGroupBox = self.findByName("intrinsicsGroupBox")
        self.pick_method: QComboBox = self.findByName("pickMethod")
        self.chessboard_rows: QSpinBox = self.findByName("chessboardRows")
        self.chessboard_cols: QSpinBox = self.findByName("chessboardColumns")
        self.chessboard_size: QDoubleSpinBox = self.findByName("squareSizeMM")
        self.progress_bar: QProgressBar = self.findByName("progressBar")

        # TODO: DEBUG ITEM REMOVE
        self.skip_calibration_button: QPushButton = self.findByName(
            "skipCalibrationButton"
        )
        self.skip_calibration_button.setVisible(False)

        # SECOND PAGE (VALIDATE)
        self.params_dir_edit: QLineEdit = self.findByName("paramsDirEdit")
        self.params_dir_browse: QPushButton = self.findByName("paramsDirBrowse")

        self.validate_dir_edit: QLineEdit = self.findByName("validateDirEdit")
        self.validate_dir_browse: QPushButton = self.findByName("validateDirBrowse")
        self.validate_button: QPushButton = self.findByName("validateButton")

        # mapping used to set/load widget state from settings
        self.mappings = []
        self.mappings.append(("project_dir", str, self.project_dir_edit))
        self.mappings.append(("intrinsics_dir", str, self.intrinsics_dir_edit))
        self.mappings.append(("output_dir", str, self.output_dir_edit))
        self.mappings.append(("chessboard_rows", int, self.chessboard_rows))
        self.mappings.append(("chessboard_cols", int, self.chessboard_cols))
        self.mappings.append(("chessboard_size", float, self.chessboard_size))

    def setInitialState(self):
        self.root_widget_stacked.setCurrentIndex(PAGE_IDX_CALIBRATE)
        """Set up any intitial state required to be done in python"""
        self.progress_bar.setVisible(False)

        for key, type, object in self.mappings:
            if settings.contains(key):
                setting_value = settings.value(key, type)
                print(
                    f"LOADING SETTING FOR {key} of type: {type}. Value to be loaded: {setting_value}"
                )
                if type == str:
                    object.setText(setting_value)
                elif type == int or type == float:
                    object.setValue(setting_value)
                else:
                    raise Exception(f"Not sure how to load setting of type: {type}")

    def makeConnections(self):
        """Connect all slots and signals"""
        # calibrate page
        self.calibrate_button.clicked.connect(self.handleCalibrate)
        self.project_dir_browse.clicked.connect(
            self.handleBrowseDirPartial(self.project_dir_edit, "Project")
        )
        self.intrinsics_dir_browse.clicked.connect(
            self.handleBrowseDirPartial(self.intrinsics_dir_edit, "Intrinsics")
        )
        self.output_dir_browse.clicked.connect(
            self.handleBrowseDirPartial(self.output_dir_edit, "Output")
        )

        # validate page
        self.validate_dir_browse.clicked.connect(
            self.handleBrowseDirPartial(self.validate_dir_edit, "Validation")
        )
        self.params_dir_browse.clicked.connect(
            self.handleBrowseDirPartial(self.params_dir_edit, "Parameter folder")
        )
        self.validate_button.clicked.connect(self.handleValidate)

        # DEBUG ITEMS : TODO: DEBUG METHOD REMOVE
        self.skip_calibration_button.clicked.connect(self.handleSkipCalibration)

    def checkCalibrationPage(self):
        if len(self.project_dir_edit.text()) == 0:
            return False
        if len(self.output_dir_browse.text()) == 0:
            return False
        if (
            self.intrinsics_group_box.isChecked()
            and len(self.intrinsics_dir_edit.text()) == 0
        ):
            return False
        if self.chessboard_size.value() < 1.0:
            return False
        return True

    def switchStackToVerificationPage(self):
        """Switch root stacked panel from the initial page (calibration) to the verification page.
        Does this gracefully and update with calibration data if provided"""
        self.root_widget_stacked.setCurrentIndex(PAGE_IDX_VALIDATE)

        if self.calibration_data:
            output_dir = self.calibration_data.output_dir
            self.params_dir_edit.setText(output_dir)

    @Slot(None)
    def handleSkipCalibration(self):
        self.switchStackToVerificationPage()

    @Slot(None)
    def handleCalibrate(self):
        valid = self.checkCalibrationPage()
        if not valid:
            return
        # disable the button immediately so it cannot be pressed multiple times
        self.calibrate_button.setEnabled(False)
        project_dir = self.project_dir_edit.text()
        intrinsics_dir = self.intrinsics_dir_edit.text()
        output_dir = self.output_dir_edit.text()
        use_existing_intrinsics = self.intrinsics_group_box.isChecked()
        method_idx = self.pick_method.currentIndex()
        method_options = {}

        if method_idx == METHOD_IDX_CHESSBOARD:
            method_name = "chessboard"
            # chessboard calibration
            method_options["rows"] = self.chessboard_rows.value()
            method_options["cols"] = self.chessboard_cols.value()
            method_options["square_size_mm"] = self.chessboard_size.value()

        elif method_idx == METHOD_IDX_APRILTAG:
            # april tag calibration
            method_name = "apriltag"

        elif method_idx == METHOD_IDX_CHARUCO:
            # charuco calirbation
            method_name = "charuco"

        else:
            # unsupported calibration method
            raise Exception(
                "Unsupported calibration index: pick_method.currentIndex. Check UI file."
            )

        settings.setValue("project_dir", project_dir)
        settings.setValue("intrinsics_dir", intrinsics_dir)
        settings.setValue("output_dir", output_dir)
        settings.setValue("chessboard_rows", method_options["rows"])
        settings.setValue("chessboard_cols", method_options["cols"])
        settings.setValue("chessboard_size", method_options["square_size_mm"])
        settings.setValue("method_idx", method_idx)

        self.progress_bar.setVisible(True)
        self.calibrateInThread(
            project_dir=project_dir,
            existing_intrinsics_dir=intrinsics_dir if use_existing_intrinsics else None,
            output_dir=output_dir,
            **method_options,
        )

    @Slot(None)
    def handleValidate(self):
        # briefly validate
        if len(self.validate_dir_edit.text()) == 0:
            logging.warning("Validate dir is empty: try again")
            return False

        if len(self.params_dir_edit.text()) == 0:
            logging.warning("Params dir is empty: try again")
            return False

        # disable the button immediately so it cannot be pressed multiple times
        self.validate_button.setEnabled(False)
        validate_dir = self.validate_dir_edit.text()
        params_dir = self.params_dir_edit.text()

        self.validateInThread(
            params_dir=params_dir,
            validate_dir=validate_dir,
            calibration_data=self.calibration_data,
        )

    @Slot(int)
    def reportProgress(self, pct: int):
        self.progress_bar.setValue(pct)

    @Slot(object)
    def handleCalibrateFinished(self, output_object):
        self.calibration_data = output_object["calibration_data"]

        logging.info("Calibration done")
        self.switchStackToVerificationPage()
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

    def validateInThread(self, **arg_dict):
        logging.warning("Trying to validate")
        if hasattr(self, "thread1"):
            raise Exception("Error: thread already exists [validation]")
        self.thread1 = QThread()
        self.worker = ValidateWorker(**arg_dict)
        self.worker.moveToThread(self.thread1)
        self.thread1.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread1.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread1.finished.connect(self.thread1.deleteLater)
        self.worker.finished.connect(self.handleValidateFinished)
        self.thread1.start()

    @Slot(None)
    def handleValidateFinished(self):
        logging.info("Validation done")
        logging.debug("Telling thread1 to quit after validation")
        self.thread1.quit()
        logging.debug("Waiting for thread1 to quit after validation")
        self.thread1.wait()
        logging.debug(
            "Killed thread1 and resuming main thread execution after validation"
        )
        del self.thread1

    def handleBrowseDirPartial(self, target_edit, name):
        """function generator for any QLineEdit widget to open a directory browse OS window"""

        @Slot(None)
        def _handleBrowseDir():
            folder_path = QFileDialog.getExistingDirectory(
                self,
                f"Select {name} Folder",
                # Open the user's home directory by default. This should work on mac/windows.
                str(Path.home()),
            )
            target_edit.setText(folder_path)

        return _handleBrowseDir


if __name__ == "__main__":
    init_logger()
    logging.info("Running as GUI")
    global loader
    loader = QUiLoader()
    app = QApplication([])
    window = CalibrationWindow()
    window.show()
    sys.exit(app.exec())
