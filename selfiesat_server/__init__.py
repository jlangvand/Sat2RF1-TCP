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
Config
"""

with open("config.yaml", 'r') as stream:
    try:
        config = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        logging.error('Error in configuration file: %s', exc)

"""
Logging
"""

logger = logging.getLogger()
logger.setLevel(logging.INFO)

"""
Log to file
"""

file_handler = logging.FileHandler(config['logging']['file_path'])
file_formatter = logging.Formatter(config['logging']['file_format'])
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)

"""
Log to console
"""

if config['debug']['log_to_console']:
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_formatter = logging.Formatter(config['logging']['console_format'])
    stream_handler.setFormatter(stream_formatter)
    logger.addHandler(stream_handler)