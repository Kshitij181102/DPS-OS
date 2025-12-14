#!/usr/bin/env python3
# watchers/udevWatcher.py
import pyudev, socket, json, argparse

parser = argparse.ArgumentParser()
parser.add_argument('--sock','--socket', default='/var/run/dpsos.sock')
args = parser.parse_args()

ctx = pyudev.Context()
monitor = pyudev.Monitor.from_netlink(ctx)
monitor.filter_by('block')
for device in iter(monitor.poll, None):
    if device.action=='add':
        msg = {'trigger':'usbPlugged', 'device':{'sysName':device.sys_name,'devNode':device.device_node}}
        try:
            s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            s.connect(args.sock)
            s.sendall(json.dumps(msg).encode())
            s.close()
        except Exception as e:
            print('notify failed', e)