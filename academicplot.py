#!/usr/bin/env python3
"""
AcademicPlot Pro - Main Entry Point
A web application for beautifying academic plots with AI-powered translation and styling.
"""

import sys
import os
import logging
from pathlib import Path
from waitress import serve


# Add the src directory to Python path
src_path = Path(__file__).parent / 'src'
sys.path.insert(0, str(src_path))

from web.app import app
def setup_logging():
    """Sets up the application logging for production."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        filename='app.log',
        filemode='a' # 'a' for append, so logs are not lost on restart
    )
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)

def main():
    """Main function to start the production web application"""
    setup_logging()

    logging.info("AcademicPlot Pro - Starting Production Server with Waitress")
    print("=" * 50)
    print("Access the application at: http://<your_server_ip>:5000")
    print("Press Ctrl+C to stop the server")
    print("=" * 50)

    # Ensure directories exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

    # use waitress.serve to run application
    serve(app, host='0.0.0.0', port=6060)

if __name__ == "__main__":
    main()
