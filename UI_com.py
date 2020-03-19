import selectors
import socket
import logging
import types


host = 'localhost'
port = 65432
sel = selectors.DefaultSelector()
logging.basicConfig(filename='dump.log', format='%(asctime)s %(levelname)s %(message)s', level=logging.INFO)


lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
lsock.bind((host, port))
lsock.listen()
logging.info('Listening on %s:%s.' % (host, port))
lsock.setblocking(False)
sel.register(lsock, selectors.EVENT_READ)


def accept_wrapper(sock):
    conn, addr = sock.accept()  # Should be ready to read.
    logging.info('Accepted connection from %s:%s.' % (addr[0], addr[1]))
    conn.setblocking(False)
    data = types.SimpleNamespace(addr=addr, inb=b'', outb=b'')
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    sel.register(conn, events, data=data)


def service_connection(key, mask):
    sock = key.fileobj
    data = key.data
    if mask & selectors.EVENT_READ:
        recv_data = sock.recv(1024)  # Should be ready to read.
        if recv_data:
            data.outb += recv_data
        else:
            logging.info('Closing connection to %s:%s.' % (data.addr[0], data.addr[1]))
            sel.unregister(sock)
            sock.close()
    if mask & selectors.EVENT_WRITE:
        if data.outb:
            logging.info('Echoing "%s" to %s:%s' % (repr(data.outb), data.addr[0], data.addr[1]))
            sent = sock.send(data.outb)  # Should be ready to write.
            data.outb = data.outb[sent:]


while True:
    events = sel.select()
    for key, mask in events:
        if key.data is None:
            accept_wrapper(key.fileobj)
        else:
            service_connection(key, mask)
