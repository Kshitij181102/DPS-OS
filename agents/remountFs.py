#!/usr/bin/env python3
import subprocess, sys

def remount_ro(path='/home'):
    """Remount filesystem as read-only"""
    try:
        subprocess.run(['sudo','mount','-o','remount,ro',path], check=True)
        print(f'Remounted {path} as read-only')
    except subprocess.CalledProcessError as e:
        print(f'Failed to remount {path}: {e}')

def remount_rw(path='/home'):
    """Remount filesystem as read-write"""
    try:
        subprocess.run(['sudo','mount','-o','remount,rw',path], check=True)
        print(f'Remounted {path} as read-write')
    except subprocess.CalledProcessError as e:
        print(f'Failed to remount {path}: {e}')

if __name__=='__main__':
    if len(sys.argv) > 1:
        if sys.argv[1] == 'ro':
            remount_ro()
        elif sys.argv[1] == 'rw':
            remount_rw()
        else:
            print('Usage: remountFs.py [ro|rw]')
    else:
        print('Usage: remountFs.py [ro|rw]')