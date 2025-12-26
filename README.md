# DPS-OS — Dynamic Privacy-Shifting OS

A cross-platform security monitoring system that automatically adjusts security postures based on detected threats. Features real-time USB monitoring, clipboard protection, financial website detection, and a web-based dashboard.

## 🌟 Features

- **🔒 USB Security**: Automatic Ultra mode when USB devices are detected
- **📋 Clipboard Protection**: Continuous clipboard clearing in high-security zones
- **🏦 Financial Website Detection**: Enhanced detection of banking and financial sites
- **🖥️ Cross-Platform**: Works on Windows, Linux, and macOS
- **📊 Real-Time Dashboard**: Web interface for monitoring and control
- **⚙️ Configurable**: JSON-based configuration for easy customization
- **🔄 Zone-Based Security**: Normal → Sensitive → Ultra security transitions

## 🚀 Quick Start

### 1. Installation

**Automatic (Recommended):**
```bash
python install.py
```

**Manual Installation:**

**Windows:**
```cmd
pip install flask psutil wmi
```

**Linux (Ubuntu/Debian/Kali):**
```bash
sudo apt update
sudo apt install python3-pip python3-dev libudev-dev build-essential libnotify-bin
pip3 install flask psutil pyudev
```

**macOS:**
```bash
pip3 install flask psutil
```

### 2. Configuration

Edit `config.json` to customize behavior:
- Security zones and colors
- Monitoring intervals
- Financial keywords for URL detection
- Security actions and commands
- Dashboard settings

### 3. Run the Application

```bash
python dps_app.py
```

Then open your browser to: **http://localhost:5000**

## 📁 Project Structure

```
dps-os/
├── dps_app.py              # Main application
├── config.json             # Configuration file
├── install.py              # Cross-platform installer
├── requirements_windows.txt # Windows dependencies
├── templates/
│   └── dashboard.html      # Web dashboard
├── README.md               # This file
└── LICENSE                 # MIT License
```

## ⚙️ Configuration

The `config.json` file controls all aspects of DPS-OS behavior:

### System Settings
```json
{
  "system": {
    "web_port": 5000,
    "max_events": 1000,
    "debug_mode": false
  }
}
```

### Security Zones
```json
{
  "security_zones": {
    "zone1": {"name": "Normal", "color": "green"},
    "zone2": {"name": "Sensitive", "color": "orange"},
    "zone3": {"name": "Ultra", "color": "red"}
  }
}
```

### USB Monitoring
```json
{
  "usb_monitoring": {
    "enabled": true,
    "auto_ultra_mode": true,
    "persistent_lock": true,
    "actions_on_connect": ["lockClipboard", "notifyUser"]
  }
}
```

### Financial URL Detection
```json
{
  "url_monitoring": {
    "enabled": true,
    "financial_keywords": ["bank", "paypal", "crypto", "trading"],
    "monitored_browsers": ["chrome.exe", "firefox.exe"]
  }
}
```

## 🔧 Platform-Specific Features

### Windows
- Process monitoring via WMI
- PowerShell-based clipboard control
- Windows notification system
- USB detection via psutil

### Linux
- Enhanced USB monitoring via pyudev
- NetworkManager VPN control
- Desktop notifications via notify-send
- Filesystem remounting capabilities

### macOS
- Native clipboard control via pbcopy
- AppleScript notifications
- Process monitoring via psutil

## 🛡️ Security Zones

### Normal Zone (Green)
- Default state
- Basic monitoring active
- No restrictions

### Sensitive Zone (Orange)
- Triggered by financial websites
- Enhanced monitoring
- VPN activation
- Clipboard protection

### Ultra Zone (Red)
- Triggered by USB devices
- Maximum security
- Persistent until USB removed
- Continuous clipboard clearing
- All security measures active

## 🧪 Testing

### Built-in Test Controls
Use the dashboard buttons to test:
1. **Simulate USB Event** - Triggers Ultra mode
2. **Simulate Banking URL** - Triggers Sensitive mode

### Manual Testing
```bash
# Test USB simulation
curl -X POST -H "Content-Type: application/json" \
  -d '{"type":"usb","data":{"device":"test_usb"}}' \
  http://localhost:5000/api/simulate_event

# Test bank URL simulation  
curl -X POST -H "Content-Type: application/json" \
  -d '{"type":"url","data":{"url":"https://chase.com/login"}}' \
  http://localhost:5000/api/simulate_event
```

## 🔍 Monitoring

### What Gets Monitored
- **USB Devices**: Removable storage detection
- **Processes**: Browsers and sensitive applications
- **Network**: New connections and traffic
- **URLs**: Financial and banking websites
- **System**: CPU, memory, disk usage

### Event Types
- `usb_plugged` / `usb_removed`
- `bank_url_detected`
- `sensitive_process`
- `network_connection`
- `zone_transition`
- `security_lockdown` / `security_unlock`

## 🚨 Troubleshooting

### Common Issues

**Port Already in Use:**
- Change `web_port` in config.json
- Default tries ports: 5000, 5001, 8081, 8082, 3000

**Permission Errors:**
- **Windows**: Run Command Prompt as Administrator
- **Linux**: Run with `sudo python3 dps_app.py`
- **macOS**: Grant necessary permissions in System Preferences

**Dependencies Missing:**
```bash
# Reinstall dependencies
python install.py

# Or manually:
pip install flask psutil
```

**USB Monitoring Not Working:**
- **Linux**: Install pyudev: `pip3 install pyudev`
- **Windows**: Install WMI: `pip install wmi`
- Check if running with admin/root privileges

### Debug Mode
Enable debug mode in config.json:
```json
{
  "system": {
    "debug_mode": true
  }
}
```

## 🔒 Security Notes

### Privileges Required
- **Windows**: Administrator rights for full functionality
- **Linux**: Root access for USB monitoring and filesystem operations
- **macOS**: Standard user with notification permissions

### Safe Testing
- Use virtual machines for testing
- Take system snapshots before testing
- Some actions (filesystem remounting) can affect running applications
- Test in isolated environments first

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test on multiple platforms
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details.

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section
2. Review config.json settings
3. Enable debug mode for detailed logging
4. Check platform-specific requirements