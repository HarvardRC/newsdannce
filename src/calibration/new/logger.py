import datetime
import logging
import os
from pathlib import Path

# inititlize logger

is_initialized = False


def init_logger(log_level=logging.INFO, log_dir="./logs"):
    # disable matplotlib fontmanager logging:
    logging.getLogger("matplotlib.font_manager").disabled = True

    logger = logging.getLogger()

    # logging has not yet been initialized
    if not logger.hasHandlers():
        # create logging output directory if it does not exist
        Path(log_dir).mkdir(parents=True, exist_ok=True)

        logger.setLevel(logging.NOTSET)

        date_fmt = "%H:%M:%S"

        # log to stdout
        stdout_fmt = "%(message)s"
        stdout_handler = logging.StreamHandler()
        stdout_handler.setLevel(log_level)
        stdout_handler.setFormatter(logging.Formatter(stdout_fmt, date_fmt))
        logger.addHandler(stdout_handler)

        # log to file
        logfile_fmt = (
            "%(asctime)s [%(levelname)s] (%(filename)s:%(lineno)2d) %(message)s"
        )
        date_prefix = datetime.datetime.now().strftime("%Y%M%d_%H%M%S")
        logfile_name = f"calibrate_{date_prefix}.out"
        logfile_path = os.path.join(log_dir, logfile_name)
        logfile_handler = logging.FileHandler(logfile_path)
        # log all messages to the file
        logfile_handler.setLevel(logging.DEBUG)
        logfile_handler.setFormatter(logging.Formatter(logfile_fmt, date_fmt))
        logger.addHandler(logfile_handler)

        logger.info(f"logging initiliazed with log level: {log_level}")
        logger.info(f"Started at {datetime.datetime.now()}")
        logger.debug(f"Log file: {logfile_path}")
