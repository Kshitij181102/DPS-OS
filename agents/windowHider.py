#!/usr/bin/env python3
import subprocess, sys

def hide_windows_by_title(title_pattern):
    """Hide windows matching title pattern using wmctrl"""
    try:
        # Get window list and filter by title
        result = subprocess.run(['wmctrl', '-l'], capture_output=True, text=True)
        if result.returncode != 0:
            print('wmctrl not available or failed')
            return
        
        for line in result.stdout.split('\n'):
            if title_pattern.lower() in line.lower():
                window_id = line.split()[0]
                subprocess.run(['wmctrl', '-i', '-r', window_id, '-b', 'add,hidden'])
                print(f'Hidden window: {line.strip()}')
    except Exception as e:
        print(f'Error hiding windows: {e}')

if __name__=='__main__':
    if len(sys.argv) > 1:
        hide_windows_by_title(sys.argv[1])
    else:
        # Default: hide password managers
        hide_windows_by_title('Password Manager')