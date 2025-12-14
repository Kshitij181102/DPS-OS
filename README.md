# DPS-OS — Dynamic Privacy-Shifting OS (Starter Repo)

This repo is a working prototype of DPS-OS: an OS-level privacy transition engine.

## What you'll find
- `daemon/` : Prototype daemon and rule engine (Python)
- `agents/`: Example action agents (clipboard lock, vpn toggler)
- `watchers/`: Event watchers (udev + browser native host)
- `ext/browser/`: Browser extension that notifies native host on URL changes
- `ui/webapp/`: React UI to manage zones and rules
- `system/`: systemd service & installer
- `schema/`: Sample rule JSON + JSON Schema

## Quick start (Linux prototype)
1. Install dependencies: `sudo apt update && sudo apt install python3 python3-venv python3-pip network-manager`.
2. Create virtualenv: `python3 -m venv .venv && source .venv/bin/activate`
3. Install Python deps: `pip install pyudev watchdog jsonschema psutil`.
4. Start daemon (dev): `python daemon/daemon.py --db daemon/config.sqlite`
5. Start udev watcher: `python watchers/udevWatcher.py --sock /var/run/dpsos.sock`
6. Install browser extension locally (load unpacked) and register the native messaging host (see `watchers/nativeHostBrowser.py`).

## Notes
This is a prototype. Remounting filesystems or toggling networks require root. Use VMs for testing.