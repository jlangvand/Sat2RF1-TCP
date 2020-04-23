"""
This contains the Connection class which can be used to
provide socket functionality to a script or a program.
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

import selectors
import socket
import types

# Defines logging format.
from sat2rf1_tcpserver import logger


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
        if settings_con:
            socket_type = "settings"
        else:
            socket_type = "data"
        logger.info('Listening for %s on %s:%s.', socket_type, host, port)

    def accept_wrapper(self):
        """
        Accepts an incoming connection. Should only be called when the
        instance's listening socket is selected by the instance's selector.
        """
        conn, addr = self.lsock.accept()
        conn.setblocking(False)
        self.sel.register(conn, selectors.EVENT_READ | selectors.EVENT_WRITE,
                          data=types.SimpleNamespace(addr=addr, inb=b'', outb=b''))
        logger.info('Accepted connection from %s:%s.', addr[0], addr[1])

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
                    logger.warning('Connection to %s:%s was closed from client side.',
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
                        logger.warning('Connection to %s:%s was closed from client side.',
                                       data.addr[0], data.addr[1])
                        self.sel.unregister(sock)
                        sock.close()
                        break
            if recv_data:
                logger.debug('Data received from %s:%s: %s',
                             data.addr[0], data.addr[1], repr(recv_data))
                self._received.append((recv_data, data))
        if mask & selectors.EVENT_WRITE:
            if data.outb:
                logger.debug('Sending data to %s:%s: %s',
                             data.addr[0], data.addr[1], repr(data.outb))
                sent = sock.send(data.outb)
                data.outb = data.outb[sent:]

    def server_cycle(self, timeout=0):
        """
        Runs the "socket" for exactly one cycle. Beware that this call will
        not return if no socket events occur and timeout is not set.
        """
        try:
            events = self.sel.select(timeout=timeout)  # Blocks.
            for key, mask in events:
                try:
                    if key.data is None:
                        self.accept_wrapper()
                    else:
                        self.service_connection(key, mask)
                except OSError:
                    logger.exception('A socket error was caught:\n')
        except:
            logger.critical('An unexpected error occurred:\n', exc_info=True)

    @staticmethod
    def send(message, data_pointer):
        """
        Registers message for sending on the socket associated with data_pointer.
        """
        data_pointer.outb += message

    def receive(self):
        """
        Pops one tuple (message, data_pointer) from the received list and returns it.
        Returns None if the received list is empty.
        """
        return self._received.pop() if self._received else None

    def receive_all(self):
        """
        Pops all tuples (message, data_pointer) from the
        received list and returns a list of them.
        Returns None if the received list is empty.
        """
        temp = []
        while self._received:
            temp.append(self._received.pop())
        return temp if temp else None
