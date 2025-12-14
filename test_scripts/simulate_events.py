#!/usr/bin/env python3
"""
DPS-OS Event Simulator
Simulates various events for testing the daemon
"""

import socket
import json
import time
import argparse
import sys

SOCK_PATH = '/var/run/dpsos.sock'

def send_event(event_data):
    """Send event to daemon via Unix socket"""
    try:
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.connect(SOCK_PATH)
        sock.sendall(json.dumps(event_data).encode())
        sock.close()
        print(f"✓ Sent: {event_data}")
        return True
    except Exception as e:
        print(f"✗ Failed to send event: {e}")
        return False

def simulate_usb_events():
    """Simulate various USB device events"""
    print("=== Simulating USB Events ===")
    
    usb_events = [
        {
            "trigger": "usbPlugged",
            "device": {
                "sysName": "sdb1",
                "devNode": "/dev/sdb1",
                "deviceClass": "mass_storage"
            }
        },
        {
            "trigger": "usbPlugged", 
            "device": {
                "sysName": "input2",
                "devNode": "/dev/input/event2",
                "deviceClass": "input"
            }
        },
        {
            "trigger": "usbPlugged",
            "device": {
                "sysName": "ttyUSB0",
                "devNode": "/dev/ttyUSB0", 
                "deviceClass": "serial"
            }
        }
    ]
    
    for event in usb_events:
        send_event(event)
        time.sleep(1)

def simulate_url_events():
    """Simulate browser URL events"""
    print("\n=== Simulating URL Events ===")
    
    url_events = [
        {
            "trigger": "openSensitiveUrl",
            "url": "https://test.bank.com/login"
        },
        {
            "trigger": "openSensitiveUrl", 
            "url": "https://payments.example.com/checkout"
        },
        {
            "trigger": "openSensitiveUrl",
            "url": "https://secure.banking.org/account"
        },
        {
            "trigger": "openSensitiveUrl",
            "url": "https://normal-site.com"  # Should not match patterns
        }
    ]
    
    for event in url_events:
        send_event(event)
        time.sleep(1)

def simulate_stress_test(count=50):
    """Send multiple events rapidly for stress testing"""
    print(f"\n=== Stress Test ({count} events) ===")
    
    start_time = time.time()
    success_count = 0
    
    for i in range(count):
        event = {
            "trigger": "usbPlugged",
            "device": {
                "sysName": f"test_device_{i}",
                "devNode": f"/dev/test{i}"
            }
        }
        if send_event(event):
            success_count += 1
        
        if i % 10 == 0:
            print(f"Progress: {i}/{count}")
    
    end_time = time.time()
    duration = end_time - start_time
    
    print(f"\nStress test completed:")
    print(f"- Events sent: {success_count}/{count}")
    print(f"- Duration: {duration:.2f} seconds")
    print(f"- Rate: {success_count/duration:.2f} events/second")

def simulate_malformed_events():
    """Test error handling with malformed events"""
    print("\n=== Testing Error Handling ===")
    
    # These should be handled gracefully by the daemon
    malformed_events = [
        '{"invalid": "missing_trigger"}',
        '{"trigger": "unknown_trigger"}',
        '{"trigger": "usbPlugged"}',  # Missing device info
        'invalid json syntax',
        '{"trigger": "' + 'x' * 10000 + '"}',  # Very long string
    ]
    
    for event_str in malformed_events:
        try:
            sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            sock.connect(SOCK_PATH)
            sock.sendall(event_str.encode())
            sock.close()
            print(f"✓ Sent malformed event (daemon should handle gracefully)")
        except Exception as e:
            print(f"✗ Failed to send malformed event: {e}")
        time.sleep(0.5)

def interactive_mode():
    """Interactive mode for manual event testing"""
    print("\n=== Interactive Mode ===")
    print("Enter JSON events (or 'quit' to exit):")
    
    while True:
        try:
            user_input = input("> ")
            if user_input.lower() in ['quit', 'exit', 'q']:
                break
            
            event_data = json.loads(user_input)
            send_event(event_data)
            
        except json.JSONDecodeError:
            print("Invalid JSON format")
        except KeyboardInterrupt:
            print("\nExiting...")
            break

def main():
    parser = argparse.ArgumentParser(description='DPS-OS Event Simulator')
    parser.add_argument('--usb', action='store_true', help='Simulate USB events')
    parser.add_argument('--url', action='store_true', help='Simulate URL events') 
    parser.add_argument('--stress', type=int, metavar='N', help='Stress test with N events')
    parser.add_argument('--malformed', action='store_true', help='Test malformed events')
    parser.add_argument('--interactive', action='store_true', help='Interactive mode')
    parser.add_argument('--all', action='store_true', help='Run all tests')
    
    args = parser.parse_args()
    
    # Check if daemon socket exists
    try:
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.connect(SOCK_PATH)
        sock.close()
        print("✓ Daemon socket is accessible")
    except Exception as e:
        print(f"✗ Cannot connect to daemon: {e}")
        print("Make sure the daemon is running: python daemon/daemon.py")
        sys.exit(1)
    
    if args.all:
        simulate_usb_events()
        simulate_url_events()
        simulate_stress_test(25)
        simulate_malformed_events()
    else:
        if args.usb:
            simulate_usb_events()
        if args.url:
            simulate_url_events()
        if args.stress:
            simulate_stress_test(args.stress)
        if args.malformed:
            simulate_malformed_events()
        if args.interactive:
            interactive_mode()
        
        if not any([args.usb, args.url, args.stress, args.malformed, args.interactive]):
            print("No test specified. Use --help for options or --all for all tests")

if __name__ == '__main__':
    main()