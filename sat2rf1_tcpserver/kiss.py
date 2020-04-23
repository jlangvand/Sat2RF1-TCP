"""
Kiss interface script for the Sat2RF1 radio module
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

import logging

import serial

from sat2rf1_tcpserver import logger
from sat2rf1_tcpserver.kiss_constants import *
from sat2rf1_tcpserver.utils import escape_special_codes, recover_special_codes


class Kiss:
    """
    Defines new KISS interface.
    """

    def __init__(self, port, baud, timeout):
        self.interface = serial.Serial(port=port, baudrate=baud, timeout=timeout)
        logging.info('Connected to radio')

        # TODO: Add some kind of queue for read and write here
        self.write_queue = []
        self.decoded_frames = []

    # TODO: Rename this to create_frame() or something.
    def create_frame(self, setting, value):  # Renamed from write_setting(...) to create_frame(...)
        """
        Writes a specific setting and appends it to the write que.

        ???This is also used to transmit data by using the DATA setting???.
        """
        logger.debug('Constructing a frame with header [{}] and value [{}]...'.format(setting, value))

        frame = b''.join([
            FEND,  # First header
            setting,  # What setting should be sent to the radio
            escape_special_codes(value),
            # Used to change data that looks like FEND's to something else to ensure the frame isn't cut to early
            FEND  # Last header
        ])

        logger.debug('Frame: [{}]\nTest: [{}]'.format(frame, FEND + setting + escape_special_codes(value) + FEND))

        # TODO: Remove this interface and write to queue instead
        # self.interface.write(frame)
        logger.debug('Adding frame to queue: {}'.format(frame))
        self.write_queue.append(frame)
        return frame

        # TODO: Don't read from radio here. This only expects one frame.
        # Read response from radio
        # Removes setting and returnes only error code
        # return self.readline().replace(setting, b'')

    # TODO: Renamed this. Has to handle reading multiple frames.
    def read_and_decode(self):
        """
        Returns single line response. Temporary?
        """
        frames = []
        read_buffer = bytes()

        try:
            response = self.interface.readline()  # returns a byte string

            if len(response) < 1:
                # logger.debug('No data found on interface')
                return

            logger.debug('Raw response: [{}]'.format(response))

            # Test redundancy

            if type(response) != type(bytes()):
                raise KissError("Respons != bytes(), will terminate.")

            split_data = response.split(FEND)  # Assumes that 'response' is a byte string
            fends = len(split_data)

            logger.debug('len(split_data) = {}'.format(len(split_data)))

            if fends == 1:
                logging.info("No FEND found, assuming the entire response is a partial frame")
                read_buffer += split_data[0]

            else:
                if split_data[0]:  # Response starts with an incomplete frame; concatenate and add frame
                    logging.info("End of frame found, joining this with incomplete frame in buffer")
                    frames.append(b''.join([read_buffer, split_data[0]]))
                    read_buffer = bytes()

                if fends >= 3:  # Handles one or more complete frames
                    logging.info("Two or more FENDs found, expecting at least one complete frame")
                    for i in range(1, fends - fends % 3):
                        if split_data[i]:
                            logging.info("Found a complete frame")
                            frames.append(split_data[i])

                if split_data[fends - 1]:  # Ends wih a partial frame; add to buffer
                    logging.info("Found an incomplete frame at end of response, adding this to buffer")
                    read_buffer += split_data[fends - 1]

            for ii in range(len(
                    frames)):  # Iterates trough the data in frames, recovers the special codes and appends the data to the decoded_frame list
                logging.info("Decoding and assembling frames")
                self.decoded_frames.append(recover_special_codes(frames[ii]))
                logger.debug('Added frame {}'.format(recover_special_codes(frames[ii])))

        except KissError as e:
            print(e)

    # TODO: Check this. not tested
    def write_frames_to_radio(self):
        logger.debug('{} frames in queue, writing to radio...'.format(len(self.write_queue)))
        for frame in self.write_queue:
            logger.debug('Writing frame [{}]'.format(repr(frame)))
            self.interface.write(frame)
        self.write_queue.clear()

    def write_and_return_response(self, frame):
        self.interface.write(frame)
        return self.interface.readline()

    # TODO: Rough scetch. Make this cleaner
    def main_loop(self):

        while True:
            if len(self.write_queue) == 0:
                self.read_and_decode()
            else:
                self.write_frames_to_radio()


class KissError(Exception):
    """Kiss Error."""
    # TODO: Logging (and error handling)
    pass
