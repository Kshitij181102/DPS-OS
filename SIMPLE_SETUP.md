# DPS-OS Unified Application - Simple Setup

## What This Is
A single Python application that runs with full privileges and provides:
- Real-time system monitoring (USB, processes, network)
- Web-based dashboard for live monitoring
- Automatic security zone transitions
- Built-in event simulation and testing

## Quick Start on Kali Linux

### 1. Copy Files to Kali VM
Transfer these files to your Kali Linux VM:
- `dps_app.py` (main application)
- `requirements_app.txt` (dependencies)
- `run_dps.sh` (launcher script)
- `schema/` folder (rules configuration)

### 2. Run the Application
```bash
# Make launcher executable
chmod +x run_dps.sh

# Run with full privileges
sudo ./run_dps.sh
```

### 3. Access the Dashboard
Open your browser and go to: **http://localhost:8080**

## What You'll See

### Dashboard Features
- **Current Security Zone**: Normal → Sensitive → Ultra
- **Real-time Statistics**: Events processed, zone transitions, actions executed
- **System Monitoring**: CPU, Memory, Disk usage
- **Live Event Feed**: All detected events with timestamps
- **Test Controls**: Simulate USB and URL events

### Automatic Monitoring
The application automatically monitors:
- **USB Devices**: Plugging in storage devices triggers security lockdown
- **Sensitive Processes**: Firefox, Chrome, Wireshark, Metasploit, etc.
- **Network Connections**: New outbound connections
- **System Resources**: Performance metrics

### Security Actions
When events are detected, the system can:
- **Enable VPN**: Activate NetworkManager VPN connection
- **Lock Clipboard**: Clear clipboard contents
- **Remount Filesystems**: Make /home read-only
- **Send Notifications**: Desktop alerts
- **Zone Transitions**: Automatically shift security posture

## Testing the System

### Built-in Test Buttons
Use the dashboard buttons to test:
1. **Simulate USB Event**: Triggers mass storage device detection
2. **Simulate Banking URL**: Triggers sensitive website detection

### Manual Testing
```bash
# In another terminal, simulate events:

# USB device
echo '{"trigger":"usbPlugged","device":{"sysName":"sdb1","deviceClass":"mass_storage"}}' | nc localhost 8080

# Banking URL
curl -X POST http://localhost:8080/api/simulate_event \
  -H "Content-Type: application/json" \
  -d '{"type":"url","data":{"url":"https://test.bank.com"}}'
```

### Real Hardware Testing
- Plug in a USB drive → Should trigger zone transition to "Ultra"
- Open Firefox/Chrome → Should detect sensitive process
- Visit banking websites → Should trigger VPN activation

## Expected Behavior

### Normal Operation
1. Application starts with "Normal" zone (green)
2. Dashboard shows 0 events initially
3. System monitoring displays current resource usage

### USB Device Detection
1. Plug in USB device
2. Zone transitions to "Ultra" (red)
3. System attempts to remount /home as read-only
4. Event appears in dashboard feed

### Sensitive URL Detection
1. Visit banking website
2. Zone transitions to "Sensitive" (orange)  
3. System attempts to enable VPN
4. Clipboard gets locked/cleared

## Troubleshooting

### Application Won't Start
```bash
# Install missing dependencies
sudo apt update
sudo apt install python3-pip python3-dev libudev-dev
sudo pip3 install flask pyudev psutil
```

### Permission Errors
```bash
# Ensure running as root
sudo python3 dps_app.py
```

### Dashboard Not Loading
- Check if port 8080 is available
- Try accessing via VM's IP address
- Check firewall settings

### No Events Detected
- Verify USB devices are being plugged in
- Check if processes are actually starting
- Look at terminal output for error messages

## Customization

### Modify Rules
Edit `schema/ruleSchema.json` to change:
- Which URLs trigger sensitive mode
- What actions are taken
- Zone transition conditions

### Add New Monitoring
The application can be extended to monitor:
- File system changes
- Keyboard/mouse input
- Screen recording attempts
- Bluetooth devices
- WiFi connections

## Security Notes

### Privileges Required
The application needs root access for:
- USB device monitoring (udev)
- Network management (VPN control)
- Filesystem operations (remounting)
- Process monitoring (system-wide)

### Safe Testing
- Use a VM for testing
- Take snapshots before testing
- Don't test on production systems
- Some actions (like remounting /home) can break running applications

## Architecture

### Single Application Design
- **Main Thread**: Flask web server
- **USB Monitor Thread**: Watches udev events
- **Process Monitor Thread**: Scans running processes
- **Network Monitor Thread**: Tracks connections
- **Event Handler**: Processes rules and executes actions

### Data Flow
1. Hardware/software event occurs
2. Monitor thread detects event
3. Rule engine evaluates conditions
4. Actions are executed if rules match
5. Event is logged and displayed in dashboard
6. Zone transition occurs if specified

This unified design makes it easy to deploy, monitor, and test the entire DPS-OS system from a single application with a web-based interface.