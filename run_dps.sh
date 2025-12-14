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

# Check if dependencies are installed
if ! python3 -c "import flask, pyudev, psutil" 2>/dev/null; then
    echo "❌ Dependencies not installed!"
    echo "📦 Please run the installation script first:"
    echo "   sudo chmod +x install_dependencies.sh"
    echo "   sudo ./install_dependencies.sh"
    echo ""
    echo "Or for quick install on Kali Linux:"
    echo "   sudo chmod +x install_simple.sh" 
    echo "   sudo ./install_simple.sh"
    exit 1
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