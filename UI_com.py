"""
This is the actual server. At the moment it is a simple
example and only echos messeges back to the client.
"""


import socket
import logging


HOST = 'localhost'
PORT = 65432
logging.basicConfig(filename='dump.log',
                    format='%(asctime)s %(levelname)s %(message)s',
                    level=logging.INFO)


lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
lsock.bind((HOST, PORT))
lsock.listen()
logging.info('Listening on %s:%s.', HOST, PORT)
conn, ADDR = lsock.accept() # Blocks (awaits connection attempt)
logging.info('Accepted connection from %s:%s.', ADDR[0], ADDR[1])

try:
    while True:
        recv_data = conn.recv(1024) # Blocks (awaits data)
        logging.info('Echoing "%s" to %s:%s.', repr(recv_data), ADDR[0], ADDR[1])
        conn.send(recv_data)
except KeyboardInterrupt:
    print('Caught keyboard interrupt. Exiting...')
finally:
    logging.info('Closing connection to %s:%s and listening socket.', ADDR[0], ADDR[1])
    conn.close()
    lsock.close()
