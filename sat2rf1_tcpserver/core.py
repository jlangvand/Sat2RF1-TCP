"""
Main function for module sat2rf1_tcpserver
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

import sys
from serial import SerialException

from sat2rf1_tcpserver import connection, logger, config
from sat2rf1_tcpserver.sat2rf1 import Sat2rf1
from sat2rf1_tcpserver.utils import dump_packet


def main():
    """
    Sets ut TCP connections for setting and getting radio configuration and tranceieving data.

    In it's current state, only the data socket is functional, and only one client can be connected.
    :return:
    """
    logger.info("Setting up sockets...")

    hostname = config['socket']['hostname']
    settings_port = config['socket']['settings_port']
    data_port = config['socket']['data_port']

    _client_data_buffer = []

    settings_socket = connection.Connection(hostname, settings_port, True)
    data_socket = connection.Connection(hostname, data_port)

    data_pointer = None
    radio_message = None

    logger.info("Setting up radio...")
    try:
        radio = Sat2rf1()
        logger.info('Testing radio...')
        # radio.test_radio()
    except SerialException as e:
        logger.error('Failed to connect to radio:')
        logger.error(e.strerror)
        if not config['debug']['fake_radio_connection']:
            sys.exit(1)

    try:
        while True:
            # Update sockets, allows them to receive data.
            # Setting a timeout so they won't block execution if no data is present.
            settings_socket.server_cycle(0.5)
            data_socket.server_cycle(0.5)

            # Check for data/settings and do stuff
            tcp_data = data_socket.receive()
            if tcp_data is not None:
                # logger.debug('tcp_data is not None')
                data_packet = tcp_data[0]
                data_pointer = tcp_data[1]
                logger.info("Got a TCP packet. Message: {} ({} bytes)".format(data_packet, len(bytes(data_packet))))
                if not config['debug']['fake_radio_connection']:
                    radio.transmit_data(data_packet)

            tcp_settings = settings_socket.receive()
            if tcp_settings is not None:
                pass
                # TODO: Add pointer to stack, do stuff with command

            if radio.cycle():
                radio_message = radio.get_message()
                logger.info("Got data from radio! Message: {}".format(radio_message[1]))
                if data_pointer is not None:
                    while len(_client_data_buffer) > 0:
                        logger.info(
                            'Radio messages in buffer: {}. Sending to client...'.format(len(_client_data_buffer)))
                        data_socket.send(_client_data_buffer.pop(0), data_pointer)  # TODO: better logic
                    # logger.info("Got data from radio, sending to client")
                    logger.debug('Sending {} to {}'.format(radio_message[1], data_pointer))
                    data_socket.send(radio_message[1], data_pointer)

                else:
                    logger.warning("Data received from radio but no client connected!")
                    # logger.info("Dumping incoming data...")
                    dump_packet(radio_message)
                    _client_data_buffer.append(radio_message)

    except KeyboardInterrupt:
        logger.info('Terminated by user')
