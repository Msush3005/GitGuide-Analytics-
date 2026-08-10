"""
GitGuide Analytics - Streamlit Interactive Web Dashboard Framework
Modular entrypoint located inside scripts/ directory.

Usage:
    streamlit run scripts/dashboard_app.py
"""

import os
import sys

# Add repository root to Python path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from app import main

if __name__ == "__main__":
    main()
