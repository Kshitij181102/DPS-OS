#!/usr/bin/env python3
"""
DPS-OS Unified Application
A single application with full privileges that monitors system events
and provides a web-based dashboard for real-time monitoring.
"""

import os
import sys
import json
import time
import threading
import subprocess
import platform
from datetime import datetime
from flask import Flask, render_template, jsonify, request
from werkzeug.serving import make_server
import psutil
import signal

# Platform-specific imports
IS_WINDOWS = platform.system() == 'Windows'
IS_LINUX = platform.system() == 'Linux'

if IS_LINUX:
    try:
        import pyudev
        PYUDEV_AVAILABLE = True
    except ImportError:
        PYUDEV_AVAILABLE = False
        print("Warning: pyudev not available. USB monitoring will be limited.")
else:
    PYUDEV_AVAILABLE = False

if IS_WINDOWS:
    try:
        import wmi
        WMI_AVAILABLE = True
    except ImportError:
        WMI_AVAILABLE = False
        print("Warning: wmi not available. Some Windows features will be limited.")

class DPSMonitor:
    def __init__(self):
        self.events = []
        self.max_events = 1000
        self.current_zone = "zone1"
        self.zones = {
            "zone1": {"name": "Normal", "color": "green"},
            "zone2": {"name": "Sensitive", "color": "orange"}, 
            "zone3": {"name": "Ultra", "color": "red"}
        }
        self.rules = self.load_rules()
        self.running = True
        self.stats = {
            "events_processed": 0,
            "zone_transitions": 0,
            "actions_executed": 0,
            "start_time": datetime.now()
        }
        
    def load_rules(self):
        """Load rules from schema or use defaults"""
        try:
            with open('schema/ruleSchema.json', 'r') as f:
                return json.load(f)
        except:
            return {
                "zones": self.zones,
                "edges": [
                    {
                        "from": "zone1", "to": "zone2",
                        "trigger": "openSensitiveUrl",
                        "conditions": {"urlPattern": ["*.bank.com", "*.payments.*"]},
                        "actions": ["enableVpn", "lockClipboard"],
                        "priority": 100
                    },
                    {
                        "from": "*", "to": "zone3", 
                        "trigger": "usbPlugged",
                        "conditions": {"deviceClass": ["mass_storage"]},
                        "actions": ["remountHomeRo", "notifyUser"],
                        "priority": 90
                    }
                ]
            }
    
    def add_event(self, event_type, data, action_taken=None):
        """Add event to monitoring log"""
        event = {
            "timestamp": datetime.now().isoformat(),
            "type": event_type,
            "data": data,
            "action": action_taken,
            "zone": self.current_zone
        }
        self.events.insert(0, event)
        if len(self.events) > self.max_events:
            self.events.pop()
        self.stats["events_processed"] += 1
        
    def evaluate_rules(self, trigger, event_data):
        """Evaluate rules and return matching edge"""
        candidates = []
        for edge in self.rules.get('edges', []):
            if edge['trigger'] != trigger:
                continue
                
            # Check conditions
            conditions = edge.get('conditions', {})
            if 'urlPattern' in conditions and 'url' in event_data:
                url = event_data['url']
                if not any(pattern.replace('*', '') in url for pattern in conditions['urlPattern']):
                    continue
                    
            candidates.append(edge)
            
        if not candidates:
            return None
            
        # Sort by priority
        candidates.sort(key=lambda e: e.get('priority', 0), reverse=True)
        return candidates[0]
    
    def execute_actions(self, actions):
        """Execute security actions"""
        results = []
        for action in actions:
            try:
                if action == "enableVpn":
                    result = self.enable_vpn()
                elif action == "lockClipboard":
                    result = self.lock_clipboard()
                elif action == "remountHomeRo":
                    result = self.remount_home_ro()
                elif action == "notifyUser":
                    result = self.notify_user()
                else:
                    result = f"Unknown action: {action}"
                    
                results.append(f"{action}: {result}")
                self.stats["actions_executed"] += 1
            except Exception as e:
                results.append(f"{action}: ERROR - {str(e)}")
                
        return results
    
    def enable_vpn(self):
        """Enable VPN connection"""
        try:
            if IS_LINUX:
                result = subprocess.run(['nmcli', 'connection', 'up', 'dps-vpn'], 
                                      capture_output=True, text=True, timeout=10)
                return "VPN enabled" if result.returncode == 0 else f"VPN failed: {result.stderr}"
            elif IS_WINDOWS:
                # Windows VPN control would require different approach
                return "VPN control not implemented for Windows"
            else:
                return "VPN control not available on this platform"
        except Exception as e:
            return f"VPN error: {str(e)}"
    
    def lock_clipboard(self):
        """Lock clipboard by clearing it"""
        try:
            if IS_LINUX:
                subprocess.run(['xsel', '--clear'], check=False)
                return "Clipboard locked (Linux)"
            elif IS_WINDOWS:
                # Windows clipboard clearing
                import win32clipboard
                win32clipboard.OpenClipboard()
                win32clipboard.EmptyClipboard()
                win32clipboard.CloseClipboard()
                return "Clipboard locked (Windows)"
            else:
                return "Clipboard lock not available"
        except ImportError:
            # Fallback for Windows without pywin32
            try:
                import subprocess
                subprocess.run(['powershell', '-command', 'Set-Clipboard', '-Value', '""'], 
                              check=False, capture_output=True)
                return "Clipboard locked (PowerShell)"
            except:
                return "Clipboard lock failed"
        except Exception as e:
            return f"Clipboard lock error: {str(e)}"
    
    def remount_home_ro(self):
        """Remount home directory as read-only"""
        try:
            if IS_LINUX:
                result = subprocess.run(['mount', '-o', 'remount,ro', '/home'], 
                                      capture_output=True, text=True)
                return "Home remounted RO" if result.returncode == 0 else "Remount failed"
            elif IS_WINDOWS:
                return "Filesystem remounting not applicable on Windows"
            else:
                return "Filesystem remounting not available"
        except Exception as e:
            return f"Remount error: {str(e)}"
    
    def notify_user(self):
        """Send desktop notification"""
        try:
            if IS_LINUX:
                subprocess.run(['notify-send', 'DPS-OS', 'Security zone transition detected'], 
                              check=False)
                return "User notified (Linux)"
            elif IS_WINDOWS:
                # Windows notification using PowerShell
                subprocess.run([
                    'powershell', '-command',
                    'Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.MessageBox]::Show("Security zone transition detected", "DPS-OS")'
                ], check=False, capture_output=True)
                return "User notified (Windows)"
            else:
                return "Notification sent (fallback)"
        except Exception as e:
            return f"Notification error: {str(e)}"
    
    def transition_zone(self, new_zone, reason):
        """Transition to new security zone"""
        old_zone = self.current_zone
        self.current_zone = new_zone
        self.stats["zone_transitions"] += 1
        self.add_event("zone_transition", {
            "from": old_zone,
            "to": new_zone,
            "reason": reason
        })

