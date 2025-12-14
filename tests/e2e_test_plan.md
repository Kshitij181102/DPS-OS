# DPS-OS End-to-End Testing Plan

## Test Environment Setup
- **VM Setup**: Use disposable Ubuntu VM with snapshot capability
- **Dependencies**: Install all required packages (python3, pyudev, etc.)
- **Permissions**: Ensure proper socket permissions and sudo access

## Test Cases

### 1. Basic Daemon Functionality
**Objective**: Verify daemon starts and accepts connections
- Start daemon: `python daemon/daemon.py --db test.sqlite`
- Check socket creation: `/var/run/dpsos.sock` exists with correct permissions
- Send test event via socket
- Verify daemon logs event reception

### 2. USB Device Detection
**Objective**: Test udev watcher and USB event flow
- Start daemon and udev watcher
- Plug USB device (or simulate udev event)
- Verify event reaches daemon
- Check rule evaluation and action dispatch

### 3. Browser URL Monitoring
**Objective**: Test browser extension integration
- Install browser extension (load unpacked)
- Register native messaging host
- Navigate to test banking URL
- Verify URL event forwarded to daemon
- Check VPN and clipboard actions triggered

### 4. Rule Engine Logic
**Objective**: Verify rule matching and priority handling
- Test multiple matching rules (priority selection)
- Test cooldown periods
- Test condition matching (URL patterns, device classes)
- Test wildcard zone matching

### 5. Action Execution
**Objective**: Verify all action types work correctly
- **VPN Toggle**: Test nmcli VPN connection
- **Clipboard Lock**: Verify clipboard clearing process
- **Filesystem Remount**: Test read-only remount (with rollback)
- **Window Hiding**: Test wmctrl window management

### 6. Error Handling
**Objective**: Test system resilience
- Invalid JSON events
- Missing rule files
- Failed action execution
- Socket permission issues
- Daemon restart scenarios

### 7. Security Tests
**Objective**: Verify security boundaries
- Unprivileged user socket access attempts
- Malformed native messaging input
- Large event payloads
- Concurrent connection handling

## Test Execution

### Automated Tests
```bash
# Basic functionality
python -m pytest tests/test_daemon.py
python -m pytest tests/test_rule_engine.py

# Integration tests
./tests/run_integration_tests.sh
```

### Manual Tests
1. **VM Snapshot**: Create clean VM state
2. **Install DPS-OS**: Run installation script
3. **Execute Test Cases**: Follow each test case procedure
4. **Document Results**: Record pass/fail and any issues
5. **Rollback**: Restore VM snapshot between tests

## Success Criteria
- All basic functionality tests pass
- USB and URL events properly trigger actions
- No security vulnerabilities in socket handling
- Graceful error handling for all failure modes
- System remains stable under normal and stress conditions

## Test Data
- Sample banking URLs: `https://test.bank.com`, `https://payments.example.com`
- Test USB devices: Various storage devices and input devices
- Malformed events: Invalid JSON, missing fields, oversized payloads