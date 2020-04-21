import sys

from serial import SerialException

from selfiesat_server import connection, HOSTNAME, SETTINGS_PORT, DATA_PORT, logger, config
from selfiesat_server.sat2rf1 import Sat2rf1
from selfiesat_server.utils import dump_packet


def main():
    logger.info("Setting up sockets...")

    hostname = config['socket']['hostname']
    settings_port = config['socket']['settings_port']
    data_port = config['socket']['data_port']

    settings_socket = connection.Connection(hostname, settings_port, True)
    data_socket = connection.Connection(hostname, data_port)

    data_pointer = None

    logger.info("Setting up radio...")
    try:
        radio = Sat2rf1()
    except SerialException as e:
        logger.error('Failed to connect to radio:')
        logger.error(e.strerror)
        if not config['debug']['fake_radio_connection']: sys.exit(1)

    while True:
        # Update sockets, allows them to receive data.
        # Setting a timeout so they won't block execution if no data is present.
        settings_socket.server_cycle(0.5)
        data_socket.server_cycle(0.5)

        # Check for data/settings and do stuff
        tcp_data = data_socket.receive()
        if tcp_data is not None:
            logger.info("Got a TCP packet")
            logger.info("Message: %s", tcp_data[1])
            data_pointer = tcp_data[0]

        tcp_settings = settings_socket.receive()
        if tcp_settings is not None:
            pass
            # TODO: Add pointer to stack, do stuff with command

        # Assuming read_data_from_interface() returns a tuple where
        # radio_data[0] contains command byte (ignored for now),
        # radio_data[1] contains message
        radio_data = radio.read_data_from_interface()
        if radio_data is not None:
            if data_pointer is not None:
                logger.info("Got data from radio, sending to client")
                data_socket.send(radio_data[1], data_pointer)
            else:
                logger.warning("Data received from radio but no client connected!")
                logger.info("Dumping incoming data...")
                dump_packet(radio_data)


if __name__ == '__main__':
    main()
