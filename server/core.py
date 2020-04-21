import logging

from server import connection, HOSTNAME, SETTINGS_PORT, DATA_PORT, logger


def main():
    logger.info("Setting up sockets...")
    settings_socket = connection.Connection(HOSTNAME, SETTINGS_PORT, True)
    data_port = connection.Connection(HOSTNAME, DATA_PORT)

    logger.info("Nothing more to do; exiting")


if __name__ == '__main__':
    main()
