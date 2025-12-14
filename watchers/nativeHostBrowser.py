#!/usr/bin/env python3
# native messaging host - prototype
# Follow Chrome native messaging protocol: stdin length (4 bytes) + message
import sys, struct, json, socket

SOCK_PATH='/var/run/dpsos.sock'

def read_message():
    raw_len = sys.stdin.buffer.read(4)
    if not raw_len:
        return None
    msg_len = struct.unpack('<I', raw_len)[0]
    data = sys.stdin.buffer.read(msg_len).decode()
    return json.loads(data)

def send_to_daemon(msg):
    try:
        s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        s.connect(SOCK_PATH)
        s.sendall(json.dumps(msg).encode())
        s.close()
    except Exception as e:
        print('daemon notify failed', e)

if __name__=='__main__':
    while True:
        m = read_message()
        if m is None: break
        send_to_daemon(m)