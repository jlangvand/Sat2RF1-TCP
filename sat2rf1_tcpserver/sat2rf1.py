"""
Class providing higher level to the Sat2RF1 radio module
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

from sat2rf1_tcpserver import logger, config

from .kiss import Kiss, FEND
from .sat2rf1_constants import *

from .utils import recover_special_codes, escape_special_codes, radio_error_code_handler

# Define parameters for serial communication
baud = config['radio']['baud']
port = config['radio']['port']
serial_timeout = config['radio']['serial_timeout']

class Sat2rf1:
    """
    Class for interfacing with the Sat2rf1 radio.
    """

    def __init__(self):
        try:
            self.kiss = Kiss(port=port, baud=baud, timeout=serial_timeout)
        except FileNotFoundError as e:
            logger.error('Could not find radio! Make sure it is connected.')
            raise RadioError('Radio might not be connected: ' + e)

        self._packets_waiting = []
        self._response_waiting = []

        # Get some information about the radio...
        frames = []
        frames.append(self.__build_frame(command=GET_FREQUENCY))
        frames.append(self.__build_frame(command=GET_POWER))
        frames.append(self.__build_frame(command=GET_MODE))
        frames.append(self.__build_frame(command=GET_CORR_COEF))

        for frame in frames:
            self.__write_frame(frame)
            self.cycle()

    def set_frequency(self, freq):
        """
        Sets frequency of the radio in Hertz.
        """
        if freq < LOWER_FREQUENCY_LIMIT:
            raise RadioError("Frequency too low. Must be higher than " + str(int(LOWER_FREQUENCY_LIMIT / 1e6)) + " MHz")
        elif freq > UPPER_FREQUENCY_LIMIT:
            raise RadioError(
                "Frequency too high. Must be lower than " + str(int(UPPER_FREQUENCY_LIMIT / 1e6)) + " MHz")

        freq_in_bytes = int(freq).to_bytes(length=4, byteorder='big')  # freq must be int
        try:
            # response = self.kiss.write_setting(setting=SET_FREQUENCY, value=freq_in_bytes)
            response = self.kiss.create_frame(setting=SET_FREQUENCY, value=freq_in_bytes)
            response = int.from_bytes(response, 'big')

            if response != 0:
                raise RadioError("Could not set frequency! Error code " + str(response))

            else:
                logger.info('Set frequency to ' + str(int(freq / 1e6)) + ' MHz.')

        except RadioError as e:
            logger.error(e)

    def get_frequency(self):
        """
        Returns current carrier frequency.
        """
        try:
            # response = self.kiss.write_setting(setting=GET_FREQUENCY, value=b'00000000')
            response = self.kiss.create_frame(setting=GET_FREQUENCY, value=b'00000000')
            freq = int.from_bytes(response, 'big')
            logger.info("Frequency is " + str(int(freq / 1e6)) + " MHz")
            return freq
        except Exception as e:
            logger.error("Could not get frequency from radio. " + str(e))

    def send_string(self, data):
        pass

    def __set_radio_mode(self, mode):
        """
        Sets a transmitter mode
        """
        self.__write_frame(self.__build_frame(SET_MODE, mode))

    def set_packet_receive_mode(self):
        """
        The packet is detected when the specific carrier signal
        to noise ratio is exceeded (15 dB above noise in case of AX.25 packets)
        """
        logger.info("Setting radio to packet receive mode.")
        self.__set_radio_mode(mode=PACKET_RECEIVE_MODE)

    def set_transparent_receive_mode(self):
        """
        In packet mode, packet detection and de-coding is
        accomplished automatically by hardware. The packet mode is more
        sensitive compared to the transparent mode, however
        it is more susceptible to the interference cause by the noisy signals
        """
        logger.info("Setting radio to transparent mode.")
        self.__set_radio_mode(mode=TRANSPARENT_RECEIVE_MODE)

    def set_continous_transmit_mode(self):
        """
        For debugging. Emits a constant carrier wave with no data.
        """
        logger.info("Setting radio to continous transmit mode.")
        self.__set_radio_mode(mode=CONTINUOUS_TRANSMIT_MODE)

    def get_radio_mode(self):
        """
        Returns current radio mode.
        """
        try:
            # response = self.kiss.write_setting(setting=GET_MODE, value=b'00000000')
            response = self.kiss.create_frame(setting=GET_MODE, value=b'00000000')

            if response == PACKET_RECEIVE_MODE:
                logger.info("Radio is in packet receive mode.")
            elif response == TRANSPARENT_RECEIVE_MODE:
                logger.info("Radio is in transparent receive mode.")
            elif response == CONTINUOUS_TRANSMIT_MODE:
                logger.info("Radio is in continous transmit mode.")
            elif response == TRANSMIT_IN_PROGRESS:
                logger.info("Radio is in transmit in progress mode.")

            return response
        except Exception as e:
            logger.error("Could not get radio mode. " + str(e))

    # TODO: Rough scetch. Test this. Data transmission uses DATA setting from KISS.
    def transmit_data(self, data):
        """
        Pass data to the radio for transmission
        """
        logger.debug("Creating a frame with a payload of {} bytes".format(len(data)))
        self.kiss.create_frame(setting=DATA_FRAME, value=data)
        self.kiss.write_frames_to_radio()

        # try:
        # response = self.kiss.write_setting(setting=DATA, value=data)
        # response = self.kiss.create_frame(setting=DATA_FRAME, value=data)

        # TODO: Implement respons error check

        # response = int.from_bytes(response, 'big')
        # if response != 0:
        #    raise RadioError("Could not set transmitter mode.")
        # except RadioError as e:
        #    logger.error(e)

    # TODO: Get data from KISS interface. Then send data to socket or validate command.
    def read_data_from_interface(self):
        """
        Description.
        """

        if len(self.kiss.decoded_frames) != 0:
            data = self.kiss.decoded_frames.pop(0)
            command = data[0:1]
            data = data[1:len(data)]

            com_dat = (command, data)
        else:
            com_dat = None

        return com_dat

        # TODO: Might be implemented differently in the future
        # for data in self.kiss.decoded_frames:
        # if command == DATA_FRAME:
        #    pass # send data to socket or some other interface

        # else:

        # TODO: Implement validation of commands
        # self.validate_command(data)

    # TODO: Validate all commands written to the radio. Each command sends a error code back. Check these or throw an exception.
    # This means that all the other functions need thir response validation moved down here.
    def validate_command(self, response):
        # first check which command sent this
        if response.command_code == SET_FREQUENCY:
            if response != 0:
                raise RadioError("Could not set frequency! Error code " + str(response))

            else:
                logger.info('Set frequency to ' + str(int(freq / 1e6)) + ' MHz.')
                # TODO: Perhaps update some frquency variable so it is easy to access?
                self.carrier_frequency = freq

    def get_message(self):
        """
        Get the oldest message from the queue

        :return: tuple (command, message)
        """
        return self._packets_waiting.pop(0)

    def __get_frame(self):
        first_byte = self.kiss.interface.read(1)

        if not first_byte == FEND:
            logger.error('Frame desync! Returned frame might be incomplete')

        payload = self.kiss.interface.read_until(FEND)

        if payload[:1] == FEND:
            logger.error('Frame desync! Lost at least one frame from radio.')
            payload = self.kiss.interface.read_until(FEND)

        self.__unpack_and_stash_frame(payload)

    def __unpack_and_stash_frame(self, payload):
        payload = payload.replace(FEND, b'')
        payload = recover_special_codes(payload)
        package = payload[:1], payload[1:]
        if package[0] != b'\x00':
            self.__handle_response(package)
            self._response_waiting.append(package)
        else:
            self._packets_waiting.append(package)

    def __handle_response(self, package):
        command = package[0]
        argument = package[1]
        arg_int = int.from_bytes(argument, byteorder='big', signed=True)
        arg_uint = int.from_bytes(argument, byteorder='big', signed=False)

        if command == Commands.GET_FREQUENCY.value:
            logger.info('Frequency: {}Mhz'.format(arg_uint / 1e6))

        elif command == Commands.GET_POWER.value:
            logger.info('Transmit power: {}dBm'.format(arg_int))

        elif command == Commands.GET_MODE.value:
            self.__handle_get_mode(argument)

        elif command == GET_CORR_COEF:
            self.__handle_get_corr_coeff(arg_uint)

        elif command == GET_RSSI:
            logger.info('RSSI level of last transmission: {}dBm'.format(arg_int))

        elif command == SET_MODE or SET_POWER or SET_CORR_COEF or SET_FREQUENCY:
            radio_error_code_handler(command, argument)

        else:
            logger.error('Invalid command byte: {}'.format(command))

    def __handle_get_corr_coeff(self, arg_uint):
        threshold = 'low (more noise)'

        if arg_uint < 14:
            threshold = 'medium'

        if arg_uint < 10:
            threshold = 'high (less noise)'

        logger.info('Correlation coefficient: {}, should be considered as {}'.format(arg_uint, threshold))

    def __handle_get_mode(self, argument):
        if argument == PACKET_RECEIVE_MODE:
            mode = 'Packet receive mode'

        elif argument == TRANSPARENT_RECEIVE_MODE:
            mode = 'Transparent receive mode'

        elif argument == CONTINUOUS_TRANSMIT_MODE:
            mode = 'Continuous transmit (beacon) mode'

        elif argument == TRANSMIT_IN_PROGRESS:
            mode = 'Transmission in progress'

        else:
            mode = 'Error! (Malformed frame)'
            logger.error('Malformed message: {} {}'.format(package[0], package[1]))

        logger.info('Radio mode: {}'.format(mode))

    def __build_frame(self, command=b'\x00', data=b''):
        escape_special_codes(data)
        return FEND + command + data + FEND

    def __write_frame(self, frame):
        return self.kiss.interface.write(frame)

    def has_data(self):
        """
        Returns the number of bytes waiting on the serial port.
        One frame is at least three bytes.

        :return: Number of bytes
        """
        return self.kiss.interface.in_waiting

    def cycle(self):
        """
        Check the serial interface for frames, add incoming frames to queue

        :return: Number of frames in queue
        """
        if self.has_data() >= 3:  # Minimum length of a complete frame
            self.__get_frame()  # Reads one frame from the radio and adds it to the queue

        return self._packets_waiting

    def test_radio(self):
        frame = self.kiss.create_frame(GET_FREQUENCY, b'')
        logger.debug('Writing frame [{}] to radio (get frequency)...'.format(frame))
        self.kiss.write_frames_to_radio()
        self.kiss.read_and_decode()
        for dec in self.kiss.decoded_frames:
            logger.info('Frequency: {}Mhz'.format(int.from_bytes(dec, byteorder='big', signed=False) / 1e6))

        frame = self.kiss.create_frame(GET_MODE, b'')
        logger.debug('Writing frame [{}] to radio (get mode)...'.format(frame))
        self.kiss.write_frames_to_radio()
        self.kiss.read_and_decode()
        for dec in self.kiss.decoded_frames:
            logger.info('Mode: {}'.format(int.from_bytes(dec, byteorder='big', signed=False)))

        frame = self.kiss.create_frame(GET_POWER, b'')
        logger.debug('Writing frame [{}] to radio (get power)...'.format(frame))
        self.kiss.write_frames_to_radio()
        self.kiss.read_and_decode()
        for dec in self.kiss.decoded_frames:
            logger.info('Power: {}dBm'.format(int.from_bytes(dec, byteorder='big', signed=True)))


class RadioError(Exception):
    """Radio Error."""
    pass
