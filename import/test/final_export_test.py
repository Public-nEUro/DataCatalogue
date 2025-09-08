#!/usr/bin/env python3

# Final test: export the actual file and validate results
import os
import json
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("Starting export test with cleanup function...")

# Import the updated export function
try:
    from export_xlsx import export_xlsx_to_jsonl
    print("Successfully imported export function")
    
    excel_file = "data_import/PN000009 Markerless Prospective Motion Correction/PublicnEuro_PN000009.xlsx"
    
    if os.path.exists(excel_file):
        print(f"Excel file found: {excel_file}")
        
        # Backup original
        original_jsonl = "data_import/PN000009 Markerless Prospective Motion Correction/PublicnEuro_PN000009.jsonl"
        backup_jsonl = original_jsonl + ".old"
        
        if os.path.exists(original_jsonl):
            import shutil
            shutil.copy2(original_jsonl, backup_jsonl)
            print(f"Backed up original to: {backup_jsonl}")
        
        # Export new version
        print("Exporting with cleanup function...")
        output_file = export_xlsx_to_jsonl(excel_file)
        print(f"Export completed: {output_file}")
        
        # Validate results
        with open(output_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        print("\nValidation results:")
        
        # Check for NaN
        if "NaN" in content:
            print("FAIL: Still contains NaN")
        else:
            print("PASS: No NaN found")
            
        # Check for n.a.
        na_count = content.count('"n.a."')
        if na_count > 0:
            print(f"INFO: Found {na_count} 'n.a.' entries (may be in nested content)")
        else:
            print("PASS: No 'n.a.' entries found")
            
        # Parse JSON
        try:
            data = json.loads(content)
            print("PASS: Valid JSON structure")
            
            # Check funding specifically
            if 'funding' in data:
                print(f"Funding entries: {len(data['funding'])}")
                for i, fund in enumerate(data['funding']):
                    name = fund.get('name', 'Unknown')
                    identifier = fund.get('identifier', 'No identifier')
                    print(f"  {i+1}. {name} - {identifier}")
            else:
                print("No funding section found")
                
        except json.JSONDecodeError as e:
            print(f"FAIL: JSON parsing error: {e}")
            
    else:
        print(f"Excel file not found: {excel_file}")
        
except Exception as e:
    print(f"Error during export: {e}")
    import traceback
    traceback.print_exc()
    
print("Test completed.")