class USBMonitor:
    def __init__(self, dps_monitor):
        self.dps_monitor = dps_monitor
        self.platform = platform.system()
        
        if IS_LINUX and PYUDEV_AVAILABLE:
            self.context = pyudev.Context()
            self.monitor = pyudev.Monitor.from_netlink(self.context)
            self.monitor.filter_by('block')
        elif IS_WINDOWS and WMI_AVAILABLE:
            self.wmi_conn = wmi.WMI()
        
    def start_monitoring(self):
        """Start USB device monitoring"""
        if IS_LINUX and PYUDEV_AVAILABLE:
            return self._start_linux_monitoring()
        elif IS_WINDOWS:
            return self._start_windows_monitoring()
        else:
            return self._start_fallback_monitoring()
    
    def _start_linux_monitoring(self):
        """Linux USB monitoring using pyudev"""
        def monitor_usb():
            for device in iter(self.monitor.poll, None):
                if not self.dps_monitor.running:
                    break
                    
                if device.action == 'add':
                    device_info = {
                        "sysName": device.sys_name,
                        "devNode": device.device_node,
                        "deviceClass": "mass_storage",
                        "platform": "linux"
                    }
                    
                    self.dps_monitor.add_event("usb_plugged", device_info)
                    
                    # Evaluate rules
                    edge = self.dps_monitor.evaluate_rules("usbPlugged", device_info)
                    if edge:
                        actions = self.dps_monitor.execute_actions(edge.get('actions', []))
                        self.dps_monitor.transition_zone(edge['to'], f"USB device: {device.sys_name}")
                        self.dps_monitor.add_event("rule_triggered", edge, actions)
        
        thread = threading.Thread(target=monitor_usb, daemon=True)
        thread.start()
        return thread
    
    def _start_windows_monitoring(self):
        """Windows USB monitoring using WMI or psutil fallback"""
        def monitor_usb():
            seen_drives = set()
            # Get initial drives
            for partition in psutil.disk_partitions():
                if 'removable' in partition.opts:
                    seen_drives.add(partition.device)
            
            while self.dps_monitor.running:
                try:
                    current_drives = set()
                    for partition in psutil.disk_partitions():
                        if 'removable' in partition.opts:
                            current_drives.add(partition.device)
                    
                    new_drives = current_drives - seen_drives
                    for drive in new_drives:
                        device_info = {
                            "device": drive,
                            "deviceClass": "mass_storage",
                            "platform": "windows"
                        }
                        
                        self.dps_monitor.add_event("usb_plugged", device_info)
                        
                        # Evaluate rules
                        edge = self.dps_monitor.evaluate_rules("usbPlugged", device_info)
                        if edge:
                            actions = self.dps_monitor.execute_actions(edge.get('actions', []))
                            self.dps_monitor.transition_zone(edge['to'], f"USB device: {drive}")
                            self.dps_monitor.add_event("rule_triggered", edge, actions)
                    
                    seen_drives = current_drives
                    time.sleep(2)  # Check every 2 seconds
                    
                except Exception as e:
                    print(f"USB monitoring error: {e}")
                    time.sleep(5)
        
        thread = threading.Thread(target=monitor_usb, daemon=True)
        thread.start()
        return thread
    
    def _start_fallback_monitoring(self):
        """Fallback monitoring using psutil only"""
        def monitor_usb():
            print("USB monitoring: Using fallback mode (limited functionality)")
            seen_drives = set()
            
            while self.dps_monitor.running:
                try:
                    current_drives = set()
                    for partition in psutil.disk_partitions():
                        if 'removable' in partition.opts:
                            current_drives.add(partition.device)
                    
                    new_drives = current_drives - seen_drives
                    for drive in new_drives:
                        device_info = {
                            "device": drive,
                            "deviceClass": "mass_storage",
                            "platform": "fallback"
                        }
                        
                        self.dps_monitor.add_event("usb_plugged", device_info)
                    
                    seen_drives = current_drives
                    time.sleep(3)  # Check every 3 seconds
                    
                except Exception as e:
                    print(f"USB monitoring error: {e}")
                    time.sleep(5)
        
        thread = threading.Thread(target=monitor_usb, daemon=True)
        thread.start()
        return thread

