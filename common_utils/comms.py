from threading import Thread
import numpy as np
import socket
import struct
import io

flags = {
            'INSTR_BEARING':    b'0',
            'INSTR_MAP_FULL':   b'1',
            'INSTR_MAP_CONV':   b'2',
            'TEMEM_POS':        b'3',
            'TELEM_TEMP':       b'4',
            'TELEM_PATH':       b'5'
         }


def listen(host, port, proc, init_args):
    # Make socket
    sock = socket.socket()

    # Specify TCP
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # Bind to port
    sock.bind((host, port))

    # Listen for new connections
    sock.listen()

    while True:
        conn, addr = sock.accept()
        conn.settimeout(300)
        # Spin off as new thread
        new_thread = Thread(target=proc, args=init_args + (conn,))
        new_thread.start()

def connect(host, port):
    # Make socket
    sock = socket.socket()

    # Connect
    conn = sock.connect((host, port))

    # Give timeout
    conn.settimeout(300)

    return conn

def send(conn, flag, data):
    with io.BytesIO() as buffer:

        buffer.write(flag)
        np.savez_compressed(buffer, data=data)

        msg_len = struct.pack('>I', buffer.tell())

        conn.sendall(msg_len)
        conn.sendall(buffer)


def recv(conn):

    # Length of our data is received as uint32
    raw_data_len = conn.recv(4)
    data_len = struct.unpack('>I', raw_data_len)[0]

    with io.BytesIO() as buffer:
        # Ensure we get the entire message
        while buffer.tell() < data_len:
            packet = conn.recv(data_len - buffer.tell())
            if not packet:
                break
            buffer.write(packet)

        # Return to beginning of buffer, read flag and data
        buffer.seek(0)
        flag = buffer.read(1)
        data = np.load(buffer)['data']

    return flag, data