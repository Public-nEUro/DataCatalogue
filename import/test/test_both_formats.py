#!/usr/bin/env python3
"""
Test both XML and JSONL export functionality
"""

import os
import sys
import json
import xml.etree.ElementTree as ET

# Get the directory where this script is located
script_dir = os.path.dirname(os.path.abspath(__file__))
# Get the import directory (parent of script if in subfolder, or script_dir itself)
import_dir = script_dir if os.path.basename(script_dir) == 'import' else os.path.dirname(script_dir)

# Add import directory to Python path
sys.path.insert(0, import_dir)

try:
    from export_xlsx import export_xlsx_to_both, export_xlsx_to_xml, export_xlsx_to_jsonl
    print("✓ Successfully imported both export functions")
    
    # Test the function with the example file
    excel_file = os.path.join(import_dir, "data_import", "PN000011 Clinical Pediatric MRI with and without Motion Correction", "PublicnEUro_PN000011.xlsx")
    
    print(f"Script directory: {script_dir}")
    print(f"Import directory: {import_dir}")
    print(f"Excel file path: {excel_file}")
    print(f"File exists: {os.path.exists(excel_file)}")
    
    if os.path.exists(excel_file):
        print("\n" + "="*60)
        print("TESTING BOTH XML AND JSONL EXPORT")
        print("="*60)
        
        # Test export to both formats
        xml_file, jsonl_file = export_xlsx_to_both(excel_file, 
                                                   os.path.join(script_dir, "test_both_output.xml"),
                                                   os.path.join(script_dir, "test_both_output.jsonl"))
        
        print(f"\n✓ Both files generated:")
        print(f"  XML:   {xml_file}")
        print(f"  JSONL: {jsonl_file}")
        
        # Validate XML file
        print("\n--- XML Validation ---")
        if os.path.exists(xml_file):
            try:
                tree = ET.parse(xml_file)
                root = tree.getroot()
                
                # Check key elements
                doi_elem = root.find(".//doi")
                timestamp_elem = root.find(".//timestamp")
                title_elem = root.find(".//titles/title")
                
                print(f"✓ XML is well-formed")
                print(f"  DOI: {doi_elem.text if doi_elem is not None else 'Not found'}")
                print(f"  Timestamp: {timestamp_elem.text if timestamp_elem is not None else 'Not found'}")
                print(f"  Title: {title_elem.text if title_elem is not None else 'Not found'}")
                
            except ET.ParseError as e:
                print(f"❌ XML parsing error: {e}")
        else:
            print("❌ XML file not found")
        
        # Validate JSONL file
        print("\n--- JSONL Validation ---")
        if os.path.exists(jsonl_file):
            try:
                with open(jsonl_file, 'r', encoding='utf-8') as f:
                    jsonl_content = f.read().strip()
                    jsonl_data = json.loads(jsonl_content)
                
                print(f"✓ JSONL is valid JSON")
                print(f"  Type: {jsonl_data.get('type', 'Not found')}")
                print(f"  DOI: {jsonl_data.get('doi', 'Not found')}")
                print(f"  Dataset Version: {jsonl_data.get('dataset_version', 'Not found')}")
                print(f"  Authors count: {len(jsonl_data.get('authors', []))}")
                print(f"  Keywords count: {len(jsonl_data.get('keywords', []))}")
                
            except json.JSONDecodeError as e:
                print(f"❌ JSONL parsing error: {e}")
        else:
            print("❌ JSONL file not found")
        
        # Compare data consistency
        print("\n--- Data Consistency Check ---")
        if os.path.exists(xml_file) and os.path.exists(jsonl_file):
            try:
                # Parse XML
                tree = ET.parse(xml_file)
                root = tree.getroot()
                xml_doi = root.find(".//doi").text if root.find(".//doi") is not None else ""
                
                # Parse JSONL
                with open(jsonl_file, 'r', encoding='utf-8') as f:
                    jsonl_data = json.loads(f.read().strip())
                    jsonl_doi = jsonl_data.get('doi', '')
                
                if xml_doi == jsonl_doi:
                    print(f"✓ DOI consistency: {xml_doi}")
                else:
                    print(f"❌ DOI mismatch: XML='{xml_doi}', JSONL='{jsonl_doi}'")
                
                # Check version formatting
                xml_resource = root.find(".//resource").text if root.find(".//resource") is not None else ""
                jsonl_version = jsonl_data.get('dataset_version', '')
                
                if jsonl_version in xml_resource:
                    print(f"✓ Version consistency: {jsonl_version}")
                else:
                    print(f"⚠️  Version check: XML resource='{xml_resource}', JSONL version='{jsonl_version}'")
                
            except Exception as e:
                print(f"❌ Consistency check error: {e}")
        
        print("\n" + "="*60)
        print("✅ BOTH FORMATS EXPORT TEST COMPLETED")
        print("="*60)
        
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
