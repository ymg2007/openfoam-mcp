#!/bin/bash
# OpenFOAM MCP Server Installation Script for Linux and macOS
# This script creates a virtual environment and installs dependencies

set -e

echo "========================================"
echo "OpenFOAM MCP Server Installation"
echo "========================================"
echo ""

# Check if Python 3.10+ is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.10 or higher"
    echo "  Ubuntu/Debian: sudo apt install python3 python3-pip"
    echo "  Fedora/RHEL: sudo dnf install python3 python3-pip"
    echo "  macOS: brew install python@3.11"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | awk '{print $2}')
echo "Python found: $PYTHON_VERSION"
echo ""

# Parse version to check if >= 3.10
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 10 ]); then
    echo "ERROR: Python 3.10 or higher is required (found $PYTHON_VERSION)"
    exit 1
fi

# Create virtual environment
if [ -d "venv" ]; then
    echo "Virtual environment already exists. Removing..."
    rm -rf venv
fi

echo "Creating virtual environment..."
python3 -m venv venv

if [ $? -ne 0 ]; then
    echo "ERROR: Failed to create virtual environment"
    echo "Make sure you have python3-venv installed:"
    echo "  Ubuntu/Debian: sudo apt install python3-venv"
    exit 1
fi

echo "Virtual environment created successfully."
echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

if [ $? -ne 0 ]; then
    echo "ERROR: Failed to activate virtual environment"
    exit 1
fi

echo ""
echo "Installing dependencies..."
echo ""

pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install dependencies"
    exit 1
fi

echo ""
echo "========================================"
echo "Installation completed successfully!"
echo "========================================"
echo ""
echo "To use the MCP server:"
echo ""
echo "1. Activate the virtual environment:"
echo "   source venv/bin/activate"
echo "   # or on Linux with fish shell:"
echo "   source venv/bin/activate.fish"
echo ""
echo "2. Configure your AI assistant (Claude Desktop, Claude Code, OpenCode, etc.)"
echo "   Add this server to your MCP config:"
echo ""
echo "   {"
echo "     \"mcpServers\": {"
echo "       \"openfoam\": {"
echo "         \"command\": \"$(pwd)/venv/bin/python\","
echo "         \"args\": [\"$(pwd)/src/server.py\"]"
echo "       }"
echo "     }"
echo "   }"
echo ""
echo "   # Replace $(pwd) with the actual path if needed"
echo ""
echo "To deactivate the virtual environment later:"
echo "   deactivate"
