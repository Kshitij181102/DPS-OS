# daemon/actionDispatcher.py
import subprocess, os

class ActionDispatcher:
    def __init__(self):
        pass

    def applyActions(self, actions):
        for a in actions:
            if a=='enableVpn':
                self.enableVpn()
            elif a=='lockClipboard':
                self.lockClipboard()
            elif a=='remountHomeRo':
                self.remountHomeRo()
            else:
                print('Unknown action', a)

    def enableVpn(self):
        print('Enabling VPN via nmcli (prototype)')
        # prototype: toggle NetworkManager connection name 'dps-vpn'
        try:
            subprocess.run(['nmcli','connection','up','dps-vpn'], check=False)
        except Exception as e:
            print('VPN toggle failed', e)

    def lockClipboard(self):
        print('Locking clipboard (prototype)')
        # naive approach: set empty clipboard periodically (works on X11)
        subprocess.Popen(['python3','agents/clipboardLocker.py'])

    def remountHomeRo(self):
        print('Remounting /home read-only (prototype)')
        try:
            subprocess.run(['sudo','mount','-o','remount,ro','/home'], check=False)
        except Exception as e:
            print('remount failed', e)