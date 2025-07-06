"""
Simple entry point for Streamlit Cloud deployment
This file ensures the dashboard can be run directly without the full run.py setup
"""
import os
import sys

# Add the project root to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Import and run the main dashboard
from dashboard.streamlit_app import main

if __name__ == "__main__":
    main()
