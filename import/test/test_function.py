#!/usr/bin/env python3
"""
Test script to demonstrate the export_xlsx function
"""

import os
import sys

# Get the directory where this script is located
script_dir = os.path.dirname(os.path.abspath(__file__))
# Get the import directory (parent of script if in subfolder, or script_dir itself)
import_dir = script_dir if os.path.basename(script_dir) == 'import' else os.path.dirname(script_dir)

# Add import directory to Python path
sys.path.insert(0, import_dir)

try:
    from export_xlsx import export_xlsx_to_xml
    print("✓ Successfully imported export_xlsx_to_xml function")
    
    # Test the function with the example file
    excel_file = os.path.join(import_dir, "data_import", "PN000011 Clinical Pediatric MRI with and without Motion Correction", "PublicnEUro_PN000011.xlsx")
    output_file = os.path.join(script_dir, "test_output_PN000011.xml")
    
    print(f"Excel file path: {excel_file}")
    print(f"File exists: {os.path.exists(excel_file)}")
    
    if os.path.exists(excel_file):
        print("Running export function...")
        result = export_xlsx_to_xml(excel_file, output_file)
        print(f"✓ XML exported successfully to: {result}")
        
        # Read and show first few lines of the output
        if os.path.exists(result):
            with open(result, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
                print("\n--- First 20 lines of generated XML ---")
                for i, line in enumerate(lines[:20]):
                    print(f"{i+1:2}: {line}")
                print("...")
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
