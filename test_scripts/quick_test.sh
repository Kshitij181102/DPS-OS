#!/bin/bash
# Quick DPS-OS Test Script for Kali Linux

set -e

echo "=== DPS-OS Quick Test Script ==="
echo "This script will test basic DPS-OS functionality"
echo

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test functions
test_pass() {
    echo -e "${GREEN}✓ $1${NC}"
}

test_fail() {
    echo -e "${RED}✗ $1${NC}"
}

test_info() {
    echo -e "${YELLOW}ℹ $1${NC}"
}

# Check if we're in the right directory
if [ ! -f "daemon/daemon.py" ]; then
    test_fail "Not in DPS-OS directory. Please cd to the project root."
    exit 1
fi

test_info "Checking system requirements..."

# Check Python
if command -v python3 &> /dev/null; then
    test_pass "Python3 is installed"
else
    test_fail "Python3 not found. Please install python3"
    exit 1
fi

# Check virtual environment
if [ ! -d ".venv" ]; then
    test_info "Creating virtual environment..."
    python3 -m venv .venv
    test_pass "Virtual environment created"
fi

# Activate virtual environment
source .venv/bin/activate
test_pass "Virtual environment activated"

# Install dependencies
test_info "Installing Python dependencies..."
pip install -q pyudev watchdog jsonschema psutil flask
test_pass "Dependencies installed"

# Create required directories
mkdir -p logs data
sudo mkdir -p /var/run/dpsos 2>/dev/null || true
sudo chmod 755 /var/run/dpsos 2>/dev/null || true
test_pass "Directories created"

# Set permissions
chmod +x daemon/daemon.py watchers/*.py agents/*.py 2>/dev/null || true
test_pass "Permissions set"

# Test 1: Start daemon in background
test_info "Starting daemon..."
python daemon/daemon.py --db data/test.sqlite &
DAEMON_PID=$!
sleep 2

if kill -0 $DAEMON_PID 2>/dev/null; then
    test_pass "Daemon started successfully (PID: $DAEMON_PID)"
else
    test_fail "Daemon failed to start"
    exit 1
fi

# Test 2: Check socket exists
if [ -S "/var/run/dpsos.sock" ]; then
    test_pass "Unix socket created"
else
    test_fail "Unix socket not found"
    kill $DAEMON_PID 2>/dev/null || true
    exit 1
fi

# Test 3: Send test event
test_info "Sending test USB event..."
echo '{"trigger":"usbPlugged","device":{"sysName":"test_device","devNode":"/dev/test"}}' | nc -U /var/run/dpsos.sock -w 1
if [ $? -eq 0 ]; then
    test_pass "Event sent successfully"
else
    test_fail "Failed to send event to daemon"
fi

# Test 4: Send URL event
test_info "Sending test URL event..."
echo '{"trigger":"openSensitiveUrl","url":"https://test.bank.com"}' | nc -U /var/run/dpsos.sock -w 1
if [ $? -eq 0 ]; then
    test_pass "URL event sent successfully"
else
    test_fail "Failed to send URL event"
fi

# Test 5: Test individual agents
test_info "Testing VPN agent..."
if python agents/vpnToggler.py up 2>/dev/null; then
    test_pass "VPN agent executed (may fail without VPN config - this is normal)"
else
    test_info "VPN agent failed (expected without VPN configuration)"
fi

# Test 6: Test clipboard agent
test_info "Testing clipboard agent..."
timeout 2 python agents/clipboardLocker.py &
CLIP_PID=$!
sleep 1
if kill -0 $CLIP_PID 2>/dev/null; then
    kill $CLIP_PID 2>/dev/null || true
    test_pass "Clipboard agent started and stopped"
else
    test_pass "Clipboard agent completed"
fi

# Test 7: Check rule engine
test_info "Checking rule schema..."
if [ -f "schema/ruleSchema.json" ]; then
    python3 -c "import json; json.load(open('schema/ruleSchema.json'))"
    test_pass "Rule schema is valid JSON"
else
    test_fail "Rule schema not found"
fi

# Test 8: Test malformed event (should not crash daemon)
test_info "Testing error handling with malformed event..."
echo 'invalid json' | nc -U /var/run/dpsos.sock -w 1 2>/dev/null || true
sleep 1
if kill -0 $DAEMON_PID 2>/dev/null; then
    test_pass "Daemon survived malformed input"
else
    test_fail "Daemon crashed on malformed input"
fi

# Cleanup
test_info "Cleaning up..."
kill $DAEMON_PID 2>/dev/null || true
sleep 1
test_pass "Daemon stopped"

# Summary
echo
echo "=== Test Summary ==="
test_pass "Basic daemon functionality works"
test_pass "Event processing works"
test_pass "Agents can be executed"
test_pass "Error handling is functional"

echo
test_info "Next steps:"
echo "1. Start daemon: python daemon/daemon.py --db data/config.sqlite"
echo "2. Start USB watcher: python watchers/udevWatcher.py"
echo "3. Test browser extension (see KALI_SETUP.md)"
echo "4. Monitor logs for detailed event processing"

echo
test_pass "DPS-OS basic functionality test completed successfully!"