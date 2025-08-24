#!/usr/bin/env python3
"""
Check if all required packages are installed
"""

import importlib
import sys

def check_package(package_name):
    """Check if a package is installed"""
    try:
        importlib.import_module(package_name)
        return True
    except ImportError:
        return False

def main():
    """Main function to check requirements"""
    required_packages = [
        'flask',
        'werkzeug', 
        'requests',
        'dotenv'
    ]
    
    print("Checking required packages...")
    print("=" * 40)
    
    all_installed = True
    for package in required_packages:
        if check_package(package):
            print(f"[OK] {package}")
        else:
            print(f"[MISSING] {package}")
            all_installed = False
    
    print("=" * 40)
    
    if all_installed:
        print("All requirements are installed!")
        return 0
    else:
        print("Some packages are missing. Please run: pip install -r requirements.txt")
        return 1

if __name__ == '__main__':
    sys.exit(main())