"""
Enum for radio settings. To be implemented.
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
from sat2rf1_tcpserver.sat2rf1_constants import *

DIR_TO_RADIO = 0
DIR_FROM_RADIO = 1


class Sat2rf1Command:
    data_type = dict({Commands.SET_FREQUENCY: (False, 32),
                      Commands.GET_FREQUENCY: (False, 32),
                      Commands.SET_POWER: (True, 8),
                      Commands.GET_POWER: (True, 8),
                      Commands.GET_RSSI: (False, 8),
                      Commands.PING: (False, 32),
                      Commands.SET_CORR_COEF: (False, 8),
                      Commands.GET_CORR_COEF: (False, 8),
                      Commands.SET_MODE: (False, 8),
                      Commands.GET_MODE: (False, 8)})

    # Response to SET_* is always uint8

    def __init__(self, command=DATA_FRAME, data=b''):
        self.command = command
        self.data = data

    def decode(self):
        return int.from_bytes(self.data, )

    @staticmethod
    def decode_uint8(value):
        int.from_bytes(value, False)
