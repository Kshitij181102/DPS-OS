# DPS-OS Kali Linux Setup & Testing Guide

## Prerequisites
- Kali Linux VM with sudo access
- At least 2GB RAM and 10GB disk space
- Network connectivity for package installation

## Step 1: System Preparation

### Update Kali Linux
```bash
sudo apt update && sudo apt upgrade -y
```

### Install Required System Packages
```bash
sudo apt install -y python3 python3-pip python3-venv git curl
sudo apt install -y python3-dev build-essential
sudo apt install -y network-manager wmctrl xsel
sudo apt install -y libudev-dev pkg-config
```

### Install Node.js for UI (optional)
```bash
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs
```

## Step 2: Project Setup

### Clone/Copy Project Files
```bash
# If you have the files locally, copy them to Kali
# Or create the project structure manually
mkdir -p ~/dps-os
cd ~/dps-os

# Copy all your project files here
# You can use scp, shared folders, or recreate the structure
```

### Create Python Virtual Environment
```bash
cd ~/dps-os
python3 -m venv .venv
source .venv/bin/activate
```

### Install Python Dependencies
```bash
pip install pyudev watchdog jsonschema psutil flask
```

## Step 3: Configuration Setup

### Create Required Directories
```bash
mkdir -p ~/dps-os/logs
mkdir -p ~/dps-os/data
sudo mkdir -p /var/run/dpsos
sudo chmod 755 /var/run/dpsos
```

### Set Execute Permissions
```bash
chmod +x daemon/daemon.py
chmod +x watchers/udevWatcher.py
chmod +x watchers/nativeHostBrowser.py
chmod +x agents/*.py
```

### Create Test VPN Connection (for testing)
```bash
# Create a dummy VPN connection for testing
sudo nmcli connection add type vpn con-name dps-vpn ifname -- vpn-type openvpn
```

## Step 4: Testing the System

### Terminal 1: Start the Daemon
```bash
cd ~/dps-os
source .venv/bin/activate
python daemon/daemon.py --db data/config.sqlite
```

You should see:
```
DPSDaemon listening on /var/run/dpsos.sock
```

### Terminal 2: Test USB Watcher
```bash
cd ~/dps-os
source .venv/bin/activate
python watchers/udevWatcher.py --sock /var/run/dpsos.sock
```

### Terminal 3: Test Manual Events
```bash
# Test sending events manually
cd ~/dps-os
echo '{"trigger":"usbPlugged","device":{"sysName":"sdb1","devNode":"/dev/sdb1"}}' | nc -U /var/run/dpsos.sock
```

### Terminal 4: Test Individual Agents
```bash
# Test VPN toggler
python agents/vpnToggler.py up

# Test clipboard locker (run in background)
python agents/clipboardLocker.py &

# Test window hider
python agents/windowHider.py "Firefox"
```

## Step 5: Browser Extension Testing

### Install Chrome/Chromium
```bash
sudo apt install -y chromium
```

### Load Extension
1. Open Chromium
2. Go to `chrome://extensions/`
3. Enable "Developer mode"
4. Click "Load unpacked"
5. Select the `ext/browser/` directory

### Register Native Messaging Host
```bash
# Create native messaging host manifest
mkdir -p ~/.config/chromium/NativeMessagingHosts/
cat > ~/.config/chromium/NativeMessagingHosts/com.dpsos.nativehost.json << EOF
{
  "name": "com.dpsos.nativehost",
  "description": "DPS-OS Native Host",
  "path": "$(pwd)/watchers/nativeHostBrowser.py",
  "type": "stdio",
  "allowed_origins": ["chrome-extension://*/"]
}
EOF

# Make native host executable
chmod +x watchers/nativeHostBrowser.py
```

## Step 6: UI Testing (Optional)

### Setup React UI
```bash
cd ui/webapp
npm install
npm start
```

The UI will be available at `http://localhost:3000`

## Step 7: Comprehensive Testing

