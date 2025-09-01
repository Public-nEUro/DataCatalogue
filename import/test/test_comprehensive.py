#!/usr/bin/env python3
"""
Comprehensive test of the new default behavior in export_xlsx.py
"""

import os
import sys
import subprocess
import tempfile

def test_all_scenarios():
    """Test all usage scenarios"""
    print("🧪 Comprehensive Test of export_xlsx.py v2.0")
    print("=" * 60)
    
    # Set up paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    export_script = os.path.join(script_dir, "export_xlsx.py")
    excel_file = os.path.join(script_dir, "data_import", "PN000011 Clinical Pediatric MRI with and without Motion Correction", "PublicnEUro_PN000011.xlsx")
    
    if not os.path.exists(excel_file):
        print(f"❌ Test file not found: {excel_file}")
        return False
    
    print(f"📁 Test file: {os.path.basename(excel_file)}")
    print(f"🔧 Script: {os.path.basename(export_script)}")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        original_cwd = os.getcwd()
        os.chdir(temp_dir)
        
        try:
            tests_passed = 0
            total_tests = 4
            
            # Test 1: Default behavior (both formats)
            print(f"\n📋 Test 1: Default behavior (both formats)")
            result = subprocess.run([
                sys.executable, export_script, excel_file
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                xml_exists = os.path.exists("PublicnEUro_PN000011.xml")
                jsonl_exists = os.path.exists("PublicnEUro_PN000011.jsonl")
                if xml_exists and jsonl_exists:
                    print("✅ PASS: Both XML and JSONL files created by default")
                    tests_passed += 1
                else:
                    print(f"❌ FAIL: Missing files - XML: {xml_exists}, JSONL: {jsonl_exists}")
            else:
                print(f"❌ FAIL: Script error - {result.stderr}")
            
            # Clean up
            for f in os.listdir('.'):
                if f.endswith(('.xml', '.jsonl')):
                    os.remove(f)
            
            # Test 2: XML only
            print(f"\n📋 Test 2: XML only format")
            result = subprocess.run([
                sys.executable, export_script, excel_file, "xml"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                xml_exists = os.path.exists("PublicnEUro_PN000011.xml")
                jsonl_exists = os.path.exists("PublicnEUro_PN000011.jsonl")
                if xml_exists and not jsonl_exists:
                    print("✅ PASS: Only XML file created")
                    tests_passed += 1
                else:
                    print(f"❌ FAIL: Wrong files - XML: {xml_exists}, JSONL: {jsonl_exists}")
            else:
                print(f"❌ FAIL: Script error - {result.stderr}")
            
            # Clean up
            for f in os.listdir('.'):
                if f.endswith(('.xml', '.jsonl')):
                    os.remove(f)
            
            # Test 3: JSONL only
            print(f"\n📋 Test 3: JSONL only format")
            result = subprocess.run([
                sys.executable, export_script, excel_file, "jsonl"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                xml_exists = os.path.exists("PublicnEUro_PN000011.xml")
                jsonl_exists = os.path.exists("PublicnEUro_PN000011.jsonl")
                if jsonl_exists and not xml_exists:
                    print("✅ PASS: Only JSONL file created")
                    tests_passed += 1
                else:
                    print(f"❌ FAIL: Wrong files - XML: {xml_exists}, JSONL: {jsonl_exists}")
            else:
                print(f"❌ FAIL: Script error - {result.stderr}")
            
            # Clean up
            for f in os.listdir('.'):
                if f.endswith(('.xml', '.jsonl')):
                    os.remove(f)
            
            # Test 4: Custom output paths
            print(f"\n📋 Test 4: Custom output path")
            result = subprocess.run([
                sys.executable, export_script, excel_file, "xml", "custom_output.xml"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                custom_exists = os.path.exists("custom_output.xml")
                default_exists = os.path.exists("PublicnEUro_PN000011.xml")
                if custom_exists and not default_exists:
                    print("✅ PASS: Custom output file created")
                    tests_passed += 1
                else:
                    print(f"❌ FAIL: Wrong files - Custom: {custom_exists}, Default: {default_exists}")
            else:
                print(f"❌ FAIL: Script error - {result.stderr}")
            
            # Summary
            print(f"\n{'='*60}")
            print(f"🎯 Test Results: {tests_passed}/{total_tests} passed")
            
            if tests_passed == total_tests:
                print("🎉 ALL TESTS PASSED! New default behavior works correctly.")
                return True
            else:
                print("❌ Some tests failed.")
                return False
                
        finally:
            os.chdir(original_cwd)

if __name__ == "__main__":
    success = test_all_scenarios()
    sys.exit(0 if success else 1)
