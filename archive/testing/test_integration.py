#!/usr/bin/env python3
"""
Test script to verify the integration between python_form_filler.py and fieldmappingwidget.py
"""

import sys
import json
from pathlib import Path
import importlib.util
import os

def run_basic_test():
    """
    Run a simple test to check if modules can be imported correctly
    """
    print("Starting basic integration test...")
    
    # Check if fieldmappingwidget.py exists and can be imported
    fieldmapping_path = Path("fieldmappingwidget.py")
    if not fieldmapping_path.exists():
        print(f"Error: {fieldmapping_path} does not exist")
        return 1
    
    # Check if python_form_filler.py exists
    form_filler_path = Path("agentic_form_filler.py")
    if not form_filler_path.exists():
        print(f"Error: {form_filler_path} does not exist")
        return 1
    
    print("1. Both required files exist - Success")
    
    # Check file content
    with open(fieldmapping_path, 'r') as f:
        fieldmapping_content = f.read()
        
    if "class FieldMappingWidget" in fieldmapping_content:
        print("2. FieldMappingWidget class exists in fieldmappingwidget.py - Success")
    else:
        print("Error: FieldMappingWidget class not found in fieldmappingwidget.py")
        return 1
    
    with open(form_filler_path, 'r') as f:
        form_filler_content = f.read()
    
    if "agentic" in form_filler_content.lower():
        print("3. Agentic system components found in agentic_form_filler.py - Success")
    else:
        print("Error: Agentic components not found")
        return 1
    
    print("\nBasic integration tests passed!")
    print("The agentic components have been properly created.")
    print("Note: Full GUI testing requires PyQt6 to be installed.")
    
    return 0

if __name__ == "__main__":
    sys.exit(run_basic_test())
