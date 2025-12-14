#!/bin/bash
# Simple DPS-OS Installation Script for Kali Linux

echo "🛡️  Installing DPS-OS Dependencies..."

# Update system
apt update

# Install system packages
apt install -y python3 python3-pip python3-dev build-essential libudev-dev network-manager wmctrl xsel libnotify-bin netcat-openbsd

# Install Python packages
pip3 install flask pyudev psutil watchdog jsonschema

# Create directories
mkdir -p /var/run/dpsos /var/log/dpsos templates
chmod 755 /var/run/dpsos /var/log/dpsos

# Create test VPN connection
nmcli connection add type vpn con-name dps-vpn ifname -- vpn-type openvpn 2>/dev/null || true

echo "✅ Installation complete!"
echo "Run: sudo python3 dps_app.py"