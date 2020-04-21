from selfiesat_server import logger, config
from .kiss import Kiss

from .sat2rf1_constants import *

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

    def set_frequency(self, freq):
        """
        Sets frequency of the radio in Hertz.
        """
        if freq < LOWER_FREQUENCY_LIMIT:
            raise RadioError("Frequency too low. Must be larger than " + str(int(LOWER_FREQUENCY_LIMIT/1e6)) + " MHz")
        elif freq > UPPER_FREQUENCY_LIMIT:
            raise RadioError("Frequency too large. Must be smaller than " + str(int(UPPER_FREQUENCY_LIMIT/1e6)) + " MHz")

        try:
            freq_in_bytes = int(freq).to_bytes(length=4, byteorder='big') # freq must be int
            #response = self.kiss.write_setting(setting=SET_FREQUENCY, value=freq_in_bytes)
            response = self.kiss.create_frame(setting=SET_FREQUENCY, value=freq_in_bytes)
            response = int.from_bytes(response, 'big')

            if response != 0:
                raise RadioError("Could not set frequency! Error code " + str(response))

            else:
                logger.info('Set frequency to ' + str(int(freq/1e6)) + ' MHz.')

        except RadioError as e:
            logger.error(e)

    def get_frequency(self):
        """
        Returns current carrier frequency.
        """
        try:
            #response = self.kiss.write_setting(setting=GET_FREQUENCY, value=b'00000000')
            response = self.kiss.create_frame(setting=GET_FREQUENCY, value=b'00000000')
            freq = int.from_bytes(response, 'big')
            logger.info("Frequency is " + str(int(freq/1e6)) + " MHz")
            return freq
        except Exception as e:
            logger.error("Could not get frequency from radio. "+ str(e))

    def send_string(self, data):
        pass

    def set_radio_mode(self, mode):
        """
        Sets a transmitter mode
        """
        try:
            #response = self.kiss.write_setting(setting=SET_MODE, value=mode)
            response = self.kiss.create_frame(setting=SET_MODE, value=mode)
            response = int.from_bytes(response, 'big')
            if response != 0:
                raise RadioError("Could not set transmitter mode.")
        except RadioError as e:
            logger.error(e)

    def set_packet_receive_mode(self):
        """
        The packet is detected when the specific carrier signal
        to noise ratio is exceeded (15 dB above noise in case of AX.25 packets)
        """
        logger.info("Setting radio to packet receive mode.")
        self.set_radio_mode(mode=PACKET_RECEIVE_MODE)

    def set_transparent_receive_mode(self):
        """
        In packet mode, packet detection and de-coding is
        accomplished automatically by hardware. The packet mode is more
        sensitive compared to the transparent mode, however
        it is more susceptible to the interference cause by the noisy signals
        """
        logger.info("Setting radio to transparent mode.")
        self.set_radio_mode(mode=TRANSPARENT_RECEIVE_MODE)

    def set_continous_transmit_mode(self):
        """
        For debugging. Emits a constant carrier wave with no data.
        """
        logger.info("Setting radio to continous transmit mode.")
        self.set_radio_mode(mode=CONTINOUS_TRANSMIT_MODE)

    def get_radio_mode(self):
        """
        Returns current radio mode.
        """
        try:
            #response = self.kiss.write_setting(setting=GET_MODE, value=b'00000000')
            response = self.kiss.create_frame(setting=GET_MODE, value=b'00000000')

            if response == PACKET_RECEIVE_MODE:
                logger.info("Radio is in packet receive mode.")
            elif response == TRANSPARENT_RECEIVE_MODE:
                logger.info("Radio is in transparent receive mode.")
            elif response == CONTINOUS_TRANSMIT_MODE:
                logger.info("Radio is in continous transmit mode.")
            elif response == TRANSMIT_IN_PROGRESS:
                logger.info("Radio is in transmit in progress mode.")

            return response
        except Exception as e:
            logger.error("Could not get radio mode. "+ str(e))

    # TODO: Rough scetch. Test this. Data transmission uses DATA setting from KISS.
    def transmit_data(self, data):
        """
        Pass data to the radio for transmission
        """
        try:
            #response = self.kiss.write_setting(setting=DATA, value=data)
            response = self.kiss.create_frame(setting=DATA_FRAME, value=data)
            response = int.from_bytes(response, 'big')
            if response != 0:
                raise RadioError("Could not set transmitter mode.")
        except RadioError as e:
            logger.error(e)

    # TODO: Get data from KISS interface. Then send data to socket or validate command.
    def read_data_from_interface(self):
        for data in self.kiss.decoded_frames:
            if data.command == DATA_FRAME:
                pass # send data to socket or some other interface
            else:
                self.validate_command(data)


    # TODO: Validate all commands written to the radio. Each command sends a error code back. Check these or throw an exception.
    # This means that all the other functions need thir response validation moved down here.
    def validate_command(self, response):
        # first check which command sent this
        if response.command_code == SET_FREQUENCY:
            if response != 0:
                raise RadioError("Could not set frequency! Error code " + str(response))

            else:
                logger.info('Set frequency to ' + str(int(freq/1e6)) + ' MHz.')
                # TODO: Perhaps update some frquency variable so it is easy to access?
                self.carrier_frequency = freq

class RadioError(Exception):
    """Radio Error."""
    pass
