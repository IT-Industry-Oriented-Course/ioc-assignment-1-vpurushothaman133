#!/bin/bash

# Setup script for Linux/Mac

set -e  # Exit on error

echo "================================================"
echo "Clinical Workflow Agent - Setup"
echo "================================================"
echo ""

# Check Python installation
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.8 or higher"
    exit 1
fi

echo "[1/4] Python found"
python3 --version

# Create virtual environment
echo ""
echo "[2/4] Creating virtual environment..."
if [ -d "venv" ]; then
    echo "Virtual environment already exists, skipping..."
else
    python3 -m venv venv
    echo "Virtual environment created"
fi

# Activate virtual environment
echo ""
echo "[3/4] Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo ""
echo "[4/4] Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "================================================"
echo "Setup Complete!"
echo "================================================"
echo ""
echo "Next steps:"
echo "  1. Make sure .env file has your HuggingFace API key"
echo "  2. Run the agent: python main.py"
echo "  3. Or run tests: python test_agent.py"
echo ""
echo "To activate the virtual environment later:"
echo "  source venv/bin/activate"
echo ""

