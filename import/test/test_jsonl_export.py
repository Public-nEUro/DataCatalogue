#!/usr/bin/env python3
"""
Test the JSONL export functionality
"""

import os
import sys
import json

# Get the directory where this script is located
script_dir = os.path.dirname(os.path.abspath(__file__))
# Get the import directory (parent of script if in subfolder, or script_dir itself)
import_dir = script_dir if os.path.basename(script_dir) == 'import' else os.path.dirname(script_dir)

# Add import directory to Python path
sys.path.insert(0, import_dir)

try:
    from export_xlsx import export_xlsx_to_jsonl, parse_excel_metadata
    print("✓ Successfully imported JSONL export functions")
    
    # Test the function with the example file
    excel_file = os.path.join(import_dir, "data_import", "PN000011 Clinical Pediatric MRI with and without Motion Correction", "PublicnEUro_PN000011.xlsx")
    output_file = os.path.join(script_dir, "test_output_PN000011.jsonl")
    
    print(f"Script directory: {script_dir}")
    print(f"Import directory: {import_dir}")
    print(f"Excel file path: {excel_file}")
    print(f"File exists: {os.path.exists(excel_file)}")
    
    if os.path.exists(excel_file):
        print("\n--- Testing metadata parsing ---")
        metadata = parse_excel_metadata(excel_file)
        
        print(f"✓ Parsed metadata successfully")
        print(f"  - Title: {metadata.get('title', 'N/A')}")
        print(f"  - DOI: {metadata.get('doi', 'N/A')}")
        print(f"  - Authors: {len(metadata.get('authors', []))} found")
        print(f"  - Funding sources: {len(metadata.get('funding', []))} found")
        print(f"  - Publications: {len(metadata.get('publications', []))} found")
        print(f"  - Keywords: {len(metadata.get('keywords', []))} found")
        
        print("\n--- Testing JSONL export ---")
        result = export_xlsx_to_jsonl(excel_file, output_file)
        print(f"✓ JSONL exported successfully to: {result}")
        
        # Read and validate the generated JSONL
        if os.path.exists(result):
            with open(result, 'r', encoding='utf-8') as f:
                jsonl_content = f.read().strip()
                jsonl_data = json.loads(jsonl_content)
            
            print("\n--- JSONL Content Validation ---")
            required_fields = [
                "type", "name", "description", "dataset_id", "dataset_version",
                "doi", "download_url", "keywords", "license", "authors",
                "funding", "publications", "metadata_sources", "additional_display"
            ]
            
            for field in required_fields:
                if field in jsonl_data:
                    print(f"✓ {field}: {type(jsonl_data[field]).__name__}")
                    if field == "doi":
                        print(f"    Value: {jsonl_data[field]}")
                    elif field == "dataset_version":
                        print(f"    Value: {jsonl_data[field]}")
                else:
                    print(f"❌ {field}: Missing")
            
            print("\n--- First few lines of generated JSONL structure ---")
            print(json.dumps(jsonl_data, indent=2)[:500] + "...")
            
    else:
        print("❌ Excel file not found")
        print("Make sure the Excel file exists in the data_import directory")
        
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("Make sure export_xlsx.py is in the import directory")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