class ProcessMonitor:
    def __init__(self, dps_monitor):
        self.dps_monitor = dps_monitor
        
        # Cross-platform sensitive processes
        base_processes = [
            'firefox', 'chrome', 'chromium', 'tor', 'wireshark', 
            'nmap', 'metasploit', 'burpsuite', 'sqlmap'
        ]
        
        # Windows-specific processes
        windows_processes = [
            'firefox.exe', 'chrome.exe', 'msedge.exe', 'iexplore.exe',
            'powershell.exe', 'cmd.exe', 'wireshark.exe', 'nmap.exe'
        ]
        
        # Linux-specific processes  
        linux_processes = [
            'firefox', 'chromium-browser', 'google-chrome', 'tor-browser',
            'wireshark', 'nmap', 'metasploit', 'burpsuite'
        ]
        
        if IS_WINDOWS:
            self.sensitive_processes = base_processes + windows_processes
        else:
            self.sensitive_processes = base_processes + linux_processes
        
    def start_monitoring(self):
        """Monitor running processes"""
        def monitor_processes():
            seen_processes = set()
            while self.dps_monitor.running:
                try:
                    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                        proc_name = proc.info['name'].lower()
                        
                        # Check if process name matches any sensitive process
                        is_sensitive = any(sensitive in proc_name for sensitive in self.sensitive_processes)
                        
                        if is_sensitive:
                            proc_id = f"{proc.info['pid']}_{proc_name}"
                            if proc_id not in seen_processes:
                                seen_processes.add(proc_id)
                                self.dps_monitor.add_event("sensitive_process", {
                                    "name": proc_name,
                                    "pid": proc.info['pid'],
                                    "cmdline": ' '.join(proc.info['cmdline'] or []),
                                    "platform": platform.system()
                                })
                                
                                # Trigger zone transition for sensitive processes
                                self.dps_monitor.transition_zone("zone2", f"Sensitive process: {proc_name}")
                                
                    time.sleep(5)
                except Exception as e:
                    print(f"Process monitoring error: {e}")
                    time.sleep(5)
        
        thread = threading.Thread(target=monitor_processes, daemon=True)
        thread.start()
        return thread

