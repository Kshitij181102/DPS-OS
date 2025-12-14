#!/usr/bin/env python3
"""
DPS-OS Setup Script
Cross-platform setup for development environment
"""

import os
import sys
import subprocess
import platform

def run_command(cmd, shell=True):
    """Run command and return success status"""
    try:
        result = subprocess.run(cmd, shell=shell, check=True, capture_output=True, text=True)
        print(f"✓ {' '.join(cmd) if isinstance(cmd, list) else cmd}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed: {' '.join(cmd) if isinstance(cmd, list) else cmd}")
        print(f"  Error: {e.stderr}")
        return False

def setup_python_env():
    """Set up Python virtual environment and dependencies"""
    print("Setting up Python environment...")
    
    # Create virtual environment
    if not os.path.exists('.venv'):
        run_command([sys.executable, '-m', 'venv', '.venv'])
    
    # Determine activation script path
    if platform.system() == 'Windows':
        activate_script = '.venv\\Scripts\\activate'
        pip_path = '.venv\\Scripts\\pip'
    else:
        activate_script = '.venv/bin/activate'
        pip_path = '.venv/bin/pip'
    
    # Install dependencies
    run_command([pip_path, 'install', '-r', 'requirements.txt'])
    
    print(f"\nTo activate the virtual environment:")
    if platform.system() == 'Windows':
        print("  .venv\\Scripts\\activate")
    else:
        print("  source .venv/bin/activate")

def create_directories():
    """Create necessary directories"""
    print("Creating directories...")
    
    directories = [
        'logs',
        'data',
        'ui/webapp/src/components',
        'tests/unit',
        'tests/integration'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✓ Created {directory}")

def setup_git_hooks():
    """Set up git hooks for development"""
    if os.path.exists('.git'):
        print("Setting up git hooks...")
        # Could add pre-commit hooks here
        pass

def main():
    """Main setup function"""
    print("DPS-OS Development Environment Setup")
    print("=" * 40)
    
    create_directories()
    setup_python_env()
    setup_git_hooks()
    
    print("\n" + "=" * 40)
    print("Setup complete!")
    print("\nNext steps:")
    print("1. Activate virtual environment")
    print("2. Run: python daemon/daemon.py --db data/config.sqlite")
    print("3. In another terminal: python watchers/udevWatcher.py")
    print("\nFor UI development:")
    print("1. cd ui/webapp")
    print("2. npm install")
    print("3. npm start")

if __name__ == '__main__':
    main()