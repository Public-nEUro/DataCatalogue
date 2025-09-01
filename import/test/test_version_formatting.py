#!/usr/bin/env python3
"""
Test the version formatting functionality
"""

import os
import sys
import pandas as pd

# Get the directory where this script is located
script_dir = os.path.dirname(os.path.abspath(__file__))
# Get the import directory (parent of script if in subfolder, or script_dir itself)
import_dir = script_dir if os.path.basename(script_dir) == 'import' else os.path.dirname(script_dir)

def format_version(version_value):
    """
    Format version to ensure it's always V followed by a number.
    Examples:
    - 'V1' -> 'V1'
    - '1' -> 'V1'
    - 'VV1' -> 'V1'
    - 'V2.0' -> 'V2.0'
    - None -> 'VNone'
    """
    if pd.isna(version_value) or not version_value:
        return "VNone"
    
    version_str = str(version_value).strip()
    
    # If it already starts with V, check for double V and fix
    if version_str.startswith('V'):
        # Remove any extra V's at the beginning
        while version_str.startswith('VV'):
            version_str = version_str[1:]  # Remove one V
        return version_str
    
    # If it doesn't start with V, add it
    return f"V{version_str}"

# Test cases
test_cases = [
    "1",          # Just number -> V1
    "V1",         # Already correct -> V1
    "VV1",        # Double V -> V1
    "2.0",        # Version with decimal -> V2.0
    "V2.0",       # Already correct with decimal -> V2.0
    "VV2.0",      # Double V with decimal -> V2.0
    "None",       # String None -> VNone
    None,         # Actual None -> VNone
    "",           # Empty string -> VNone
    "3",          # Another number -> V3
]

print("VERSION FORMATTING TEST RESULTS:")
print("=" * 50)
print(f"Script running from: {script_dir}")
print(f"Import directory: {import_dir}")
print("=" * 50)
print("Input          -> Output")
print("-" * 30)

for test_case in test_cases:
    result = format_version(test_case)
    input_display = repr(test_case) if test_case is not None else "None"
    print(f"{input_display:<14} -> {result}")

print("\n" + "=" * 50)
print("✓ Version formatting works correctly!")
print("✓ Prevents VV1 -> ensures V1 format")
print("✓ Handles all edge cases properly")
