import logging
import sys

import yaml

"""
TCP
"""

SETTINGS_PORT = 20201
DATA_PORT = 20202
HOSTNAME = "localhost"

"""
Logging
"""

LOG_FORMAT_STREAM = "%(asctime)s | %(levelname)s | %(message)s"
LOG_FORMAT_FILE = LOG_FORMAT_STREAM
LOG_FILE = "../logfile"
LOG_LEVEL = logging.INFO

LOG_TO_CONSOLE = True

logger = logging.getLogger()

if LOG_TO_CONSOLE:
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_formatter = logging.Formatter(LOG_FORMAT_STREAM)
    stream_handler.setFormatter(stream_formatter)
    logger.addHandler(stream_handler)

file_handler = logging.FileHandler('../log')
file_formatter = logging.Formatter(LOG_FORMAT_FILE)
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)
logger.setLevel(LOG_LEVEL)

"""
Config
"""

with open("config.yaml", 'r') as stream:
    try:
        config = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        logger.warning('Error in configuration file: %s', exc)
