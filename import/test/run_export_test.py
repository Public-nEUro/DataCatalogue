#!/usr/bin/env python3

# Test the export with the new cleanup function
import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from export_xlsx import export_xlsx_to_jsonl

excel_file = "data_import/PN000009 Markerless Prospective Motion Correction/PublicnEuro_PN000009.xlsx"

try:
    print(f"Exporting {excel_file}...")
    output_file = export_xlsx_to_jsonl(excel_file)
    print(f"Export completed successfully!")
    print(f"Output file: {output_file}")
    
    # Test if the output is valid JSON
    import json
    with open(output_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print("JSON validation: PASSED")
    
    # Check funding section specifically
    if 'funding' in data and data['funding']:
        print(f"Funding entries found: {len(data['funding'])}")
        for i, fund in enumerate(data['funding']):
            print(f"  Funding {i+1}:")
            print(f"    Name: {fund.get('name', 'N/A')}")
            print(f"    Identifier: {fund.get('identifier', 'N/A')}")
    else:
        print("No funding entries found or funding array is empty")
        
except Exception as e:
    print(f"Error occurred: {e}")
    import traceback
    traceback.print_exc()