class NetworkMonitor:
    def __init__(self, dps_monitor):
        self.dps_monitor = dps_monitor
        
    def start_monitoring(self):
        """Monitor network connections"""
        def monitor_network():
            seen_connections = set()
            while self.dps_monitor.running:
                try:
                    connections = psutil.net_connections(kind='inet')
                    for conn in connections:
                        if conn.status == 'ESTABLISHED' and conn.raddr:
                            conn_id = f"{conn.raddr.ip}:{conn.raddr.port}"
                            if conn_id not in seen_connections:
                                seen_connections.add(conn_id)
                                self.dps_monitor.add_event("network_connection", {
                                    "remote_ip": conn.raddr.ip,
                                    "remote_port": conn.raddr.port,
                                    "local_port": conn.laddr.port,
                                    "status": conn.status
                                })
                    time.sleep(10)
                except Exception as e:
                    print(f"Network monitoring error: {e}")
                    time.sleep(10)
        
        thread = threading.Thread(target=monitor_network, daemon=True)
        thread.start()
        return thread

# Flask Web Interface
app = Flask(__name__)
dps_monitor = DPSMonitor()

@app.route('/')
def dashboard():
    return render_template('dashboard.html', platform=platform.system())

@app.route('/api/status')
def api_status():
    uptime = datetime.now() - dps_monitor.stats["start_time"]
    return jsonify({
        "current_zone": dps_monitor.current_zone,
        "zone_info": dps_monitor.zones[dps_monitor.current_zone],
        "stats": {
            **dps_monitor.stats,
            "uptime_seconds": int(uptime.total_seconds())
        },
        "system_info": {
            "cpu_percent": psutil.cpu_percent(),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage('/').percent
        }
    })

@app.route('/api/events')
def api_events():
    limit = request.args.get('limit', 50, type=int)
    return jsonify(dps_monitor.events[:limit])

@app.route('/api/rules')
def api_rules():
    return jsonify(dps_monitor.rules)

@app.route('/api/simulate_event', methods=['POST'])
def api_simulate_event():
    """Simulate an event for testing"""
    data = request.json
    event_type = data.get('type')
    event_data = data.get('data', {})
    
    if event_type == 'usb':
        edge = dps_monitor.evaluate_rules("usbPlugged", event_data)
        if edge:
            actions = dps_monitor.execute_actions(edge.get('actions', []))
            dps_monitor.transition_zone(edge['to'], "Simulated USB event")
            dps_monitor.add_event("simulated_usb", event_data, actions)
    elif event_type == 'url':
        edge = dps_monitor.evaluate_rules("openSensitiveUrl", event_data)
        if edge:
            actions = dps_monitor.execute_actions(edge.get('actions', []))
            dps_monitor.transition_zone(edge['to'], f"Sensitive URL: {event_data.get('url')}")
            dps_monitor.add_event("simulated_url", event_data, actions)
    
    return jsonify({"status": "success"})

