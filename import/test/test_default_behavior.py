#!/usr/bin/env python3
"""
Test default behavior: both XML and JSONL export by default
"""

import os
import sys
import subprocess
import tempfile

# Add parent directory to path for imports
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)
sys.path.insert(0, parent_dir)

def test_default_both_formats():
    """Test that default behavior outputs both XML and JSONL files"""
    print("\n=== Testing Default Behavior (Both Formats) ===")
    
    # Locate the test Excel file
    excel_file = os.path.join(parent_dir, "data_import", "PN000011 Clinical Pediatric MRI with and without Motion Correction", "PublicnEUro_PN000011.xlsx")
    export_script = os.path.join(parent_dir, "export_xlsx.py")
    
    if not os.path.exists(excel_file):
        print(f"❌ Test Excel file not found: {excel_file}")
        return False
    
    if not os.path.exists(export_script):
        print(f"❌ Export script not found: {export_script}")
        return False
    
    # Create temporary directory for output
    with tempfile.TemporaryDirectory() as temp_dir:
        # Change to temp directory to ensure output files are created there
        original_cwd = os.getcwd()
        os.chdir(temp_dir)
        
        try:
            # Run the script with default behavior (no format specified)
            result = subprocess.run([
                sys.executable, export_script, excel_file
            ], capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"❌ Script execution failed: {result.stderr}")
                return False
            
            # Check that both files were created
            base_name = "PublicnEUro_PN000011"
            xml_file = f"{base_name}.xml"
            jsonl_file = f"{base_name}.jsonl"
            
            xml_exists = os.path.exists(xml_file)
            jsonl_exists = os.path.exists(jsonl_file)
            
            print(f"Output in: {temp_dir}")
            print(f"XML file created: {xml_exists} ({xml_file})")
            print(f"JSONL file created: {jsonl_exists} ({jsonl_file})")
            print(f"Script output: {result.stdout}")
            
            if xml_exists and jsonl_exists:
                print("✅ Default behavior test passed: Both files created")
                return True
            else:
                print("❌ Default behavior test failed: Missing output files")
                return False
                
        finally:
            os.chdir(original_cwd)

def test_single_format_xml():
    """Test XML-only output"""
    print("\n=== Testing XML-Only Format ===")
    
    excel_file = os.path.join(parent_dir, "data_import", "PN000011 Clinical Pediatric MRI with and without Motion Correction", "PublicnEUro_PN000011.xlsx")
    export_script = os.path.join(parent_dir, "export_xlsx.py")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        original_cwd = os.getcwd()
        os.chdir(temp_dir)
        
        try:
            # Run with xml format specified
            result = subprocess.run([
                sys.executable, export_script, excel_file, "xml"
            ], capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"❌ Script execution failed: {result.stderr}")
                return False
            
            # Check that only XML file was created
            xml_file = "PublicnEUro_PN000011.xml"
            jsonl_file = "PublicnEUro_PN000011.jsonl"
            
            xml_exists = os.path.exists(xml_file)
            jsonl_exists = os.path.exists(jsonl_file)
            
            print(f"XML file created: {xml_exists}")
            print(f"JSONL file created: {jsonl_exists}")
            print(f"Script output: {result.stdout}")
            
            if xml_exists and not jsonl_exists:
                print("✅ XML-only test passed")
                return True
            else:
                print("❌ XML-only test failed")
                return False
                
        finally:
            os.chdir(original_cwd)

def test_single_format_jsonl():
    """Test JSONL-only output"""
    print("\n=== Testing JSONL-Only Format ===")
    
    excel_file = os.path.join(parent_dir, "data_import", "PN000011 Clinical Pediatric MRI with and without Motion Correction", "PublicnEUro_PN000011.xlsx")
    export_script = os.path.join(parent_dir, "export_xlsx.py")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        original_cwd = os.getcwd()
        os.chdir(temp_dir)
        
        try:
            # Run with jsonl format specified
            result = subprocess.run([
                sys.executable, export_script, excel_file, "jsonl"
            ], capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"❌ Script execution failed: {result.stderr}")
                return False
            
            # Check that only JSONL file was created
            xml_file = "PublicnEUro_PN000011.xml"
            jsonl_file = "PublicnEUro_PN000011.jsonl"
            
            xml_exists = os.path.exists(xml_file)
            jsonl_exists = os.path.exists(jsonl_file)
            
            print(f"XML file created: {xml_exists}")
            print(f"JSONL file created: {jsonl_exists}")
            print(f"Script output: {result.stdout}")
            
            if jsonl_exists and not xml_exists:
                print("✅ JSONL-only test passed")
                return True
            else:
                print("❌ JSONL-only test failed")
                return False
                
        finally:
            os.chdir(original_cwd)

if __name__ == "__main__":
    print("Testing New Default Behavior")
    print("=" * 50)
    
    tests_passed = 0
    total_tests = 3
    
    # Run all tests
    if test_default_both_formats():
        tests_passed += 1
    
    if test_single_format_xml():
        tests_passed += 1
        
    if test_single_format_jsonl():
        tests_passed += 1
    
    print(f"\n{'='*50}")
    print(f"Test Results: {tests_passed}/{total_tests} passed")
    
    if tests_passed == total_tests:
        print("🎉 All tests passed!")
        sys.exit(0)
    else:
        print("❌ Some tests failed")
        sys.exit(1)
