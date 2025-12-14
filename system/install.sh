#!/bin/bash
# DPS-OS Installation Script

set -e

echo "Installing DPS-OS..."

# Create installation directory
sudo mkdir -p /opt/dps-os
sudo cp -r daemon/ agents/ watchers/ schema/ /opt/dps-os/

# Set permissions
sudo chmod +x /opt/dps-os/daemon/daemon.py
sudo chmod +x /opt/dps-os/watchers/udevWatcher.py
sudo chmod +x /opt/dps-os/watchers/nativeHostBrowser.py
sudo chmod +x /opt/dps-os/agents/*.py

# Create socket directory
sudo mkdir -p /var/run/dpsos
sudo chmod 755 /var/run/dpsos

# Install systemd service
sudo cp system/dpsos.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable dpsos.service

# Install Python dependencies
pip3 install pyudev watchdog jsonschema psutil

echo "DPS-OS installed successfully!"
echo "Start with: sudo systemctl start dpsos"
echo "Check status: sudo systemctl status dpsos"