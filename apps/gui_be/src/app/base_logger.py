import os
import logging
import sys
from pathlib import Path
import time
import math

# logger = logging.basicConfig(
#     level=logging.INFO,
#     format="%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s",
#     datefmt="%H:%M:%S",
# )

# logger = logging.getLogger("")
# logger.setLevel(logging.DEBUG)


# handler = logging.handlers.RotatingFileHandler(
#   filename=
logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger(__name__)

# logger.basicConfig(filename=LOG_FILE,
#                    filemode='a',
#                     format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
#                     datefmt='%H:%M:%S',
#                     level=logging.DEBUG)