def create_html_template():
    """Create the dashboard HTML template"""
    os.makedirs('templates', exist_ok=True)
    
    html_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DPS-OS Monitor</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #1a1a1a; color: #fff; }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        .header { text-align: center; margin-bottom: 30px; }
        .header h1 { color: #00ff88; font-size: 2.5em; margin-bottom: 10px; }
        .status-bar { display: flex; justify-content: space-between; background: #2a2a2a; padding: 15px; border-radius: 8px; margin-bottom: 20px; }
        .zone-indicator { padding: 10px 20px; border-radius: 5px; font-weight: bold; }
        .zone-normal { background: #28a745; }
        .zone-sensitive { background: #fd7e14; }
        .zone-ultra { background: #dc3545; }
        .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-bottom: 20px; }
        .stat-card { background: #2a2a2a; padding: 15px; border-radius: 8px; text-align: center; }
        .stat-value { font-size: 2em; font-weight: bold; color: #00ff88; }
        .stat-label { color: #ccc; margin-top: 5px; }
        .events-section { background: #2a2a2a; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
        .events-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; }
        .event-item { background: #3a3a3a; padding: 10px; margin-bottom: 10px; border-radius: 5px; border-left: 4px solid #00ff88; }
        .event-timestamp { color: #888; font-size: 0.9em; }
        .event-type { color: #00ff88; font-weight: bold; }
        .event-data { color: #ccc; margin-top: 5px; }
        .controls { background: #2a2a2a; padding: 20px; border-radius: 8px; }
        .btn { background: #007bff; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; margin: 5px; }
        .btn:hover { background: #0056b3; }
        .btn-danger { background: #dc3545; }
        .btn-danger:hover { background: #c82333; }
        .system-info { display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; margin-top: 15px; }
        .progress-bar { background: #444; height: 20px; border-radius: 10px; overflow: hidden; }
        .progress-fill { height: 100%; background: linear-gradient(90deg, #28a745, #ffc107, #dc3545); transition: width 0.3s; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🛡️ DPS-OS Monitor</h1>
            <p>Dynamic Privacy-Shifting Operating System</p>
        </div>
        
        <div class="status-bar">
            <div>
                <strong>Current Zone:</strong>
                <span id="current-zone" class="zone-indicator">Loading...</span>
            </div>
            <div>
                <strong>Uptime:</strong> <span id="uptime">0s</span>
            </div>
            <div>
                <strong>Status:</strong> <span style="color: #00ff88;">● Active</span>
            </div>
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <div class="stat-value" id="events-count">0</div>
                <div class="stat-label">Events Processed</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="transitions-count">0</div>
                <div class="stat-label">Zone Transitions</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="actions-count">0</div>
                <div class="stat-label">Actions Executed</div>
            </div>
        </div>
        
        <div class="system-info">
            <div class="stat-card">
                <div class="stat-label">CPU Usage</div>
                <div class="progress-bar">
                    <div class="progress-fill" id="cpu-progress"></div>
                </div>
                <div id="cpu-percent">0%</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Memory Usage</div>
                <div class="progress-bar">
                    <div class="progress-fill" id="memory-progress"></div>
                </div>
                <div id="memory-percent">0%</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Disk Usage</div>
                <div class="progress-bar">
                    <div class="progress-fill" id="disk-progress"></div>
                </div>
                <div id="disk-percent">0%</div>
            </div>
        </div>
        
        <div class="events-section">
            <div class="events-header">
                <h3>Recent Events</h3>
                <button class="btn" onclick="refreshEvents()">Refresh</button>
            </div>
            <div id="events-list">Loading events...</div>
        </div>
        
        <div class="controls">
            <h3>Test Controls</h3>
            <button class="btn" onclick="simulateUSB()">Simulate USB Event</button>
            <button class="btn" onclick="simulateURL()">Simulate Banking URL</button>
            <button class="btn btn-danger" onclick="clearEvents()">Clear Events</button>
        </div>
    </div>

    <script>
        function updateStatus() {
            fetch('/api/status')
                .then(response => response.json())
                .then(data => {
                    const zone = data.current_zone;
                    const zoneElement = document.getElementById('current-zone');
                    zoneElement.textContent = data.zone_info.name;
                    zoneElement.className = 'zone-indicator zone-' + data.zone_info.color;
                    
                    document.getElementById('uptime').textContent = formatUptime(data.stats.uptime_seconds);
                    document.getElementById('events-count').textContent = data.stats.events_processed;
                    document.getElementById('transitions-count').textContent = data.stats.zone_transitions;
                    document.getElementById('actions-count').textContent = data.stats.actions_executed;
                    
                    updateProgressBar('cpu', data.system_info.cpu_percent);
                    updateProgressBar('memory', data.system_info.memory_percent);
                    updateProgressBar('disk', data.system_info.disk_percent);
                });
        }
        
        function updateProgressBar(type, percent) {
            document.getElementById(type + '-progress').style.width = percent + '%';
            document.getElementById(type + '-percent').textContent = percent.toFixed(1) + '%';
        }
        
        function formatUptime(seconds) {
            const hours = Math.floor(seconds / 3600);
            const minutes = Math.floor((seconds % 3600) / 60);
            const secs = seconds % 60;
            return hours + 'h ' + minutes + 'm ' + secs + 's';
        }
        
        function refreshEvents() {
            fetch('/api/events?limit=20')
                .then(response => response.json())
                .then(events => {
                    const eventsList = document.getElementById('events-list');
                    if (events.length === 0) {
                        eventsList.innerHTML = '<p>No events yet</p>';
                        return;
                    }
                    
                    eventsList.innerHTML = events.map(event => `
                        <div class="event-item">
                            <div class="event-timestamp">${new Date(event.timestamp).toLocaleString()}</div>
                            <div class="event-type">${event.type}</div>
                            <div class="event-data">${JSON.stringify(event.data)}</div>
                            ${event.action ? '<div class="event-data">Actions: ' + JSON.stringify(event.action) + '</div>' : ''}
                        </div>
                    `).join('');
                });
        }
        
        function simulateUSB() {
            fetch('/api/simulate_event', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    type: 'usb',
                    data: {sysName: 'test_usb', deviceClass: 'mass_storage'}
                })
            }).then(() => {
                setTimeout(refreshEvents, 500);
                setTimeout(updateStatus, 500);
            });
        }
        
        function simulateURL() {
            fetch('/api/simulate_event', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    type: 'url',
                    data: {url: 'https://test.bank.com/login'}
                })
            }).then(() => {
                setTimeout(refreshEvents, 500);
                setTimeout(updateStatus, 500);
            });
        }
        
        function clearEvents() {
            if (confirm('Clear all events?')) {
                // This would need a backend endpoint
                location.reload();
            }
        }
        
        // Auto-refresh every 2 seconds
        setInterval(updateStatus, 2000);
        setInterval(refreshEvents, 5000);
        
        // Initial load
        updateStatus();
        refreshEvents();
    </script>
</body>
</html>'''
    
    with open('templates/dashboard.html', 'w', encoding='utf-8') as f:
        f.write(html_content)

def main():
    """Main application entry point"""
    print("🛡️  DPS-OS Unified Monitor Starting...")
    
    # Check if running with appropriate privileges
    if IS_LINUX:
        if os.geteuid() != 0:
            print("⚠️  Warning: Not running as root. Some features may not work.")
            print("   Run with: sudo python3 dps_app.py")
    elif IS_WINDOWS:
        import ctypes
        if not ctypes.windll.shell32.IsUserAnAdmin():
            print("⚠️  Warning: Not running as Administrator. Some features may not work.")
            print("   Run Command Prompt as Administrator and try again.")
    
    # Create HTML template
    create_html_template()
    
    # Initialize monitors
    usb_monitor = USBMonitor(dps_monitor)
    process_monitor = ProcessMonitor(dps_monitor)
    network_monitor = NetworkMonitor(dps_monitor)
    
    # Start monitoring threads
    print("🔍 Starting USB monitoring...")
    usb_monitor.start_monitoring()
    
    print("🔍 Starting process monitoring...")
    process_monitor.start_monitoring()
    
    print("🔍 Starting network monitoring...")
    network_monitor.start_monitoring()
    
    # Handle shutdown gracefully
    def signal_handler(sig, frame):
        print("\n🛑 Shutting down DPS-OS Monitor...")
        dps_monitor.running = False
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Start web server with fallback ports
    ports_to_try = [5000, 5001, 8081, 8082, 3000]
    server_started = False
    
    for port in ports_to_try:
        try:
            print(f"🌐 Trying to start web dashboard on http://localhost:{port}")
            print("📊 Open your browser to view the monitoring dashboard")
            print("🔧 Use Ctrl+C to stop")
            app.run(host='127.0.0.1', port=port, debug=False, threaded=True)
            server_started = True
            break
        except OSError as e:
            if "Address already in use" in str(e) or "access" in str(e).lower():
                print(f"⚠️  Port {port} is not available, trying next port...")
                continue
            else:
                print(f"❌ Error starting web server on port {port}: {e}")
                continue
        except Exception as e:
            print(f"❌ Unexpected error starting web server on port {port}: {e}")
            continue
    
    if not server_started:
        print("❌ Could not start web server on any available port")
        print("💡 Try running as Administrator or check firewall settings")
        sys.exit(1)

if __name__ == '__main__':
    main()