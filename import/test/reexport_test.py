#!/usr/bin/env python3

# Re-export the file with the updated function
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("Re-exporting JSONL file with updated cleanup function...")

try:
    from export_xlsx import export_xlsx_to_jsonl
    
    excel_file = "data_import/PN000009 Markerless Prospective Motion Correction/PublicnEuro_PN000009.xlsx"
    
    # Export with the new cleanup function
    output_file = export_xlsx_to_jsonl(excel_file)
    
    print(f"✅ Export completed: {output_file}")
    
    # Validate the new file
    import json
    with open(output_file, 'r', encoding='utf-8') as f:
        content = f.read()
        
    print("\nValidating new file...")
    
    # Check for problematic values
    if "NaN" in content:
        print("❌ Still has 'NaN' in file")
    else:
        print("✅ No 'NaN' found")
        
    if '"n.a."' in content:
        print("❌ Still has 'n.a.' values")  
    else:
        print("✅ No 'n.a.' values found")
        
    # Parse JSON
    data = json.loads(content)
    print("✅ New file is valid JSON")
    
    # Check funding section
    if 'funding' in data and data['funding']:
        print(f"\nFunding entries: {len(data['funding'])}")
        for i, fund in enumerate(data['funding']):
            name = fund.get('name', 'N/A')
            identifier = fund.get('identifier', 'N/A')
            print(f"  {i+1}. {name} - {identifier}")
    else:
        print("No funding entries found")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
