#!/usr/bin/env python3
"""
DPS-OS Cross-Platform Installer
Automatically detects the operating system and installs appropriate dependencies.
"""

import os
import sys
import platform
import subprocess
import json

def detect_platform():
    """Detect the current platform"""
    system = platform.system()
    if system == 'Windows':
        return 'windows'
    elif system == 'Linux':
        return 'linux'
    elif system == 'Darwin':
        return 'macos'
    else:
        return 'unknown'

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 7):
        print("❌ Python 3.7 or higher is required")
        print(f"   Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} detected")
    return True

def install_windows():
    """Install dependencies on Windows"""
    print("🪟 Installing Windows dependencies...")
    
    # Core Python packages
    packages = ['flask>=2.3.0', 'psutil>=5.9.0']
    
    # Optional Windows-specific packages
    try:
        subprocess.run(['pip', 'install', 'wmi>=1.5.1'], check=True)
        packages.append('wmi>=1.5.1')
        print("✅ WMI support installed")
    except subprocess.CalledProcessError:
        print("⚠️  WMI support failed to install (optional)")
    
    # Install core packages
    for package in packages[:2]:  # flask and psutil
        try:
            subprocess.run(['pip', 'install', package], check=True)
            print(f"✅ {package} installed")
        except subprocess.CalledProcessError:
            print(f"❌ Failed to install {package}")
            return False
    
    print("✅ Windows installation complete!")
    return True

def install_linux():
    """Install dependencies on Linux"""
    print("🐧 Installing Linux dependencies...")
    
    # Detect Linux distribution
    try:
        with open('/etc/os-release', 'r') as f:
            os_info = f.read().lower()
    except FileNotFoundError:
        os_info = ""
    
    # Install system packages
    if 'ubuntu' in os_info or 'debian' in os_info or 'kali' in os_info:
        print("📦 Installing system packages (Debian/Ubuntu/Kali)...")
        try:
            subprocess.run(['sudo', 'apt', 'update'], check=True)
            subprocess.run(['sudo', 'apt', 'install', '-y', 
                          'python3-pip', 'python3-dev', 'libudev-dev', 
                          'build-essential', 'libnotify-bin'], check=True)
            print("✅ System packages installed")
        except subprocess.CalledProcessError:
            print("⚠️  Some system packages failed to install")
    
    # Install Python packages
    packages = ['flask>=2.3.0', 'psutil>=5.9.0']
    
    # Try to install pyudev for better USB monitoring
    try:
        subprocess.run(['pip3', 'install', 'pyudev>=0.24.0'], check=True)
        packages.append('pyudev>=0.24.0')
        print("✅ pyudev installed for enhanced USB monitoring")
    except subprocess.CalledProcessError:
        print("⚠️  pyudev failed to install (USB monitoring will be limited)")
    
    # Install core packages
    for package in packages[:2]:  # flask and psutil
        try:
            subprocess.run(['pip3', 'install', package], check=True)
            print(f"✅ {package} installed")
        except subprocess.CalledProcessError:
            print(f"❌ Failed to install {package}")
            return False
    
    print("✅ Linux installation complete!")
    return True

def install_macos():
    """Install dependencies on macOS"""
    print("🍎 Installing macOS dependencies...")
    
    # Install Python packages
    packages = ['flask>=2.3.0', 'psutil>=5.9.0']
    
    for package in packages:
        try:
            subprocess.run(['pip3', 'install', package], check=True)
            print(f"✅ {package} installed")
        except subprocess.CalledProcessError:
            print(f"❌ Failed to install {package}")
            return False
    
    print("✅ macOS installation complete!")
    return True

def create_config_if_missing():
    """Create default config file if it doesn't exist"""
    if not os.path.exists('config.json'):
        print("📝 Creating default configuration file...")
        # The config.json file should already exist from our previous creation
        print("✅ Configuration file ready")
    else:
        print("✅ Configuration file already exists")

def main():
    """Main installer function"""
    print("🛡️  DPS-OS Cross-Platform Installer")
    print("=" * 40)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Detect platform
    platform_name = detect_platform()
    print(f"🖥️  Platform detected: {platform_name}")
    
    # Install based on platform
    success = False
    if platform_name == 'windows':
        success = install_windows()
    elif platform_name == 'linux':
        success = install_linux()
    elif platform_name == 'macos':
        success = install_macos()
    else:
        print(f"❌ Unsupported platform: {platform_name}")
        sys.exit(1)
    
    if not success:
        print("❌ Installation failed!")
        sys.exit(1)
    
    # Create config file
    create_config_if_missing()
    
    print("\n🎉 Installation completed successfully!")
    print("\n📋 Next steps:")
    print("   1. Review and customize config.json if needed")
    print("   2. Run: python dps_app.py")
    print("   3. Open browser to: http://localhost:5000")
    print("\n💡 Tips:")
    print("   - Run as Administrator/root for full functionality")
    print("   - Check config.json to customize behavior")
    print("   - Use Ctrl+C to stop the application")

if __name__ == '__main__':
    main()