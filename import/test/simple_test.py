#!/usr/bin/env python3
import sys
import os

# Simple test script
print("Testing export_xlsx.py command line interface")
print("=" * 50)

# Set the working directory
os.chdir(r'd:\PublicnEUro\DataCatalogue\import')

# Test 1: No arguments (should show usage)
print("\n1. Testing with no arguments:")
os.system('python export_xlsx.py')

# Test 2: With a real file (default both formats)
excel_file = r'data_import\PN000011 Clinical Pediatric MRI with and without Motion Correction\PublicnEUro_PN000011.xlsx'
if os.path.exists(excel_file):
    print(f"\n2. Testing default behavior with: {excel_file}")
    os.system(f'python export_xlsx.py "{excel_file}"')
    
    # Check if files were created
    if os.path.exists('PublicnEUro_PN000011.xml'):
        print("✅ XML file created")
    else:
        print("❌ XML file NOT created")
        
    if os.path.exists('PublicnEUro_PN000011.jsonl'):
        print("✅ JSONL file created")
    else:
        print("❌ JSONL file NOT created")
else:
    print(f"❌ Test file not found: {excel_file}")

print("\nTest completed!")
