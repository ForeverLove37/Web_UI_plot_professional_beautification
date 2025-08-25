#!/usr/bin/env python3
"""
AcademicPlot Pro - Main Entry Point
A web application for beautifying academic plots with AI-powered translation and styling.
"""

import sys
from pathlib import Path

# Add the src directory to Python path
src_path = Path(__file__).parent / 'src'
sys.path.insert(0, str(src_path))

from web.app import app

def main():
    """Main function to start the web application"""
    print("AcademicPlot Pro - Starting Web Application")
    print("=" * 50)
    print("Access the application at: http://localhost:5000")
    print("Press Ctrl+C to stop the server")
    print("=" * 50)
    
    # Ensure directories exist
    from web.app import app
    import os
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)
    
    # Start the Flask application
    app.run(debug=True, use_reloader=False, host='0.0.0.0', port=5000)

if __name__ == '__main__':
    main()