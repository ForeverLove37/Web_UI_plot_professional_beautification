#!/usr/bin/env python3
"""
Test script for the enhanced agent functionality
"""

import os
import sys
from enhanced_agent import process_python_file

def test_agent():
    # Test file path
    test_file = "test_plot.py"
    
    if not os.path.exists(test_file):
        print(f"Error: Test file '{test_file}' not found")
        return False
    
    print("Testing enhanced agent functionality...")
    print("=" * 50)
    
    # Test with academic mode enabled
    academic_options = {
        'enabled': True,
        'paper_format': 'nature',
        'layout': 'single',
        'vector_format': 'pdf',
        'dpi': 300
    }
    
    try:
        print("Processing with Nature style...")
        process_python_file(test_file, beautify=True, academic_options=academic_options)
        
        # Check if output file was created
        output_file = "test_plot_zh_revision.py"
        if os.path.exists(output_file):
            print(f"Success: Output file '{output_file}' created")
            
            # Read and show some content
            with open(output_file, 'r', encoding='utf-8') as f:
                content = f.read()
                print("\nGenerated content preview:")
                print("-" * 30)
                # Show first 10 lines
                lines = content.split('\n')[:10]
                for line in lines:
                    print(line)
                print("...")
                
            return True
        else:
            print("Error: Output file was not created")
            return False
            
    except Exception as e:
        print(f"Error during processing: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_agent()
    if success:
        print("\nAll tests passed!")
        sys.exit(0)
    else:
        print("\nTests failed!")
        sys.exit(1)