import numpy as np
import struct  # required for float conversion to bytes
import zlib
import os  # to interact with operating system
import socket
import sys
from threading import Thread
from io import BytesIO

def listen(host, port):

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


# =====for changing into binary and then compress it ==========
def np_to_bytes(data):
    np_bytes = data.tobytes()  # convert image array into bytes
    comp_bytes = zlib.compress(np_bytes)  # to compress the byte array

    return comp_bytes


# =====to decompress and convert it into numpy array ==========
def bytes_to_np(data, sh):
    np_bytes = zlib.decompress(data)
    data = np.fromstring(np_bytes, dtype='float32').reshape(sh[0], sh[1])

    return data


def float_to_bytes(data):
    # inbyte = bytes(data)
    float_bytes = struct.pack('f', data)  # to convert float value to bytes
    return float_bytes


def bytes_to_float(data):
    data = struct.unpack('f', data)
    return data


def send(sock, flag, data):

    with BytesIO() as buffer:
        buffer.write(flag)
        np.savez_compressed(buffer, data=data)

        sock.send(buffer)


def recv(conn, BUFFER_SIZE=1024):

    with BytesIO() as buffer:
        buffer.write(conn.recv(BUFFER_SIZE))

        buffer.seek(0)
        flag = buffer.read(1)
        data = np.load(buffer)['data']

    return flag, data

    flag = bytes[0]
    data = bytes[1:]
    return flag, data



