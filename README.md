# DPS-OS — Dynamic Privacy-Shifting OS

A unified application that monitors system events and automatically adjusts security postures with real-time web dashboard.

## Project Structure
```
dps-os/
├── dps_app.py              # Main unified application
├── run_dps.sh              # Launcher script  
├── install_simple.sh       # Dependency installer
├── requirements_app.txt    # Python dependencies
├── schema/
│   └── ruleSchema.json     # Security rules configuration
├── templates/
│   └── dashboard.html      # Web dashboard template
├── README.md               # This file
└── LICENSE                 # MIT License
```

## Quick Start

### Linux (Kali/Ubuntu/Debian)
```bash
# 1. Install dependencies
sudo chmod +x install_simple.sh
sudo ./install_simple.sh

# 2. Run the application
sudo chmod +x run_dps.sh
sudo ./run_dps.sh

# 3. Open browser to: http://localhost:8080
```

### Windows
```cmd
# Install dependencies
pip install flask psutil

# Run application
python dps_app.py
```

## Features
- **Real-time Monitoring**: USB devices, processes, network connections
- **Web Dashboard**: Live monitoring interface at localhost:8080
- **Automatic Actions**: VPN activation, clipboard locking, filesystem remounting
- **Security Zones**: Normal → Sensitive → Ultra transitions
- **Built-in Testing**: Simulate events via dashboard buttons

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
# Install missing dependencies
sudo apt install python3-pip python3-dev libudev-dev
sudo pip3 install flask pyudev psutil
```

### Windows
```cmd
# Install missing dependencies
pip install flask psutil
```

### Common Issues
- **Permission Errors**: Ensure running as root/admin
- **Dashboard Not Loading**: Check if port 8080 is available
- **No Events Detected**: Verify hardware events are occurring