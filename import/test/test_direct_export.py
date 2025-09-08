#!/usr/bin/env python3

# Direct test of export function
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from export_xlsx import export_xlsx_to_jsonl
    
    print("Testing export function...")
    excel_file = 'data_import/PN000009 Markerless Prospective Motion Correction/PublicnEuro_PN000009.xlsx'
    
    if os.path.exists(excel_file):
        output_file = export_xlsx_to_jsonl(excel_file)
        print(f"Export completed. Output file: {output_file}")
        
        # Read and check funding section
        import json
        with open(output_file, 'r', encoding='utf-8') as f:
            try:
                data = json.loads(f.read())
                if 'funding' in data:
                    print("Funding section:")
                    for fund in data['funding']:
                        print(f"  - Name: {fund.get('name', 'N/A')}")
                        print(f"    Identifier: {fund.get('identifier', 'N/A')}")
                else:
                    print("No funding section found")
            except json.JSONDecodeError as e:
                print(f"JSON decode error: {e}")
                # Read first few lines to see what went wrong
                with open(output_file, 'r', encoding='utf-8') as f2:
                    content = f2.read()[:1000]
                    print(f"File content preview: {content}")
    else:
        print(f"Excel file not found: {excel_file}")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
