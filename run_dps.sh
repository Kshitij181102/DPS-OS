#!/bin/bash
# DPS-OS Unified Application Launcher

echo "🛡️  DPS-OS Unified Monitor"
echo "=========================="

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "⚠️  This application requires root privileges for full functionality."
    echo "   Restarting with sudo..."
    exec sudo "$0" "$@"
fi

# Install dependencies if needed
if ! python3 -c "import flask, pyudev, psutil" 2>/dev/null; then
    echo "📦 Installing required packages..."
    apt update
    apt install -y python3-pip python3-dev libudev-dev
    pip3 install -r requirements_app.txt
fi

# Create necessary directories
mkdir -p logs templates

# Set permissions
chmod +x dps_app.py

echo "🚀 Starting DPS-OS Monitor..."
echo "📊 Dashboard will be available at: http://localhost:8080"
echo "🔧 Press Ctrl+C to stop"
echo ""

# Run the application
python3 dps_app.py