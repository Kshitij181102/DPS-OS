# DPS-OS — Dynamic Privacy-Shifting OS

A unified application that monitors system events and automatically adjusts security postures with real-time web dashboard.

## What you'll find
- `dps_app.py` : Unified monitoring application with web dashboard
- `schema/` : Rule configuration (JSON format)
- `run_dps.sh` : Simple launcher script
- `requirements_app.txt` : Python dependencies

## Quick Start (Kali Linux)
```bash
# Make launcher executable
chmod +x run_dps.sh

# Run with full privileges
sudo ./run_dps.sh

# Open browser to: http://localhost:8080
```

## Features
- **Real-time Monitoring**: USB devices, processes, network connections
- **Web Dashboard**: Live monitoring interface at localhost:8080
- **Automatic Actions**: VPN activation, clipboard locking, filesystem remounting
- **Security Zones**: Normal → Sensitive → Ultra transitions
- **Built-in Testing**: Simulate events via dashboard buttons

## Notes
Requires root privileges for full system monitoring. Use VMs for testing.