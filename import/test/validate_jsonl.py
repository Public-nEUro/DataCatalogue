#!/usr/bin/env python3

# Quick validation of the JSONL file after export
import json

input_file = "data_import/PN000009 Markerless Prospective Motion Correction/PublicnEuro_PN000009.jsonl"

print("Checking current JSONL file for issues...")

try:
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Check for problematic values
    if "NaN" in content:
        print("❌ Found 'NaN' in file - this will cause JSON parsing errors")
    else:
        print("✅ No 'NaN' found in file")
        
    if '"n.a."' in content:
        print("❌ Found 'n.a.' values in file")  
    else:
        print("✅ No 'n.a.' values found in file")
        
    # Try to parse as JSON
    data = json.loads(content)
    print("✅ File is valid JSON")
    
    # Check funding section specifically
    if 'funding' in data and data['funding']:
        print(f"Funding entries: {len(data['funding'])}")
        for i, fund in enumerate(data['funding']):
            name = fund.get('name', 'N/A')
            identifier = fund.get('identifier', 'N/A')
            print(f"  {i+1}. {name} - {identifier}")
    else:
        print("No funding entries found")
        
    # Check additional_display for n.a. values
    if 'additional_display' in data:
        na_count = 0
        for section in data['additional_display']:
            if isinstance(section, dict) and 'content' in section:
                content_str = str(section['content'])
                na_count += content_str.count('n.a.')
        if na_count > 0:
            print(f"❌ Found {na_count} 'n.a.' values in additional_display")
        else:
            print("✅ No 'n.a.' values in additional_display")
        
except json.JSONDecodeError as e:
    print(f"❌ JSON parsing failed: {e}")
except Exception as e:
    print(f"❌ Error: {e}")
