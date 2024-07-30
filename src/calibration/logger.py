import datetime
import logging
import os
from pathlib import Path
import io


def init_logger(log_level=logging.INFO, log_dir="./logs"):
    """Initialize python logger and print data both to the terminal and ot the log files"""

    # disable matplotlib fontmanager logging (avoids log clutter at info level)
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
        # logger.logfile_path = logfile_path
        # log all messages to the file
        logfile_handler.setLevel(logging.DEBUG)
        logfile_handler.setFormatter(logging.Formatter(logfile_fmt, date_fmt))
        logger.addHandler(logfile_handler)

        # log to string buffer
        log_stream = io.StringIO()
        log_stream_handler = logging.StreamHandler(log_stream)
        log_stream_handler.setLevel(logging.INFO)
        logger.addHandler(log_stream_handler)
        logger.log_stream = log_stream

        logger.debug(f"logger initiliazed with log level: {log_level}")
        logger.debug(f"Log started at timestamp: {datetime.datetime.now()}")
        logger.debug(f"Log file: {logfile_path}")
