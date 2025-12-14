#!/usr/bin/env python3
import subprocess

def up():
    subprocess.run(['nmcli','connection','up','dps-vpn'])

def down():
    subprocess.run(['nmcli','connection','down','dps-vpn'])

if __name__=='__main__':
    import sys
    if len(sys.argv)>1 and sys.argv[1]=='up': up()
    else: down()