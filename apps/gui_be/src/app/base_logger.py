import os
import logging
import sys
from pathlib import Path
import time
import math

filename = f"log-{math.floor(time.time())}"

logger = logging
# logger.basicConfig(stream=sys.stdout, level=logging.INFO)
ENV_INSTANCE_DIR = os.environ.get("INSTANCE_DIR")
LOG_DIR = Path(ENV_INSTANCE_DIR, "logs")
LOG_FILE= LOG_DIR.joinpath(f"{filename}")

logger.basicConfig(filename=LOG_FILE,
                   filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.DEBUG)

