"""
This is a small testing app for ui_com. It establishes
a specified amount of connections to the server and sends
two byte strings per connection; test information gets printed
to terminal.
"""


import socket
import selectors
import types


HOST = 'localhost'
PORT = 65432
sel = selectors.DefaultSelector()
MESSAGES = [b'Message 1 from client.', b'Message 2 from client.']


def start_connections(host, port, num_conns):
    """
    Establishes connections to the server.
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
            print('Sending "%s" to connection %s' % (repr(data.outb), data.connid))
            sent = sock.send(data.outb)  # Should be ready to write
            data.outb = data.outb[sent:]


start_connections(HOST, PORT, int(input('Input number of connections: ')))

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