### Test Scenario 1: USB Event Flow
1. Start daemon and udev watcher
2. Insert USB device or simulate:
   ```bash
   # Simulate USB event
   echo '{"trigger":"usbPlugged","device":{"sysName":"sdb1"}}' | nc -U /var/run/dpsos.sock
   ```
3. Check daemon logs for rule evaluation
4. Verify actions are triggered

### Test Scenario 2: Browser URL Detection
1. Start daemon and native host
2. Open browser with extension loaded
3. Navigate to `https://test.bank.com`
4. Check daemon logs for URL events
5. Verify VPN and clipboard actions

### Test Scenario 3: Manual Rule Testing
```bash
# Test sensitive URL trigger
echo '{"trigger":"openSensitiveUrl","url":"https://payments.example.com"}' | nc -U /var/run/dpsos.sock

# Check if VPN connection attempts
nmcli connection show --active
```

## Step 8: Security Testing

### Test Socket Permissions
```bash
# Try accessing socket as different user
sudo -u nobody echo '{"test":"event"}' | nc -U /var/run/dpsos.sock
# Should fail with permission denied
```

### Test Malformed Events
```bash
# Send invalid JSON
echo 'invalid json' | nc -U /var/run/dpsos.sock

# Send oversized payload
python3 -c "print('{'*10000)" | nc -U /var/run/dpsos.sock
```

## Step 9: Monitoring & Debugging

### Check System Logs
```bash
# Monitor daemon output
tail -f ~/dps-os/logs/daemon.log

# Check system logs
sudo journalctl -f | grep dpsos
```

### Debug Network Manager
```bash
# Check VPN connections
nmcli connection show
nmcli device status

# Monitor NetworkManager logs
sudo journalctl -u NetworkManager -f
```

### Monitor USB Events
```bash
# Watch udev events
sudo udevadm monitor --property

# List USB devices
lsusb
```

## Step 10: Performance Testing

### Load Testing
```bash
# Send multiple events rapidly
for i in {1..100}; do
  echo '{"trigger":"usbPlugged","device":{"sysName":"test'$i'"}}' | nc -U /var/run/dpsos.sock
done
```

### Resource Monitoring
```bash
# Monitor daemon resource usage
top -p $(pgrep -f daemon.py)

# Check memory usage
ps aux | grep python
```

## Troubleshooting

### Common Issues

1. **Socket Permission Denied**
   ```bash
   sudo chown $USER:$USER /var/run/dpsos.sock
   sudo chmod 660 /var/run/dpsos.sock
   ```

2. **Python Module Not Found**
   ```bash
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

3. **VPN Connection Fails**
   ```bash
   # Check NetworkManager status
   sudo systemctl status NetworkManager
   
   # List available connections
   nmcli connection show
   ```

4. **Browser Extension Not Working**
   - Check extension is loaded and enabled
   - Verify native messaging host path is correct
   - Check browser console for errors

### Debug Commands
```bash
# Test socket connectivity
nc -U /var/run/dpsos.sock < /dev/null

# Check if daemon is listening
sudo netstat -xl | grep dpsos

# Verify file permissions
ls -la /var/run/dpsos.sock
ls -la daemon/daemon.py
```

## Expected Results

### Successful Test Indicators
- Daemon starts without errors
- USB events trigger rule evaluation
- Browser URLs are detected and forwarded
- VPN connections toggle (may fail without real VPN config)
- Clipboard clearing works
- No permission errors in logs
- UI loads and displays rules correctly

### Performance Benchmarks
- Event processing: < 100ms
- Memory usage: < 50MB for daemon
- CPU usage: < 5% under normal load
- Socket response time: < 10ms

## Next Steps After Testing
1. Review logs for any errors or warnings
2. Test with real VPN configurations
3. Add custom rules via UI
4. Test with different USB device types
5. Implement additional security hardening
6. Set up systemd service for production use

## Production Deployment
Once testing is complete, use the installation script:
```bash
sudo ./system/install.sh
sudo systemctl start dpsos
sudo systemctl enable dpsos
```