#!/bin/bash
# DPS-OS Dependency Installation Script
# Installs all required system packages and Python libraries

set -e

echo "🛡️  DPS-OS Dependency Installer"
echo "================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
check_root() {
    if [ "$EUID" -ne 0 ]; then
        print_error "This script requires root privileges."
        print_status "Please run with: sudo $0"
        exit 1
    fi
    print_success "Running with root privileges"
}

# Detect Linux distribution
detect_distro() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        DISTRO=$ID
        VERSION=$VERSION_ID
    else
        print_error "Cannot detect Linux distribution"
        exit 1
    fi
    print_status "Detected distribution: $DISTRO $VERSION"
}

# Update package manager
update_packages() {
    print_status "Updating package manager..."
    
    case $DISTRO in
        "kali"|"debian"|"ubuntu")
            apt update
            print_success "Package manager updated (apt)"
            ;;
        "fedora"|"rhel"|"centos")
            dnf update -y || yum update -y
            print_success "Package manager updated (dnf/yum)"
            ;;
        "arch"|"manjaro")
            pacman -Sy
            print_success "Package manager updated (pacman)"
            ;;
        *)
            print_warning "Unknown distribution, attempting apt..."
            apt update || {
                print_error "Failed to update packages"
                exit 1
            }
            ;;
    esac
}

# Install system packages
install_system_packages() {
    print_status "Installing system packages..."
    
    case $DISTRO in
        "kali"|"debian"|"ubuntu")
            apt install -y \
                python3 \
                python3-pip \
                python3-dev \
                python3-venv \
                build-essential \
                pkg-config \
                libudev-dev \
                libffi-dev \
                libssl-dev \
                curl \
                wget \
                git \
                network-manager \
                wmctrl \
                xsel \
                libnotify-bin \
                netcat-openbsd
            print_success "System packages installed (Debian/Ubuntu/Kali)"
            ;;
        "fedora"|"rhel"|"centos")
            dnf install -y \
                python3 \
                python3-pip \
                python3-devel \
                gcc \
                gcc-c++ \
                make \
                pkgconfig \
                systemd-devel \
                libudev-devel \
                libffi-devel \
                openssl-devel \
                curl \
                wget \
                git \
                NetworkManager \
                wmctrl \
                xsel \
                libnotify \
                netcat || \
            yum install -y \
                python3 \
                python3-pip \
                python3-devel \
                gcc \
                gcc-c++ \
                make \
                pkgconfig \
                systemd-devel \
                libudev-devel \
                libffi-devel \
                openssl-devel \
                curl \
                wget \
                git \
                NetworkManager \
                wmctrl \
                xsel \
                libnotify \
                netcat
            print_success "System packages installed (Fedora/RHEL/CentOS)"
            ;;
        "arch"|"manjaro")
            pacman -S --noconfirm \
                python \
                python-pip \
                base-devel \
                pkgconf \
                systemd \
                libffi \
                openssl \
                curl \
                wget \
                git \
                networkmanager \
                wmctrl \
                xsel \
                libnotify \
                gnu-netcat
            print_success "System packages installed (Arch/Manjaro)"
            ;;
        *)
            print_warning "Unknown distribution, attempting Debian packages..."
            apt install -y python3 python3-pip python3-dev build-essential libudev-dev || {
                print_error "Failed to install system packages"
                exit 1
            }
            ;;
    esac
}

# Install Python packages
install_python_packages() {
    print_status "Installing Python packages..."
    
    # Upgrade pip first
    python3 -m pip install --upgrade pip
    print_success "pip upgraded"
    
    # Install required packages
    python3 -m pip install \
        flask>=2.3.0 \
        pyudev>=0.24.0 \
        psutil>=5.9.0 \
        watchdog>=3.0.0 \
        jsonschema>=4.17.0
    
    print_success "Python packages installed"
}

# Verify installations
verify_installation() {
    print_status "Verifying installation..."
    
    # Check Python
    if python3 --version >/dev/null 2>&1; then
        PYTHON_VERSION=$(python3 --version)
        print_success "Python: $PYTHON_VERSION"
    else
        print_error "Python3 not found"
        return 1
    fi
    
    # Check pip
    if python3 -m pip --version >/dev/null 2>&1; then
        PIP_VERSION=$(python3 -m pip --version)
        print_success "pip: $PIP_VERSION"
    else
        print_error "pip not found"
        return 1
    fi
    
    # Check Python packages
    local packages=("flask" "pyudev" "psutil" "watchdog" "jsonschema")
    for package in "${packages[@]}"; do
        if python3 -c "import $package" >/dev/null 2>&1; then
            print_success "Python package: $package ✓"
        else
            print_error "Python package missing: $package"
            return 1
        fi
    done
    
    # Check system tools
    local tools=("wmctrl" "xsel" "nmcli" "nc")
    for tool in "${tools[@]}"; do
        if command -v $tool >/dev/null 2>&1; then
            print_success "System tool: $tool ✓"
        else
            print_warning "System tool missing: $tool (some features may not work)"
        fi
    done
}

# Create necessary directories
create_directories() {
    print_status "Creating necessary directories..."
    
    # Create application directories
    mkdir -p /var/run/dpsos
    chmod 755 /var/run/dpsos
    
    # Create log directory
    mkdir -p /var/log/dpsos
    chmod 755 /var/log/dpsos
    
    # Create templates directory for Flask
    mkdir -p templates
    
    print_success "Directories created"
}

# Set up NetworkManager VPN (optional)
setup_test_vpn() {
    print_status "Setting up test VPN connection..."
    
    if command -v nmcli >/dev/null 2>&1; then
        # Create a dummy VPN connection for testing
        nmcli connection add type vpn con-name dps-vpn ifname -- vpn-type openvpn >/dev/null 2>&1 || true
        print_success "Test VPN connection created (dps-vpn)"
    else
        print_warning "NetworkManager not available, VPN features will not work"
    fi
}

# Main installation function
main() {
    echo
    print_status "Starting DPS-OS dependency installation..."
    echo
    
    check_root
    detect_distro
    update_packages
    install_system_packages
    install_python_packages
    create_directories
    setup_test_vpn
    
    echo
    print_status "Verifying installation..."
    if verify_installation; then
        echo
        print_success "🎉 All dependencies installed successfully!"
        echo
        print_status "Next steps:"
        echo "  1. Run the application: sudo python3 dps_app.py"
        echo "  2. Or use the launcher: sudo ./run_dps.sh"
        echo "  3. Open browser to: http://localhost:8080"
        echo
        print_status "Installation complete!"
    else
        echo
        print_error "❌ Installation verification failed"
        print_status "Some dependencies may be missing. Check the errors above."
        exit 1
    fi
}

# Run main function
main "$@"