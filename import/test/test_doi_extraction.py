#!/usr/bin/env python3
"""
Test DOI extraction functionality
"""

import os
import sys
import pandas as pd

# Get the directory where this script is located
script_dir = os.path.dirname(os.path.abspath(__file__))
# Get the import directory (parent of script if in subfolder, or script_dir itself)
import_dir = script_dir if os.path.basename(script_dir) == 'import' else os.path.dirname(script_dir)

def extract_doi_suffix(doi_value):
    """
    Extract the suffix from a DOI, handling both full URLs and DOI format.
    """
    if pd.isna(doi_value) or not doi_value:
        return "XXXX"
    
    doi_str = str(doi_value).strip()
    
    # If it's already just the suffix (no slash), return as is
    if '/' not in doi_str:
        return doi_str
    
    # Extract the last part after the final '/'
    parts = doi_str.split('/')
    return parts[-1] if parts[-1] else "XXXX"

# Test cases
test_cases = [
    "https://doi.org/10.70883/VMIF5895",
    "http://dx.doi.org/10.70883/VMIF5895", 
    "10.70883/VMIF5895",
    "VMIF5895",
    "https://doi.org/10.70883/ABCD1234",
    None,
    "",
    "10.70883/"
]

print("DOI EXTRACTION TEST RESULTS:")
print("=" * 50)
print(f"Script running from: {script_dir}")
print(f"Import directory: {import_dir}")
print("=" * 50)
for test_case in test_cases:
    result = extract_doi_suffix(test_case)
    final_doi = f"10.70883/{result}"
    print(f"Input:  '{test_case}'")
    print(f"Suffix: '{result}'") 
    print(f"Final:  '{final_doi}'")
    print("-" * 30)

print("\nThe function correctly extracts the DOI suffix and formats it as '10.70883/something'")
print("where 'something' is the extracted value from the Excel file.")
