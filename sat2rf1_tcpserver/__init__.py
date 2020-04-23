# -*- coding: utf-8 -*-

"""
Init script for module sat2rf1_tcpserver
"""

#  Copyright (c) 2020 Orbit NTNU (http://orbitntnu.no)
#
#  Authors:
#  David Ferenc Bendiksen
#  Joakim Skogø Langvand <jlangvand@gmail.com>
#  Sander Aakerholt
#
#  This file is part of Sat2rf1-tcpserver.
#
#  Sat2rf1-tcpserver is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  Sat2rf1-tcpserver is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with Sat2rf1-tcpserver.  If not, see <https://www.gnu.org/licenses/>.

import logging
import sys

import yaml

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
logger.setLevel(logging.DEBUG)

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

if config['logging']['log_to_console']:
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_formatter = logging.Formatter(config['logging']['console_format'])
    stream_handler.setFormatter(stream_formatter)
    logger.addHandler(stream_handler)
