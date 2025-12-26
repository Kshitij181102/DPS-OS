#!/usr/bin/env python3
"""
DPS-OS Unified Application
A cross-platform application that monitors system events and automatically 
adjusts security postures with real-time web dashboard.

Supports: Windows, Linux, macOS
Features: USB monitoring, clipboard protection, URL detection, process monitoring
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
import psutil
import signal

# Platform detection
IS_WINDOWS = platform.system() == 'Windows'
IS_LINUX = platform.system() == 'Linux'
IS_MACOS = platform.system() == 'Darwin'

# Platform-specific imports
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

class ConfigManager:
    """Manages configuration loading and validation"""
    
    def __init__(self, config_file='config.json'):
        self.config_file = config_file
        self.config = self.load_config()
    
    def load_config(self):
        """Load configuration from JSON file with fallback defaults"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                print(f"✅ Configuration loaded from {self.config_file}")
                return config
        except FileNotFoundError:
            print(f"⚠️  Config file {self.config_file} not found, using defaults")
            return self.get_default_config()
        except json.JSONDecodeError as e:
            print(f"❌ Error parsing config file: {e}")
            print("Using default configuration")
            return self.get_default_config()
    
    def get_default_config(self):
        """Return default configuration if file is missing"""
        return {
            "system": {"web_port": 5000, "max_events": 1000, "debug_mode": False},
            "usb_monitoring": {"enabled": True, "auto_ultra_mode": True, "persistent_lock": True},
            "clipboard_protection": {"enabled": True, "continuous_clear_in_ultra": True},
            "url_monitoring": {"enabled": True, "auto_sensitive_mode": True},
            "process_monitoring": {"enabled": True, "auto_sensitive_mode": True},
            "network_monitoring": {"enabled": True},
            "security_actions": {"vpn": {"enabled": True}, "clipboard": {"enabled": True}},
            "dashboard": {"enabled": True, "auto_refresh_seconds": 2}
        }
    
    def get(self, key_path, default=None):
        """Get configuration value using dot notation (e.g., 'system.web_port')"""
        keys = key_path.split('.')
        value = self.config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value
    
    def save_config(self):
        """Save current configuration to file"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2)
            print(f"✅ Configuration saved to {self.config_file}")
        except Exception as e:
            print(f"❌ Error saving config: {e}")

# Global configuration manager
config = ConfigManager()

class DPSMonitor:
    """Main monitoring class that coordinates all security monitoring"""
    
    def __init__(self):
        self.events = []
        self.max_events = config.get('system.max_events', 1000)
        self.current_zone = "zone1"
        
        # Load zones from config
        self.zones = config.get('security_zones', {
            "zone1": {"name": "Normal", "color": "green"},
            "zone2": {"name": "Sensitive", "color": "orange"}, 
            "zone3": {"name": "Ultra", "color": "red"}
        })
        
        self.running = True
        self.stats = {
            "events_processed": 0,
            "zone_transitions": 0,
            "actions_executed": 0,
            "start_time": datetime.now()
        }
        
        # USB tracking for persistent Ultra mode
        self.connected_usb_devices = set()
        self.ultra_mode_locked = False
        
        # Clipboard monitoring
        self.clipboard_blocked = False
        self.clipboard_monitor_thread = None
        
        # Load financial keywords from config
        self.bank_url_patterns = config.get('url_monitoring.financial_keywords', [
            'bank', 'banking', 'finance', 'payment', 'paypal', 'login'
        ])
        
        print(f"🔧 DPS Monitor initialized with {len(self.bank_url_patterns)} financial keywords")
    
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
        
        if config.get('system.debug_mode', False):
            print(f"📝 Event: {event_type} - {data}")
    
    def execute_actions(self, actions):
        """Execute security actions based on configuration"""
        results = []
        for action in actions:
            try:
                if action == "enableVpn" and config.get('security_actions.vpn.enabled', True):
                    result = self.enable_vpn()
                elif action == "lockClipboard" and config.get('security_actions.clipboard.enabled', True):
                    result = self.lock_clipboard()
                elif action == "unlockClipboard":
                    result = self.unlock_clipboard()
                elif action == "remountHomeRo" and config.get('security_actions.filesystem.enabled', True):
                    result = self.remount_home_ro()
                elif action == "notifyUser" and config.get('security_actions.notifications.enabled', True):
                    result = self.notify_user()
                else:
                    result = f"Action {action} disabled or unknown"
                    
                results.append(f"{action}: {result}")
                self.stats["actions_executed"] += 1
            except Exception as e:
                results.append(f"{action}: ERROR - {str(e)}")
                
        return results
    
    def enable_vpn(self):
        """Enable VPN connection - cross-platform"""
        try:
            if IS_LINUX:
                cmd = config.get('security_actions.vpn.linux_command', ['nmcli', 'connection', 'up', 'dps-vpn'])
                timeout = config.get('security_actions.vpn.timeout_seconds', 10)
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
                return "VPN enabled (Linux)" if result.returncode == 0 else f"VPN failed: {result.stderr}"
            elif IS_WINDOWS:
                cmd = config.get('security_actions.vpn.windows_command', 'echo VPN control not implemented for Windows')
                result = subprocess.run(['powershell', '-command', cmd], capture_output=True, text=True)
                return "VPN command executed (Windows)"
            elif IS_MACOS:
                return "VPN control not implemented for macOS"
            else:
                return "VPN control not available on this platform"
        except Exception as e:
            return f"VPN error: {str(e)}"
    
    def lock_clipboard(self):
        """Lock clipboard by clearing it - cross-platform"""
        try:
            if IS_LINUX:
                cmd = config.get('security_actions.clipboard.linux_command', ['xsel', '--clear'])
                subprocess.run(cmd, check=False, timeout=5)
                result = "Clipboard locked (Linux)"
            elif IS_WINDOWS:
                cmd = config.get('security_actions.clipboard.windows_powershell', 'Set-Clipboard -Value ""')
                subprocess.run(['powershell', '-command', cmd], check=False, capture_output=True, timeout=5)
                result = "Clipboard locked (Windows)"
            elif IS_MACOS:
                subprocess.run(['pbcopy'], input='', text=True, check=False, timeout=5)
                result = "Clipboard locked (macOS)"
            else:
                result = "Clipboard lock not available"
            
            # Start continuous monitoring if enabled and in Ultra mode
            if (config.get('clipboard_protection.continuous_clear_in_ultra', True) and 
                self.current_zone == "zone3"):
                self.clipboard_blocked = True
                self.start_clipboard_monitor()
                result += " + Continuous monitoring enabled"
            
            return result
        except Exception as e:
            return f"Clipboard lock error: {str(e)}"
    
    def unlock_clipboard(self):
        """Stop clipboard monitoring"""
        self.clipboard_blocked = False
        if self.clipboard_monitor_thread:
            self.clipboard_monitor_thread = None
        return "Clipboard monitoring stopped"
    
    def start_clipboard_monitor(self):
        """Start continuous clipboard monitoring thread"""
        if (self.clipboard_monitor_thread and self.clipboard_monitor_thread.is_alive() or
            not config.get('clipboard_protection.enabled', True)):
            return
            
        def monitor_clipboard():
            interval = config.get('clipboard_protection.clear_interval_seconds', 2)
            while self.clipboard_blocked and self.running:
                try:
                    if IS_WINDOWS:
                        cmd = config.get('security_actions.clipboard.windows_powershell', 'Set-Clipboard -Value ""')
                        subprocess.run(['powershell', '-command', cmd], check=False, capture_output=True, timeout=5)
                    elif IS_LINUX:
                        cmd = config.get('security_actions.clipboard.linux_command', ['xsel', '--clear'])
                        subprocess.run(cmd, check=False, timeout=5)
                    elif IS_MACOS:
                        subprocess.run(['pbcopy'], input='', text=True, check=False, timeout=5)
                    
                    time.sleep(interval)
                except Exception as e:
                    if config.get('system.debug_mode', False):
                        print(f"Clipboard monitor error: {e}")
                    time.sleep(5)
        
        self.clipboard_monitor_thread = threading.Thread(target=monitor_clipboard, daemon=True)
        self.clipboard_monitor_thread.start()
    
    def stop_clipboard_monitor(self):
        """Stop clipboard monitoring"""
        self.clipboard_blocked = False
        if self.clipboard_monitor_thread:
            self.clipboard_monitor_thread = None
    
    def remount_home_ro(self):
        """Remount home directory as read-only (Linux only)"""
        try:
            if IS_LINUX:
                cmd = config.get('security_actions.filesystem.linux_remount_ro', ['mount', '-o', 'remount,ro', '/home'])
                result = subprocess.run(cmd, capture_output=True, text=True)
                return "Home remounted RO" if result.returncode == 0 else "Remount failed"
            elif IS_WINDOWS:
                return config.get('security_actions.filesystem.windows_note', 'Filesystem remounting not applicable on Windows')
            elif IS_MACOS:
                return "Filesystem remounting not implemented for macOS"
            else:
                return "Filesystem remounting not available"
        except Exception as e:
            return f"Remount error: {str(e)}"
    
    def notify_user(self):
        """Send desktop notification - cross-platform"""
        try:
            if IS_LINUX:
                cmd = config.get('security_actions.notifications.linux_command', 
                               ['notify-send', 'DPS-OS', 'Security zone transition detected'])
                subprocess.run(cmd, check=False, timeout=5)
                return "User notified (Linux)"
            elif IS_WINDOWS:
                cmd = config.get('security_actions.notifications.windows_powershell',
                               "Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.MessageBox]::Show('Security zone transition detected', 'DPS-OS')")
                subprocess.run(['powershell', '-command', cmd], check=False, capture_output=True, timeout=10)
                return "User notified (Windows)"
            elif IS_MACOS:
                subprocess.run(['osascript', '-e', 'display notification "Security zone transition detected" with title "DPS-OS"'], 
                              check=False, timeout=5)
                return "User notified (macOS)"
            else:
                return "Notification sent (fallback)"
        except Exception as e:
            return f"Notification error: {str(e)}"
    
    def detect_bank_url(self, url):
        """Enhanced bank URL detection using configuration"""
        if not config.get('url_monitoring.enabled', True):
            return False
            
        url_lower = url.lower()
        
        # Check financial keywords from config
        keywords = config.get('url_monitoring.financial_keywords', self.bank_url_patterns)
        for pattern in keywords:
            if pattern in url_lower:
                return True
        
        # Check financial domains from config
        domains = config.get('url_monitoring.financial_domains', ['.bank', '.finance', '.pay'])
        for domain in domains:
            if domain in url_lower:
                return True
        
        # Check for HTTPS secure login pages
        if 'https://' in url_lower and ('login' in url_lower or 'signin' in url_lower or 'account' in url_lower):
            return True
            
        return False
    
    def transition_zone(self, new_zone, reason):
        """Transition to new security zone with Ultra mode lock protection"""
        old_zone = self.current_zone
        
        # Prevent leaving Ultra mode if USB devices are still connected
        if self.ultra_mode_locked and old_zone == "zone3" and new_zone != "zone3":
            if self.connected_usb_devices:
                self.add_event("zone_transition_blocked", {
                    "attempted_from": old_zone,
                    "attempted_to": new_zone,
                    "reason": "Ultra mode locked - USB devices still connected",
                    "connected_devices": list(self.connected_usb_devices)
                })
                return  # Block the transition
        
        self.current_zone = new_zone
        self.stats["zone_transitions"] += 1
        self.add_event("zone_transition", {
            "from": old_zone,
            "to": new_zone,
            "reason": reason
        })
        
        # Start clipboard monitoring if entering Ultra mode
        if new_zone == "zone3":
            self.clipboard_blocked = True
            self.start_clipboard_monitor()
        elif old_zone == "zone3" and new_zone != "zone3":
            # Stop clipboard monitoring when leaving Ultra mode
            self.stop_clipboard_monitor()

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
                    device_id = device.sys_name
                    self.dps_monitor.connected_usb_devices.add(device_id)
                    device_info = {
                        "sysName": device.sys_name,
                        "devNode": device.device_node,
                        "deviceClass": "mass_storage",
                        "platform": "linux",
                        "action": "plugged"
                    }
                    
                    self.dps_monitor.add_event("usb_plugged", device_info)
                    
                    # Force transition to Ultra mode and lock it
                    self.dps_monitor.transition_zone("zone3", f"USB device plugged: {device.sys_name}")
                    self.dps_monitor.ultra_mode_locked = True
                    
                    # Execute security actions
                    actions = self.dps_monitor.execute_actions(["lockClipboard", "remountHomeRo", "notifyUser"])
                    self.dps_monitor.add_event("security_lockdown", {"reason": "USB detected", "actions": actions})
                
                elif device.action == 'remove':
                    device_id = device.sys_name
                    if device_id in self.dps_monitor.connected_usb_devices:
                        self.dps_monitor.connected_usb_devices.remove(device_id)
                        device_info = {
                            "sysName": device.sys_name,
                            "deviceClass": "mass_storage",
                            "platform": "linux",
                            "action": "removed"
                        }
                        
                        self.dps_monitor.add_event("usb_removed", device_info)
                        
                        # Check if all USB devices are removed
                        if not self.dps_monitor.connected_usb_devices:
                            self.dps_monitor.ultra_mode_locked = False
                            self.dps_monitor.stop_clipboard_monitor()
                            self.dps_monitor.transition_zone("zone1", "All USB devices removed - returning to Normal")
                            self.dps_monitor.add_event("security_unlock", {"reason": "No USB devices connected"})
        
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
                    self.dps_monitor.connected_usb_devices.add(partition.device)
            
            while self.dps_monitor.running:
                try:
                    current_drives = set()
                    for partition in psutil.disk_partitions():
                        if 'removable' in partition.opts:
                            current_drives.add(partition.device)
                    
                    # Handle new USB devices (plugged in)
                    new_drives = current_drives - seen_drives
                    for drive in new_drives:
                        self.dps_monitor.connected_usb_devices.add(drive)
                        device_info = {
                            "device": drive,
                            "deviceClass": "mass_storage",
                            "platform": "windows",
                            "action": "plugged"
                        }
                        
                        self.dps_monitor.add_event("usb_plugged", device_info)
                        
                        # Force transition to Ultra mode and lock it
                        self.dps_monitor.transition_zone("zone3", f"USB device plugged: {drive}")
                        self.dps_monitor.ultra_mode_locked = True
                        
                        # Execute security actions
                        actions = self.dps_monitor.execute_actions(["lockClipboard", "notifyUser"])
                        self.dps_monitor.add_event("security_lockdown", {"reason": "USB detected", "actions": actions})
                    
                    # Handle removed USB devices (unplugged)
                    removed_drives = seen_drives - current_drives
                    for drive in removed_drives:
                        if drive in self.dps_monitor.connected_usb_devices:
                            self.dps_monitor.connected_usb_devices.remove(drive)
                            device_info = {
                                "device": drive,
                                "deviceClass": "mass_storage",
                                "platform": "windows",
                                "action": "removed"
                            }
                            
                            self.dps_monitor.add_event("usb_removed", device_info)
                            
                            # Check if all USB devices are removed
                            if not self.dps_monitor.connected_usb_devices:
                                self.dps_monitor.ultra_mode_locked = False
                                self.dps_monitor.stop_clipboard_monitor()
                                self.dps_monitor.transition_zone("zone1", "All USB devices removed - returning to Normal")
                                self.dps_monitor.add_event("security_unlock", {"reason": "No USB devices connected"})
                    
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

class URLMonitor:
    def __init__(self, dps_monitor):
        self.dps_monitor = dps_monitor
        self.monitored_processes = ['chrome.exe', 'firefox.exe', 'msedge.exe', 'iexplore.exe', 'chrome', 'firefox', 'chromium']
        
    def start_monitoring(self):
        """Monitor browser processes for bank-related URLs"""
        def monitor_urls():
            while self.dps_monitor.running:
                try:
                    # Monitor browser processes
                    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                        proc_name = proc.info['name'].lower()
                        
                        # Check if it's a browser process
                        if any(browser in proc_name for browser in self.monitored_processes):
                            cmdline = ' '.join(proc.info['cmdline'] or [])
                            
                            # Look for URLs in command line arguments
                            if 'http' in cmdline.lower():
                                urls = self.extract_urls_from_cmdline(cmdline)
                                for url in urls:
                                    if self.dps_monitor.detect_bank_url(url):
                                        self.dps_monitor.add_event("bank_url_detected", {
                                            "url": url,
                                            "browser": proc_name,
                                            "pid": proc.info['pid']
                                        })
                                        
                                        # Transition to Sensitive mode for bank URLs
                                        if not self.dps_monitor.ultra_mode_locked:
                                            self.dps_monitor.transition_zone("zone2", f"Bank URL detected: {url}")
                                            actions = self.dps_monitor.execute_actions(["enableVpn", "lockClipboard", "notifyUser"])
                                            self.dps_monitor.add_event("bank_security_activated", {"url": url, "actions": actions})
                    
                    time.sleep(5)  # Check every 5 seconds
                except Exception as e:
                    print(f"URL monitoring error: {e}")
                    time.sleep(10)
        
        thread = threading.Thread(target=monitor_urls, daemon=True)
        thread.start()
        return thread
    
    def extract_urls_from_cmdline(self, cmdline):
        """Extract URLs from command line arguments"""
        import re
        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
        urls = re.findall(url_pattern, cmdline, re.IGNORECASE)
        return urls

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
        "ultra_mode_locked": dps_monitor.ultra_mode_locked,
        "connected_usb_devices": list(dps_monitor.connected_usb_devices),
        "clipboard_blocked": dps_monitor.clipboard_blocked,
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

@app.route('/api/simulate_event', methods=['POST'])
def api_simulate_event():
    """Simulate an event for testing"""
    data = request.json
    event_type = data.get('type')
    event_data = data.get('data', {})
    
    if event_type == 'usb':
        # Simulate USB device connection
        dps_monitor.connected_usb_devices.add(event_data.get('device', 'test_usb'))
        dps_monitor.transition_zone("zone3", "Simulated USB event")
        dps_monitor.ultra_mode_locked = True
        actions = dps_monitor.execute_actions(["lockClipboard", "notifyUser"])
        dps_monitor.add_event("simulated_usb", event_data, actions)
    elif event_type == 'url':
        # Simulate bank URL detection
        url = event_data.get('url', '')
        if dps_monitor.detect_bank_url(url):
            if not dps_monitor.ultra_mode_locked:
                dps_monitor.transition_zone("zone2", f"Simulated bank URL: {url}")
            actions = dps_monitor.execute_actions(["enableVpn", "lockClipboard", "notifyUser"])
            dps_monitor.add_event("simulated_bank_url", event_data, actions)
    
    return jsonify({"status": "success"})

def main():
    """Main application entry point"""
    print("🛡️  DPS-OS Cross-Platform Monitor Starting...")
    print(f"🖥️  Platform: {platform.system()} {platform.release()}")
    print(f"🐍 Python: {platform.python_version()}")
    
    # Load configuration
    print(f"⚙️  Configuration: {len(config.config)} sections loaded")
    
    # Check if running with appropriate privileges
    if IS_LINUX:
        if os.geteuid() != 0:
            print("⚠️  Warning: Not running as root. Some features may not work.")
            print("   Run with: sudo python3 dps_app.py")
    elif IS_WINDOWS:
        try:
            import ctypes
            if not ctypes.windll.shell32.IsUserAnAdmin():
                print("⚠️  Warning: Not running as Administrator. Some features may not work.")
                print("   Run Command Prompt as Administrator and try again.")
        except:
            print("⚠️  Could not check Administrator status")
    elif IS_MACOS:
        print("🍎 macOS detected - some features may require additional permissions")
    
    # Initialize monitors based on configuration
    monitors = []
    
    if config.get('usb_monitoring.enabled', True):
        print("🔍 Starting USB monitoring...")
        usb_monitor = USBMonitor(dps_monitor)
        monitors.append(('USB', usb_monitor))
    
    if config.get('process_monitoring.enabled', True):
        print("🔍 Starting process monitoring...")
        process_monitor = ProcessMonitor(dps_monitor)
        monitors.append(('Process', process_monitor))
    
    if config.get('network_monitoring.enabled', True):
        print("🔍 Starting network monitoring...")
        network_monitor = NetworkMonitor(dps_monitor)
        monitors.append(('Network', network_monitor))
    
    if config.get('url_monitoring.enabled', True):
        print("� StarSting URL monitoring...")
        url_monitor = URLMonitor(dps_monitor)
        monitors.append(('URL', url_monitor))
    
    # Start all enabled monitors
    for name, monitor in monitors:
        try:
            monitor.start_monitoring()
            print(f"✅ {name} monitor started")
        except Exception as e:
            print(f"❌ {name} monitor failed to start: {e}")
    
    # Handle shutdown gracefully
    def signal_handler(sig, frame):
        print("\n🛑 Shutting down DPS-OS Monitor...")
        dps_monitor.running = False
        dps_monitor.stop_clipboard_monitor()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    if hasattr(signal, 'SIGTERM'):  # Not available on Windows
        signal.signal(signal.SIGTERM, signal_handler)
    
    # Start web server with fallback ports
    if config.get('dashboard.enabled', True):
        ports_to_try = [
            config.get('system.web_port', 5000),
            5001, 8081, 8082, 3000
        ]
        server_started = False
        
        for port in ports_to_try:
            try:
                print(f"🌐 Trying to start web dashboard on http://localhost:{port}")
                print("📊 Open your browser to view the monitoring dashboard")
                print("🔧 Use Ctrl+C to stop")
                app.run(host='127.0.0.1', port=port, debug=config.get('system.debug_mode', False), threaded=True)
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
    else:
        print("📊 Dashboard disabled in configuration")
        print("🔧 Monitoring will continue in background. Use Ctrl+C to stop")
        try:
            while dps_monitor.running:
                time.sleep(1)
        except KeyboardInterrupt:
            signal_handler(signal.SIGINT, None)

if __name__ == '__main__':
    main()