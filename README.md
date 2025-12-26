# DPS-OS — Dynamic Privacy-Shifting OS

A unified application that monitors system events and automatically adjusts security postures with real-time web dashboard.

## Project Structure
```
dps-os/
├── dps_app.py                  # Main unified application
├── run_dps.sh                  # Linux launcher script  
├── install_simple.sh           # Linux dependency installer
├── install_windows.bat         # Windows dependency installer
├── requirements_app.txt        # Core dependencies (cross-platform)
├── requirements_linux.txt      # Linux-specific dependencies
├── requirements_windows.txt    # Windows-specific dependencies
├── schema/
│   └── ruleSchema.json         # Security rules configuration
├── templates/
│   └── dashboard.html          # Web dashboard template
├── README.md                   # This file
└── LICENSE                     # MIT License
```

## Quick Start

### Linux (Kali/Ubuntu/Debian)
```bash
# Method 1: Use installer script (recommended)
sudo chmod +x install_simple.sh
sudo ./install_simple.sh

# Method 2: Manual installation
sudo apt install python3-pip python3-dev libudev-dev
pip3 install -r requirements_linux.txt

# Run the application
sudo chmod +x run_dps.sh
sudo ./run_dps.sh

# Open browser to: http://localhost:8080
```

### Windows
```cmd
# Method 1: Use installer script (recommended)
install_windows.bat

# Method 2: Manual installation
pip install -r requirements_windows.txt

# Run application (as Administrator for full functionality)
python dps_app.py

# Open browser to: http://localhost:8080
```

### Cross-Platform (Core Features Only)
```bash
# Install minimal dependencies (limited functionality)
pip install -r requirements_app.txt

# Run application
python dps_app.py
```

## Features
- **Real-time Monitoring**: USB devices, processes, network connections
- **Web Dashboard**: Live monitoring interface at localhost:8080
- **Automatic Actions**: VPN activation, clipboard locking, filesystem remounting
- **Security Zones**: Normal → Sensitive → Ultra transitions
- **Built-in Testing**: Simulate events via dashboard buttons
- **Cross-Platform**: Works on Linux and Windows (with platform-specific features)

## Platform Support

### Linux Features (Full Functionality)
- USB device monitoring via udev
- Process monitoring
- Network connection tracking
- VPN control via NetworkManager
- Filesystem remounting
- Desktop notifications

### Windows Features (Core Functionality)
- Process monitoring
- Network connection tracking
- Basic USB detection
- Clipboard management
- System notifications

### Cross-Platform Features
- Web dashboard
- Security zone transitions
- Event logging
- Manual testing controls

## Usage

### Dashboard Features
- **Current Security Zone**: Normal → Sensitive → Ultra
- **Real-time Statistics**: Events processed, zone transitions, actions executed
- **System Monitoring**: CPU, Memory, Disk usage
- **Live Event Feed**: All detected events with timestamps
- **Test Controls**: Simulate USB and URL events

### Testing the System
1. **Built-in Test Buttons**: Use dashboard buttons to simulate events
2. **Real Hardware**: Plug in USB drives, open browsers
3. **Manual Testing**: Use curl commands to trigger events

### Expected Behavior
- **USB Device**: Plug in USB → Zone transitions to "Ultra" (red)
- **Sensitive Process**: Open browser → Zone transitions to "Sensitive" (orange)
- **Banking URL**: Visit banking sites → Triggers VPN activation

## Customization

### Modify Security Rules
Edit `schema/ruleSchema.json` to change:
- Zone transition conditions
- Actions to execute
- Priority levels

### Add New Processes
Edit `dps_app.py` to monitor additional processes or events.

## Security Notes
- Requires root/admin privileges for full functionality
- Use VMs for testing
- Some actions (filesystem remounting) can affect running applications

## Troubleshooting

### Linux
```bash
# Install missing system dependencies
sudo apt update
sudo apt install python3-pip python3-dev libudev-dev build-essential

# Install Python dependencies
pip3 install -r requirements_linux.txt

# For NetworkManager VPN support
sudo apt install network-manager openvpn
```

### Windows
```cmd
# Install Python dependencies
pip install -r requirements_windows.txt

# For WMI support (system monitoring)
pip install wmi

# Run as Administrator for full functionality
```

### Common Issues
- **Permission Errors**: 
  - Linux: Ensure running with `sudo`
  - Windows: Run Command Prompt as Administrator
- **Dashboard Not Loading**: Check if port 8080 is available
- **No Events Detected**: Verify hardware events are occurring
- **Import Errors**: 
  - Linux: Install `python3-dev` and `libudev-dev`
  - Windows: Install Visual C++ Build Tools if needed

### Dependencies Explained
- **flask**: Web dashboard framework
- **psutil**: Cross-platform system monitoring
- **pyudev** (Linux only): USB device monitoring
- **wmi** (Windows only): Windows Management Instrumentation