#!/usr/bin/env python3
import time, subprocess
# naive: use xsel to clear clipboard every 1s
while True:
    subprocess.run(['xsel','--clear'], check=False)
    time.sleep(1)