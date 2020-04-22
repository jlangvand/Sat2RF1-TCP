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
CONTINOUS_TRANSMIT_MODE = b'\x02'
TRANSMIT_IN_PROGRESS = b'\x03'
