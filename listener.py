import socket
import sys
from threading import Thread

def listen(host, port:)

    # Make socket
    sock = socket.socket()

    # Specify TCP
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        sock.bind((host, port))
    except socket.error:
        print('Bind failed.' + str(sys.exc_info()))
        exit(1)

    sock.listen()
    while True:
        # Get a new connection
        conn, addr = sock.accept()
        conn.settimeout(300)

        Thread(target=do_shit, args=(conn,)).start()


def do_shit(conn):
    # Program logic