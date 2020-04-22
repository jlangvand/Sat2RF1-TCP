SERIAL_TIMEOUT = 0.01

DATA_FRAME = b'\x00'

FEND = b'\xC0'  # Marks START and END of a Frame
FESC = b'\xDB'  # Escapes FEND and FESC bytes within a frame

# Transpose Bytes: Used within a frame

# "Transpose FEND": An FEND after an FESC (within a frame)-
# Sent as FESC TFEND
TFEND = b'\xDC'
# "Transpose FESC": An FESC after an FESC (within a frame)-
# Sent as FESC TFESC
TFESC = b'\xDD'

# "FEND is sent as FESC, TFEND"
# 0xC0 is sent as 0xDB 0xDC
FESC_TFEND = b''.join([FESC, TFEND])

# "FESC is sent as FESC, TFESC"
# 0xDB is sent as 0xDB 0xDD
FESC_TFESC = b''.join([FESC, TFESC])

UI_PROTOCOL_ID = b'\xF0'  # TODO: Not sure if we need this anymore
SLOT_TIME = b'\x00'  # TODO: Not sure what this should do yet
