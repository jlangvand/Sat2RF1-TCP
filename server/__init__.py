import logging

"""
TCP
"""
import logging

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

logger = logging.getLogger()
stream_handler = logging.StreamHandler()
stream_formatter = logging.Formatter(LOG_FORMAT_STREAM)
stream_handler.setFormatter(stream_formatter)
file_handler = logging.FileHandler('../log')
file_formatter = logging.Formatter(LOG_FORMAT_FILE)
file_handler.setFormatter(file_formatter)
logger.addHandler(stream_handler)
logger.addHandler(file_handler)
logger.setLevel(LOG_LEVEL)
