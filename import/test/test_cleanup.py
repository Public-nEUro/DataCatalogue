#!/usr/bin/env python3

# Test the new cleanup functionality
from export_xlsx import export_xlsx_to_jsonl
import json

# Test with the problematic file
excel_file = 'data_import/PN000009 Markerless Prospective Motion Correction/PublicnEuro_PN000009.xlsx'
output_file = export_xlsx_to_jsonl(excel_file)

# Read and display the funding section to see if NaN values were cleaned
with open(output_file, 'r', encoding='utf-8') as f:
    data = json.loads(f.read())
    
if 'funding' in data:
    print("Funding section after cleanup:")
    print(json.dumps(data['funding'], indent=2))
else:
    print("No funding section found in output")
