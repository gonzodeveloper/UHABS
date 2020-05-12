import numpy as np
import socket
import io


def send(sock, flag, data):
    with io.BytesIO() as buffer:

        buffer.write(flag)
        np.savez_compressed(buffer, data=data)

        sock.send(buffer)


def recv(conn, BUFFER_SIZE=1024):
    with io.BytesIO(conn.recv(BUFFER_SIZE)) as buffer:

        buffer.seek(0)
        flag = buffer.read(1)
        data = np.load(buffer)['data']

    return flag, data