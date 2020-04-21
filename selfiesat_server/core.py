import sys

from serial import SerialException

from selfiesat_server import connection, HOSTNAME, SETTINGS_PORT, DATA_PORT, logger, config
from selfiesat_server.sat2rf1 import Sat2rf1


def main():
    logger.info("Setting up sockets...")

    hostname = config['socket']['hostname']
    settings_port = config['socket']['settings_port']
    data_port = config['socket']['data_port']

    settings_socket = connection.Connection(hostname, settings_port, True)
    data_socket = connection.Connection(hostname, data_port)

    logger.info("Setting up radio...")
    try:
        radio = Sat2rf1()
    except SerialException as e:
        logger.error('Failed to connect to radio:')
        logger.error(e.strerror)
        if not config['debug']['fake_radio_connection']: sys.exit(1)


if __name__ == '__main__':
    main()