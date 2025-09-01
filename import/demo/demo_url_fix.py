#!/usr/bin/env python3
"""
Demonstrate the fixed URL generation with proper version formatting
"""

import os
import sys
import pandas as pd

# Get the directory where this script is located
script_dir = os.path.dirname(os.path.abspath(__file__))
# Get the import directory (parent of script if in subfolder, or script_dir itself)
import_dir = script_dir if os.path.basename(script_dir) == 'import' else os.path.dirname(script_dir)

# Add import directory to Python path for potential imports
sys.path.insert(0, import_dir)

def format_version(version_value):
    """Format version to ensure it's always V followed by a number."""
    if pd.isna(version_value) or not version_value:
        return "VNone"
    
    version_str = str(version_value).strip()
    
    if version_str.startswith('V'):
        while version_str.startswith('VV'):
            version_str = version_str[1:]
        return version_str
    
    return f"V{version_str}"

def generate_url_example(pn_id, title, version_raw):
    """Generate URL with proper version formatting"""
    url_base = "https://datacatalog.publicneuro.eu/dataset/"
    url_dataset = f"{pn_id} {title}"
    url_version = format_version(version_raw)
    download_url = f"{url_base}{url_dataset}/{url_version}".replace(" ", "%20")
    return download_url

print("URL GENERATION WITH FIXED VERSION FORMATTING")
print("=" * 60)
print(f"Script running from: {script_dir}")
print(f"Import directory: {import_dir}")
print("=" * 60)

# Example data similar to PN000011
test_cases = [
    {
        "pn_id": "PN000011",
        "title": "A dataset of clinical pediatric brain MRI with and without motion correction",
        "version": "1",
        "description": "Excel has just '1'"
    },
    {
        "pn_id": "PN000011", 
        "title": "A dataset of clinical pediatric brain MRI with and without motion correction",
        "version": "V1",
        "description": "Excel has 'V1'"
    },
    {
        "pn_id": "PN000011",
        "title": "A dataset of clinical pediatric brain MRI with and without motion correction", 
        "version": "VV1",
        "description": "Excel has 'VV1' (problematic case)"
    },
    {
        "pn_id": "PN000012",
        "title": "Another dataset",
        "version": "2.0",
        "description": "Excel has '2.0'"
    }
]

for i, case in enumerate(test_cases, 1):
    print(f"\nTest Case {i}: {case['description']}")
    print(f"PN ID: {case['pn_id']}")
    print(f"Title: {case['title']}")
    print(f"Version from Excel: '{case['version']}'")
    
    formatted_version = format_version(case['version'])
    url = generate_url_example(case['pn_id'], case['title'], case['version'])
    
    print(f"Formatted Version: {formatted_version}")
    print(f"Generated URL: {url}")
    print("-" * 60)

print("\n✅ FIXED ISSUES:")
print("- No more VV1 -> now correctly produces V1")
print("- Handles both '1' and 'V1' from Excel correctly") 
print("- URL versioning is consistent: always V + number")
print("- Matches the expected format from your backup file")

print(f"\n📝 NOTE:")
print(f"Your backup file had 'VNone' which suggests the Excel had 'None' as version.")
print(f"The current file had 'VV1' which was the bug we just fixed.")
print(f"Now it will correctly show 'V1' instead of 'VV1'.")
