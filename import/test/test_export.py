#!/usr/bin/env python3
import sys
import os

# Get the directory where this script is located
script_dir = os.path.dirname(os.path.abspath(__file__))
# Get the import directory (parent of script if in subfolder, or script_dir itself)
import_dir = script_dir if os.path.basename(script_dir) == 'import' else os.path.dirname(script_dir)

# Add import directory to Python path
sys.path.insert(0, import_dir)

try:
    from export_xlsx import export_xlsx_to_xml
except ImportError:
    print("Error: Could not import export_xlsx. Make sure export_xlsx.py is in the import directory.")
    sys.exit(1)

# Use absolute path for Excel file
excel_path = os.path.join(import_dir, 'data_import', 'PN000011 Clinical Pediatric MRI with and without Motion Correction', 'PublicnEUro_PN000011.xlsx')
output_path = os.path.join(script_dir, 'test_output.xml')

print(f'Script directory: {script_dir}')
print(f'Import directory: {import_dir}')
print(f'Excel file path: {excel_path}')
print('File exists:', os.path.exists(excel_path))

if os.path.exists(excel_path):
    try:
        result = export_xlsx_to_xml(excel_path, output_path)
        print('Output file:', result)
        print('Test completed successfully!')
    except Exception as e:
        print('Error:', str(e))
        import traceback
        traceback.print_exc()
else:
    print('Excel file not found')
    print('Make sure the Excel file exists in the data_import directory')
