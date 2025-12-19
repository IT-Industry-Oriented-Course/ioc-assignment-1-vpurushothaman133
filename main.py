"""
Clinical Workflow Automation Agent - Main Entry Point

This is a function-calling LLM agent for healthcare workflow orchestration.
It does NOT provide medical advice - only administrative automation.

Usage:
    python main.py                    # Normal mode
    python main.py --dry-run          # Dry-run mode (simulate only)
    python main.py --help             # Show help
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.dirname(__file__))

from src.cli import main

if __name__ == "__main__":
    main()

