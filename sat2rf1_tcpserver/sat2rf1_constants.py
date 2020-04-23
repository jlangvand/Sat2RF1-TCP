"""
Constants used in the Sat2rf1 class
"""

#  Copyright (c) 2020 Orbit NTNU (http://orbitntnu.no)
#
#  Authors:
#  David Ferenc Bendiksen
#  Joakim Skogø Langvand <jlangvand@gmail.com>
#  Peter Uran
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
import enum

"""
SAT2RF1 commands from data sheet.
Strictly a part of the KISS protocol the radio employs,
but is unique for this radio and not part of the KISS module.
"""

DATA_FRAME = b'\x00'
SET_FREQUENCY = b'\x20'
GET_FREQUENCY = b'\x21'
SET_POWER = b'\x22'
GET_POWER = b'\x23'
GET_RSSI = b'\x24'
PING = b'\x25'
DEBUG = b'\x26'
SET_CORR_COEF = b'\x27'
GET_CORR_COEF = b'\x28'
SET_MODE = b'\x29'
GET_MODE = b'\x30'

"""
Carrier frequency limits
"""
LOWER_FREQUENCY_LIMIT = 430e6  # Hertz
UPPER_FREQUENCY_LIMIT = 440e6  # Hertz

"""
Transmitter operational modes
"""
PACKET_RECEIVE_MODE = b'\x00'
TRANSPARENT_RECEIVE_MODE = b'\x01'
CONTINUOUS_TRANSMIT_MODE = b'\x02'
TRANSMIT_IN_PROGRESS = b'\x03'


class Commands(enum.Enum):
    DATA_FRAME = b'\x00'
    SET_FREQUENCY = b'\x20'
    GET_FREQUENCY = b'\x21'
    SET_POWER = b'\x22'
    GET_POWER = b'\x23'
    GET_RSSI = b'\x24'
    PING = b'\x25'
    DEBUG = b'\x26'
    SET_CORR_COEF = b'\x27'
    GET_CORR_COEF = b'\x28'
    SET_MODE = b'\x29'
    GET_MODE = b'\x30'
