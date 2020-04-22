"""
This is a testing script for ui_com. It establishes
a specified amount of connections to the socket and sends
two byte strings per connection. Test information gets printed
to the terminal.
"""

#  Copyright © 2020 Orbit NTNU (http://orbitntnu.no)
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
#
#  Authors:
#  David Ferenc Bendiksen
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

# Where to connect to.
HOST = 'localhost'
PORT = 65432

# Selector for handling multiple connections.
sel = selectors.DefaultSelector()

# The byte messages that will be sent.
m1 = b''
m2 = b''
for i in range(0, 250):
    m1 += b'a'
    m2 += b'b'
MESSAGES = [m1, m2]


def start_connections(host, port, num_conns):
    """
    Establishes connections to the sat2rf1_tcpserver.
    """
    server_addr = (host, port)
    for i in range(0, num_conns):
        connid = i + 1
        print('Starting connection %s to %s:%s' % (connid, server_addr[0], server_addr[1]))
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setblocking(False)
        sock.connect_ex(server_addr)
        events = selectors.EVENT_READ | selectors.EVENT_WRITE
        data = types.SimpleNamespace(connid=connid,
                                     msg_total=sum(len(m) for m in MESSAGES),
                                     recv_total=0,
                                     messages=list(MESSAGES),
                                     outb=b'')
        sel.register(sock, events, data=data)


def service_connection(key, mask):
    """
    Services established connections. (Either sends or receives the byte strings.)
    """
    sock = key.fileobj
    data = key.data
    if mask & selectors.EVENT_READ:
        recv_data = sock.recv(1024)  # Should be ready to read
        if recv_data:
            print('Received "%s" from connection %s' % (repr(recv_data), data.connid))
            data.recv_total += len(recv_data)
        if not recv_data or data.recv_total == data.msg_total:
            print('Closing connection %s' % data.connid)
            sel.unregister(sock)
            sock.close()
    if mask & selectors.EVENT_WRITE:
        if not data.outb and data.messages:
            data.outb = data.messages.pop(0)
        if data.outb:
            print('Sending %s to connection %s' % (repr(data.outb), data.connid))
            sent = sock.send(data.outb)  # Should be ready to write
            data.outb = data.outb[sent:]


# Asks for the amount of connections to initiate before starting them.
start_connections(HOST, PORT, int(input('Input number of connections: ')))

# The test loop.
try:
    while True:
        events = sel.select(timeout=1)
        if events:
            for key, mask in events:
                service_connection(key, mask)
        # Check for a socket being monitored to continue.
        if not sel.get_map():
            break
except KeyboardInterrupt:
    print('Caught keyboard interrupt. Exiting...')
finally:
    sel.close()
