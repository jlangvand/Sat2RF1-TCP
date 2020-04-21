import yaml
import logging, sys
import threading
import numpy as np

from sat2rf1.kiss import Kiss

from .constants import *

# Import config
with open("./config.yaml", 'r') as stream:
    try:
        config = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        logging.warning('Error in configuration file: %s', exc)

# Set the logging
logFormatter = '%(asctime)s - %(levelname)s - %(message)s'
logging.basicConfig(format=logFormatter, level=logging.DEBUG, handlers=[logging.StreamHandler(sys.stdout)])

# Define parameters for serial communication
baudrate = config['radio']['baudrate']
port = config['radio']['port']
serial_timeout = config['radio']['serial_timeout']


def build_settings_command(setting, value):
    return b''.join([
        Kiss.FEND,
        setting,
        value,
        Kiss.FEND
    ])


class Sat2rf1():
    """
    Class for interfacing with the Sat2rf1 radio.
    """
    def __init__(self):
        self.kiss = Kiss(port=port, baudrate=baudrate, timeout=serial_timeout)

    def set_freq(self, freq):
        freq_in_bytes = int(freq).to_bytes(length=4, byteorder='big')  # freq must be int
        frame = build_settings_command(SET_FREQUENCY, freq_in_bytes)
        if len(self.kiss.write_queue) > 0:
            logging.warning("Interface busy, " + len(self.kiss.write_queue) + "packets in line")
            while len(self.kiss.write_queue) > 0:
                pass
        logging.info("Seting frequency to " + str(int(freq/1e6)) + " MHz.")
        response = self.kiss.write_and_return_response(frame)
        # ...

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
                logging.info('Set frequency to ' + str(int(freq/1e6)) + ' MHz.')

        except RadioError as e:
            logging.error(e)

    def get_frequency(self):
        """
        Returns current carrier frequency.
        """
        try:
            #response = self.kiss.write_setting(setting=GET_FREQUENCY, value=b'00000000')
            response = self.kiss.create_frame(setting=GET_FREQUENCY, value=b'00000000')
            freq = int.from_bytes(response, 'big')
            logging.info("Frequency is " + str(int(freq/1e6)) + " MHz")
            return freq
        except Exception as e:
            logging.error("Could not get frequency from radio. "+ str(e))

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
            logging.error(e)

    def set_packet_receive_mode(self):
        """
        The packet is detected when the specific carrier signal
        to noise ratio is exceeded (15 dB above noise in case of AX.25 packets)
        """
        logging.info("Setting radio to packet receive mode.")
        self.set_radio_mode(mode=PACKET_RECEIVE_MODE)

    def set_transparent_receive_mode(self):
        """
        In packet mode, packet detection and de-coding is
        accomplished automatically by hardware. The packet mode is more
        sensitive compared to the transparent mode, however
        it is more susceptible to the interference cause by the noisy signals
        """
        logging.info("Setting radio to transparent mode.")
        self.set_radio_mode(mode=TRANSPARENT_RECEIVE_MODE)

    def set_continous_transmit_mode(self):
        """
        For debugging. Emits a constant carrier wave with no data.
        """
        logging.info("Setting radio to continous transmit mode.")
        self.set_radio_mode(mode=CONTINOUS_TRANSMIT_MODE)

    def get_radio_mode(self):
        """
        Returns current radio mode.
        """
        try:
            #response = self.kiss.write_setting(setting=GET_MODE, value=b'00000000')
            response = self.kiss.create_frame(setting=GET_MODE, value=b'00000000')

            if response == PACKET_RECEIVE_MODE:
                logging.info("Radio is in packet receive mode.")
            elif response == TRANSPARENT_RECEIVE_MODE:
                logging.info("Radio is in transparent receive mode.")
            elif response == CONTINOUS_TRANSMIT_MODE:
                logging.info("Radio is in continous transmit mode.")
            elif response == TRANSMIT_IN_PROGRESS:
                logging.info("Radio is in transmit in progress mode.")

            return response
        except Exception as e:
            logging.error("Could not get radio mode. "+ str(e))

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
            logging.error(e)

    # TODO: Get data from KISS interface. Then send data to socket or validate command.
    def read_data_from_interface(self):
        for data in self.kiss.get_decoded_frames():
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
                logging.info('Set frequency to ' + str(int(freq/1e6)) + ' MHz.')
                # TODO: Perhaps update some frquency variable so it is easy to access?
                self.carrier_frequency = freq

class RadioError(Exception):
    """Radio Error."""
    pass
