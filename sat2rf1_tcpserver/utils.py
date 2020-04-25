"""
Assorted helper functions
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

from pathlib import Path

from time import time

from .kiss_constants import FESC, FESC_TFEND, FESC_TFESC, FEND, DATA_FRAME


def escape_special_codes(raw_codes):
    """
    Escape special codes, per KISS spec.

    "If the FEND or FESC codes appear in the data to be transferred, they
    need to be escaped. The FEND code is then sent as FESC, TFEND and the
    FESC is then sent as FESC, TFESC."
    - http://en.wikipedia.org/wiki/KISS_(TNC)#Description
    """
    return raw_codes.replace(
        FESC,
        FESC_TFESC
    ).replace(
        FEND,
        FESC_TFEND
    )


def recover_special_codes(escaped_codes):
    """
    Recover special codes, per KISS spec.

    "If the FESC_TFESC or FESC_TFEND escaped codes appear in the data received,
    they need to be recovered to the original codes. The FESC_TFESC code is
    replaced by FESC code and FESC_TFEND is replaced by FEND code."
    - http://en.wikipedia.org/wiki/KISS_(TNC)#Description
    """
    return escaped_codes.replace(
        FESC_TFESC,
        FESC
    ).replace(
        FESC_TFEND,
        FEND
    )


def extract_ui(frame):
    """
    Extracts the UI component of an individual frame.

    :param frame: APRS/AX.25 frame.
    :type frame: str
    :returns: UI component of frame.
    :rtype: str
    """
    start_ui = frame.split(
        b''.join([FEND, DATA_FRAME]))
    end_ui = start_ui[0].split(b''.join([SLOT_TIME, UI_PROTOCOL_ID]))
    return ''.join([chr(x >> 1) for x in end_ui[0]])


def strip_df_start(frame):
    """
    Strips KISS DATA_FRAME start (0x00) and newline from frame.

    :param frame: APRS/AX.25 frame.
    :type frame: str
    :returns: APRS/AX.25 frame sans DATA_FRAME start (0x00).
    :rtype: str
    """
    return frame.lstrip(DATA_FRAME).strip()


def dump_packet(packet):
    data = packet[1]
    path = 'dumps'
    Path(path).mkdir(exist_ok=True)
    filename = '{}/{}.bin'.format(path, time())
    f = open(filename, 'wb')
    f.write(data)
    f.close()


def radio_error_code_handler(command, status):
    if command == SET_MODE:
        setting = 'mode'

    elif command == SET_FREQUENCY:
        setting = 'frequency'

    elif command == SET_POWER:
        setting = 'power'

    elif command == SET_CORR_COEF:
        setting = 'correlation coefficient'

    else:
        logger.error('Invalid command code')
        return

    if status == b'\x00':
        logger.info('Setting {} is OK'.format(setting))

    else:
        logger.error('Failed to set {}, error code {}'.format(setting, status))
