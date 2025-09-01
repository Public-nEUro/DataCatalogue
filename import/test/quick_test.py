import sys
import os

# Add the import directory to path
sys.path.insert(0, r'd:\PublicnEUro\DataCatalogue\import')

from export_xlsx import export_xlsx_to_both

# Test the functionality directly
excel_file = r'd:\PublicnEUro\DataCatalogue\import\data_import\PN000011 Clinical Pediatric MRI with and without Motion Correction\PublicnEUro_PN000011.xlsx'

if os.path.exists(excel_file):
    print(f"Testing with file: {excel_file}")
    try:
        xml_file, jsonl_file = export_xlsx_to_both(excel_file)
        print(f"✅ SUCCESS! Generated:")
        print(f"   XML: {xml_file}")
        print(f"   JSONL: {jsonl_file}")
    except Exception as e:
        print(f"❌ ERROR: {e}")
else:
    print(f"❌ File not found: {excel_file}")
