import numpy as np
import io

flags = {
            'MANUAL_BEARING':  b'0',
            'FULL_MAP':        b'1',
            'CONV_MAP':        b'2',
            'TEMEM_POS':       b'3',
            'TELEM_TEMP':      b'4',
            'TELEM_PATH':      b'5'
         }

def send(conn, flag, data):
    with io.BytesIO() as buffer:

        buffer.write(flag)
        np.savez_compressed(buffer, data=data)

        conn.send(buffer)


def recv(conn, BUFFER_SIZE=1024):
    with io.BytesIO(conn.recv(BUFFER_SIZE)) as buffer:

        buffer.seek(0)
        flag = buffer.read(1)
        data = np.load(buffer)['data']

    return flag, data