"""
This is the actual server. At the moment it is a simple
example and only echos messeges back to the client.
"""


import socket
import logging


# Defines the logging format.
logging.basicConfig(filename='dump.log',
                    format='%(asctime)s %(levelname)s %(message)s',
                    level=logging.INFO)


# Creates a socket listening for connections at HOST:PORT.
HOST = 'localhost'
PORT = 65432
lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
lsock.bind((HOST, PORT))
lsock.listen()
logging.info('Listening on %s:%s.', HOST, PORT)


def accept_connection(listening_socket):
    """
    Accepts an incoming connection.
    """
    logging.info('Awaiting incoming connection.')
    connection, address = listening_socket.accept() # Blocks (awaits connection attempt).
    logging.info('Accepted connection from %s:%s.', address[0], address[1])
    return connection, address


def serve_connection(connection, address):
    """
    Serves an established connection.
    """
    received = []
    # TODO: Correct the package size; 250 is a placeholder.
    while len(received) < 250:
        data = connection.recv(250) # Blocks (awaits data).
        if not data:
            logging.warning('Connection to %s:%s was closed from client side.',
                            address[0], address[1])
            connection.close()
            return False
        received.append(data)
    # TODO: Change from echo back to client to pass to radio interface.
    logging.info('Echoing %s to %s:%s.', repr(data), address[0], address[1])
    connection.sendall(b''.join(received))
    return True


# The server loop.
try:
    conn = None # Just to make sure it's defined (for error handling).
    conn, ADDR = accept_connection(lsock)
    while True:
        try:
            if not serve_connection(conn, ADDR):
                conn, ADDR = accept_connection(lsock)
        except OSError:
            logging.exception('Connection to %s:%s was terminated; a socket error occured: ',
                              ADDR[0], ADDR[1])
            conn.close()
            conn, ADDR = accept_connection(lsock)

except KeyboardInterrupt:
    logging.info('Keyboard interrupt caught.')

except:
    logging.critical('An unexpected error occured: ', exc_info=True)

finally:
    if conn is None:
        logging.info('Closing listening socket.\n')
        lsock.close()
    else:
        logging.info('Closing connection to %s:%s and listening socket.\n', ADDR[0], ADDR[1])
        conn.close()
        lsock.close()
