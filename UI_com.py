"""
This is the actual server. At the moment it is a simple
example and only echos messeges back to the client(s).
"""


import selectors
import socket
import logging
import types


# Defines logging format.
logging.basicConfig(filename='dump.log',
                    format='%(asctime)s %(levelname)s %(message)s',
                    level=logging.INFO)


# Creates a socket listening on HOST:PORT.
HOST = 'localhost'
PORT = 65432
lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
lsock.setblocking(False)
lsock.bind((HOST, PORT))
lsock.listen()
logging.info('Listening on %s:%s.', HOST, PORT)


# Creates a selector which decides when to create new connections,
# receive data or send data.
sel = selectors.DefaultSelector()
sel.register(lsock, selectors.EVENT_READ)


def accept_wrapper(sock):
    """
    Accepts incoming connections.
    """
    conn, addr = sock.accept()
    conn.setblocking(False)
    sel.register(conn, selectors.EVENT_READ | selectors.EVENT_WRITE,
                 data=types.SimpleNamespace(addr=addr, inb=b'', outb=b''))
    logging.info('Accepted connection from %s:%s.', addr[0], addr[1])


def service_connection(key, mask):
    """
    Services established connections. (Echoes messeges.)
    """
    sock = key.fileobj
    data = key.data
    if mask & selectors.EVENT_READ:
        recv_data = b''
        # TODO: Correct the package size; 250 is a placeholder number.
        while len(recv_data) < 250:
            temp_data = sock.recv(250)
            if temp_data:
                recv_data += temp_data
            else:
                logging.warning('Connection to %s:%s was closed from client side.',
                                data.addr[0], data.addr[1])
                sel.unregister(sock)
                sock.close()
                break
        # TODO: Send the received package where it should be.
        if recv_data:
            logging.info('Package received: ' + repr(recv_data))
            data.outb += recv_data
    if mask & selectors.EVENT_WRITE:
        # TODO: Change from echoing to passing packages.
        if data.outb:
            logging.info('Echoing %s to %s:%s', repr(data.outb), data.addr[0], data.addr[1])
            sent = sock.send(data.outb)
            data.outb = data.outb[sent:]


# The server loop.
try:
    while True:
        # Keyboard interrupts does not seem to work when
        # using Windows. This can be remedied by setting a
        # timeout (e.g. sel.select(timeout=5)).
        events = sel.select(timeout=3)
        for key, mask in events:
            try:
                if key.data is None:
                    accept_wrapper(key.fileobj)
                else:
                    service_connection(key, mask)
            except OSError:
                logging.exception('A socket error was caught: ')
except KeyboardInterrupt:
    logging.info('Keyboard interrupt caught.')
except Exception:
    logging.critical('An unexpected error occured: ', exc_info=True)
finally:
    logging.info('Shutting down server side.\n')
    sel.close()
