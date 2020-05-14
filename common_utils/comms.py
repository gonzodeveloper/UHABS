from threading import Thread
import numpy as np
import socket
import struct
import io


class Transmistter:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.conn = self.connect()



    def connect(self):
        # Make socket
        sock = socket.socket()

        # Connect
        conn = sock.connect((self.host, self.port))

        # Give timeout
        conn.settimeout(300)

        return conn

    def send(self, data):
        with io.BytesIO() as buffer:
            np.savez_compressed(buffer, data=data)

            msg_len = struct.pack('>I', buffer.tell())

            self.conn.sendall(msg_len)
            self.conn.sendall(buffer)



class Listener:
    def __init__(self, host, port):
        self.host = host
        self.port = port

        self.conn = self.listen()

    def listen(self):
        # Make socket
        sock = socket.socket()

        # Specify TCP
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # Bind to port
        sock.bind((self.host, self.port))

        # Listen for new connections
        sock.listen()

        conn, addr = sock.accept()
        conn.settimeout(300)

        # Spin off as new thread
        return conn



    def recv(self):

        # Length of our data is received as uint32
        raw_data_len = self.conn.recv(4)
        data_len = struct.unpack('>I', raw_data_len)[0]

        with io.BytesIO() as buffer:
            # Ensure we get the entire message
            while buffer.tell() < data_len:
                packet = self.conn.recv(data_len - buffer.tell())
                if not packet:
                    break
                buffer.write(packet)

            # Return to beginning of buffer, read flag and data
            buffer.seek(0)
            data = np.load(buffer)['data']

        return data