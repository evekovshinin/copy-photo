#!/bin/bash

# Install script for copy-photo application
# This script installs the copy-photo utility on Linux systems

set -e  # Exit on any error

echo "Installing copy-photo application..."

# Check if running on Linux
if [[ "$OSTYPE" != "linux-gnu"* ]]; then
    echo "Error: This script is designed for Linux systems only."
    exit 1
fi

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required but not installed."
    echo "Please install Python 3 first."
    exit 1
fi

# Check Python version (require 3.6+)
PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
if [[ $(echo "$PYTHON_VERSION < 3.6" | bc -l) -eq 1 ]]; then
    echo "Error: Python 3.6 or higher is required. Current version: $PYTHON_VERSION"
    exit 1
fi

echo "Python version: $PYTHON_VERSION ✓"

# Install system dependencies
echo "Installing system dependencies..."
if command -v apt-get &> /dev/null; then
    # Debian/Ubuntu
    sudo apt-get update
    sudo apt-get install -y exiftool
elif command -v yum &> /dev/null; then
    # CentOS/RHEL
    sudo yum install -y perl-Image-ExifTool
elif command -v dnf &> /dev/null; then
    # Fedora
    sudo dnf install -y perl-Image-ExifTool
elif command -v pacman &> /dev/null; then
    # Arch Linux
    sudo pacman -S --noconfirm perl-image-exiftool
else
    echo "Warning: Could not determine package manager. Please install exiftool manually."
    echo "On ALTLinux: sudo apt-get install exiftool"
    echo "On CentOS/RHEL: sudo yum install perl-Image-ExifTool"
    echo "On Fedora: sudo dnf install perl-Image-ExifTool"
    echo "On Arch: sudo pacman -S perl-image-exiftool"
fi

# Verify exiftool installation
if ! command -v exiftool &> /dev/null; then
    echo "Error: exiftool installation failed. Please install it manually."
    exit 1
fi

echo "exiftool installed ✓"

# Install Python dependencies
echo "Installing Python dependencies..."
pip3 install --user -r requirements.txt

# Install the application
echo "Installing copy-photo application..."
pip3 install --user -e .

# Verify installation
if ! command -v copy-photo &> /dev/null; then
    echo "Warning: copy-photo command not found in PATH."
    echo "You may need to add ~/.local/bin to your PATH:"
    echo "  export PATH=\$HOME/.local/bin:\$PATH"
    echo "  echo 'export PATH=\$HOME/.local/bin:\$PATH' >> ~/.bashrc"
else
    echo "copy-photo installed ✓"
fi

echo ""
echo "Installation completed successfully!"
echo ""
echo "Usage:"
echo "  copy-photo --help"
echo ""
echo "For more information, see the README.md file."