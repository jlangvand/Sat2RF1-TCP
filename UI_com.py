"""
This contains the Connection class which can be used to
provide server functionality to a script or a program.
"""

import selectors
import socket
import logging
import types

# Defines logging format.
logging.basicConfig(filename='dump.log',
                    format='%(asctime)s | %(levelname)s | %(message)s',
                    level=logging.INFO)


class Connection:
    """
    A serverlike class that listens on a specific network address and may
    accept and serve an arbitrary amount of connection attempts.
    """
    def __init__(self, host='localhost', port=65432, settings_con=False):
        # Defines variables.
        self._host = host
        self._port = port
        self._settings_con = settings_con
        self._received = []
        # Defines objects.
        self.lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sel = selectors.DefaultSelector()
        # Sets up objects.
        self.lsock.setblocking(False)
        self.lsock.bind((self._host, self._port))
        self.lsock.listen()
        self.sel.register(self.lsock, selectors.EVENT_READ)
        # Logs.
        logging.info('Listening on %s:%s.', host, port)

    def accept_wrapper(self):
        """
        Accepts an incoming connection. Should only be called when the instance's
        listening socket is selected by the instance's selector.
        Returns the newly created connection socket and its address.
        """
        conn, addr = self.lsock.accept()
        conn.setblocking(False)
        self.sel.register(conn, selectors.EVENT_READ | selectors.EVENT_WRITE,
                          data=types.SimpleNamespace(addr=addr, inb=b'', outb=b''))
        logging.info('Accepted connection from %s:%s.', addr[0], addr[1])

    def service_connection(self, key, mask):
        """
        Services established connections (sends/receives data).
        Should only be called when the passed connection socket
        (key.fileobj) is selected by the instance's selector.
        """
        sock = key.fileobj
        data = key.data
        if mask & selectors.EVENT_READ:
            recv_data = b''
            if self._settings_con:
                # TODO: Correct the settings size; 1 is a placeholder number.
                temp_data = sock.recv(1)
                if temp_data:
                    recv_data += temp_data
                else:
                    logging.warning('Connection to %s:%s was closed from client side.',
                                    data.addr[0], data.addr[1])
                    self.sel.unregister(sock)
                    sock.close()
            else:
                # TODO: Correct the package size; 250 is a placeholder number.
                while len(recv_data) < 250:
                    temp_data = sock.recv(250)
                    if temp_data:
                        recv_data += temp_data
                    else:
                        logging.warning('Connection to %s:%s was closed from client side.',
                                        data.addr[0], data.addr[1])
                        self.sel.unregister(sock)
                        sock.close()
                        break
            if recv_data:
                logging.debug('Data received from %s:%s: %s',
                              data.addr[0], data.addr[1], repr(recv_data))
                self._received.append(recv_data, data.outb)
        if mask & selectors.EVENT_WRITE:
            if data.outb:
                logging.debug('Sending data to %s:%s: %s',
                              data.addr[0], data.addr[1], repr(data.outb))
                sent = sock.send(data.outb)
                data.outb = data.outb[sent:]

    def server_cycle(self, timeout=0):
        """
        Runs the "server" for exactly one cycle. Beware that this call will
        not return if no server events occur and timeout is not set.
        """
        try:
            events = self.sel.select(timeout=timeout) # Blocks.
            for key, mask in events:
                try:
                    if key.data is None:
                        self.accept_wrapper()
                    else:
                        self.service_connection(key, mask)
                except OSError:
                    logging.exception('A socket error was caught:\n')
        except:
            logging.critical('An unexpected error occured:\n', exc_info=True)

    @staticmethod
    def send(message, data_pointer):
        """
        Registers message for sending on the socket associated with data_pointer.
        """
        data_pointer.append(message)

    def receive(self):
        """
        Pops one tuple (message, data_pointer) from the received list.
        Returns None if the received list is empty.
        """
        return self._received.pop() if self._received else None
