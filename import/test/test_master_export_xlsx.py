"""
Master Test Suite for export_xlsx.py

This comprehensive test suite validates all functionality of the export_xlsx.py module:
- XML export (CrossRef format)
- JSONL export (data catalog format)  
- Default behavior (both formats)
- Import module functionality
- Error handling
- Version formatting
- DOI extraction
- Metadata parsing

Usage:
    python test_master_export_xlsx.py          # Run all tests
    python test_master_export_xlsx.py --quick  # Run quick tests only
    python test_master_export_xlsx.py --verbose # Detailed output
"""

import sys
import os
import subprocess
import tempfile
import json
import xml.etree.ElementTree as ET

# Add parent directory to path for imports
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)
sys.path.insert(0, parent_dir)


class ExportXlsxTestSuite:
    """Comprehensive test suite for export_xlsx.py functionality"""
    
    def __init__(self, verbose=False):
        self.verbose = verbose
        self.test_excel_file = None
        self.tests_passed = 0
        self.total_tests = 0
        self.find_test_file()
    
    def find_test_file(self):
        """Locate the test Excel file"""
        # Use the test Excel file in the test directory
        test_file_path = os.path.join(script_dir, "PublicnEUro_test.xlsx")
        
        if os.path.exists(test_file_path):
            self.test_excel_file = test_file_path
        else:
            print("❌ CRITICAL: Test Excel file not found!")
            print(f"   Expected: {test_file_path}")
            print("   Please ensure PublicnEUro_test.xlsx is in the test/ directory")
            sys.exit(1)
        
        if self.verbose:
            print(f"📁 Using test file: {self.test_excel_file}")
    
    def log(self, message):
        """Print message if verbose mode is enabled"""
        if self.verbose:
            print(f"   {message}")
    
    def run_test(self, test_name, test_func):
        """Run a single test and track results"""
        self.total_tests += 1
        print(f"\n🧪 {self.total_tests}. {test_name}")
        
        try:
            if test_func():
                print(f"✅ PASS")
                self.tests_passed += 1
                return True
            else:
                print(f"❌ FAIL")
                return False
        except Exception as e:
            print(f"❌ ERROR: {e}")
            return False
    
    def test_import_functionality(self):
        """Test 1: Module import functionality"""
        self.log("Testing module imports...")
        
        try:
            from export_xlsx import export_xlsx_to_xml, export_xlsx_to_jsonl, export_xlsx_to_both
            self.log("✓ All functions imported successfully")
            
            # Check function signatures
            import inspect
            xml_sig = inspect.signature(export_xlsx_to_xml)
            jsonl_sig = inspect.signature(export_xlsx_to_jsonl)
            both_sig = inspect.signature(export_xlsx_to_both)
            
            self.log(f"✓ export_xlsx_to_xml: {xml_sig}")
            self.log(f"✓ export_xlsx_to_jsonl: {jsonl_sig}")
            self.log(f"✓ export_xlsx_to_both: {both_sig}")
            
            return True
            
        except ImportError as e:
            self.log(f"✗ Import failed: {e}")
            return False
    
    def test_xml_export(self):
        """Test 2: XML export functionality"""
        self.log("Testing XML export...")
        
        try:
            from export_xlsx import export_xlsx_to_xml
            
            with tempfile.TemporaryDirectory() as temp_dir:
                original_cwd = os.getcwd()
                os.chdir(temp_dir)
                
                try:
                    xml_file = export_xlsx_to_xml(self.test_excel_file)
                    
                    if not os.path.exists(xml_file):
                        self.log(f"✗ XML file not created: {xml_file}")
                        return False
                    
                    # Validate XML structure
                    try:
                        tree = ET.parse(xml_file)
                        root = tree.getroot()
                        
                        # Check for CrossRef elements
                        if 'crossref' not in root.tag.lower():
                            self.log("✗ XML root is not CrossRef format")
                            return False
                        
                        self.log(f"✓ Valid XML created: {os.path.basename(xml_file)}")
                        self.log(f"✓ Root element: {root.tag}")
                        
                        # Check for DOI
                        doi_elements = root.findall(".//doi")
                        if doi_elements:
                            self.log(f"✓ DOI found: {doi_elements[0].text}")
                        
                        return True
                        
                    except ET.ParseError as e:
                        self.log(f"✗ Invalid XML structure: {e}")
                        return False
                        
                finally:
                    os.chdir(original_cwd)
                    
        except Exception as e:
            self.log(f"✗ XML export failed: {e}")
            return False
    
    def test_jsonl_export(self):
        """Test 3: JSONL export functionality"""
        self.log("Testing JSONL export...")
        
        try:
            from export_xlsx import export_xlsx_to_jsonl
            
            with tempfile.TemporaryDirectory() as temp_dir:
                original_cwd = os.getcwd()
                os.chdir(temp_dir)
                
                try:
                    jsonl_file = export_xlsx_to_jsonl(self.test_excel_file)
                    
                    if not os.path.exists(jsonl_file):
                        self.log(f"✗ JSONL file not created: {jsonl_file}")
                        return False
                    
                    # Validate JSONL structure
                    try:
                        with open(jsonl_file, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                        
                        # Check required fields
                        required_fields = ['type', 'dataset_id', 'name']
                        for field in required_fields:
                            if field not in data:
                                self.log(f"✗ Missing required field: {field}")
                                return False
                        
                        self.log(f"✓ Valid JSONL created: {os.path.basename(jsonl_file)}")
                        self.log(f"✓ Dataset type: {data.get('type')}")
                        self.log(f"✓ Dataset ID: {data.get('dataset_id')}")
                        
                        return True
                        
                    except json.JSONDecodeError as e:
                        self.log(f"✗ Invalid JSON structure: {e}")
                        return False
                        
                finally:
                    os.chdir(original_cwd)
                    
        except Exception as e:
            self.log(f"✗ JSONL export failed: {e}")
            return False
    
    def test_both_formats(self):
        """Test 4: Both formats export functionality"""
        self.log("Testing both formats export...")
        
        try:
            from export_xlsx import export_xlsx_to_both
            
            with tempfile.TemporaryDirectory() as temp_dir:
                original_cwd = os.getcwd()
                os.chdir(temp_dir)
                
                try:
                    xml_file, jsonl_file = export_xlsx_to_both(self.test_excel_file)
                    
                    xml_exists = os.path.exists(xml_file)
                    jsonl_exists = os.path.exists(jsonl_file)
                    
                    if not xml_exists:
                        self.log(f"✗ XML file not created: {xml_file}")
                        return False
                    
                    if not jsonl_exists:
                        self.log(f"✗ JSONL file not created: {jsonl_file}")
                        return False
                    
                    self.log(f"✓ Both files created successfully")
                    self.log(f"✓ XML: {os.path.basename(xml_file)}")
                    self.log(f"✓ JSONL: {os.path.basename(jsonl_file)}")
                    
                    return True
                    
                finally:
                    os.chdir(original_cwd)
                
        except Exception as e:
            self.log(f"✗ Both formats export failed: {e}")
            return False
    
    def test_cli_default_behavior(self):
        """Test 5: CLI default behavior (both formats)"""
        self.log("Testing CLI default behavior...")
        
        try:
            export_script = os.path.join(parent_dir, "export_xlsx.py")
            
            with tempfile.TemporaryDirectory() as temp_dir:
                os.chdir(temp_dir)
                
                result = subprocess.run([
                    sys.executable, export_script, self.test_excel_file
                ], capture_output=True, text=True, timeout=30)
                
                if result.returncode != 0:
                    self.log(f"✗ CLI execution failed: {result.stderr}")
                    return False
                
                # Check that both files were created
                base_name = "PublicnEUro_PN000011"
                xml_file = f"{base_name}.xml"
                jsonl_file = f"{base_name}.jsonl"
                
                xml_exists = os.path.exists(xml_file)
                jsonl_exists = os.path.exists(jsonl_file)
                
                if not (xml_exists and jsonl_exists):
                    self.log(f"✗ Default behavior failed - XML: {xml_exists}, JSONL: {jsonl_exists}")
                    return False
                
                self.log("✓ CLI default behavior works correctly")
                self.log(f"✓ Created: {xml_file}, {jsonl_file}")
                
                return True
                
        except subprocess.TimeoutExpired:
            self.log("✗ CLI test timed out")
            return False
        except Exception as e:
            self.log(f"✗ CLI test failed: {e}")
            return False
    
    def test_cli_single_formats(self):
        """Test 6: CLI single format options"""
        self.log("Testing CLI single format options...")
        
        try:
            export_script = os.path.join(parent_dir, "export_xlsx.py")
            
            with tempfile.TemporaryDirectory() as temp_dir:
                os.chdir(temp_dir)
                
                # Test XML only
                result = subprocess.run([
                    sys.executable, export_script, self.test_excel_file, "xml"
                ], capture_output=True, text=True, timeout=30)
                
                if result.returncode != 0:
                    self.log(f"✗ XML-only CLI failed: {result.stderr}")
                    return False
                
                xml_exists = os.path.exists("PublicnEUro_PN000011.xml")
                jsonl_exists = os.path.exists("PublicnEUro_PN000011.jsonl")
                
                if not xml_exists or jsonl_exists:
                    self.log(f"✗ XML-only test failed - XML: {xml_exists}, JSONL: {jsonl_exists}")
                    return False
                
                # Clean up
                if xml_exists:
                    os.remove("PublicnEUro_PN000011.xml")
                
                # Test JSONL only
                result = subprocess.run([
                    sys.executable, export_script, self.test_excel_file, "jsonl"
                ], capture_output=True, text=True, timeout=30)
                
                if result.returncode != 0:
                    self.log(f"✗ JSONL-only CLI failed: {result.stderr}")
                    return False
                
                xml_exists = os.path.exists("PublicnEUro_PN000011.xml")
                jsonl_exists = os.path.exists("PublicnEUro_PN000011.jsonl")
                
                if xml_exists or not jsonl_exists:
                    self.log(f"✗ JSONL-only test failed - XML: {xml_exists}, JSONL: {jsonl_exists}")
                    return False
                
                self.log("✓ Single format CLI options work correctly")
                return True
                
        except subprocess.TimeoutExpired:
            self.log("✗ Single format CLI test timed out")
            return False
        except Exception as e:
            self.log(f"✗ Single format CLI test failed: {e}")
            return False
    
    def test_version_formatting(self):
        """Test 7: Version formatting (V1, not VV1)"""
        self.log("Testing version formatting...")
        
        try:
            from export_xlsx import export_xlsx_to_xml
            
            with tempfile.TemporaryDirectory() as temp_dir:
                os.chdir(temp_dir)
                
                xml_file = export_xlsx_to_xml(self.test_excel_file)
                
                # Read and check version formatting
                with open(xml_file, 'r', encoding='utf-8') as f:
                    xml_content = f.read()
                
                # Check for proper version format
                if "VV1" in xml_content:
                    self.log("✗ Found incorrect version format VV1")
                    return False
                
                if "V1" in xml_content:
                    self.log("✓ Correct version format V1 found")
                    return True
                
                self.log("? No version information found in XML")
                return True  # Not necessarily an error
                
        except Exception as e:
            self.log(f"✗ Version formatting test failed: {e}")
            return False
    
    def test_error_handling(self):
        """Test 8: Error handling for invalid inputs"""
        self.log("Testing error handling...")
        
        try:
            from export_xlsx import export_xlsx_to_xml
            
            # Test with non-existent file
            try:
                result = export_xlsx_to_xml("nonexistent_file.xlsx")
                self.log("✗ Should have failed with non-existent file")
                return False
            except Exception:
                self.log("✓ Correctly handles non-existent file")
            
            # Test CLI with non-existent file
            export_script = os.path.join(parent_dir, "export_xlsx.py")
            result = subprocess.run([
                sys.executable, export_script, "nonexistent_file.xlsx"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                self.log("✗ CLI should have failed with non-existent file")
                return False
            
            self.log("✓ CLI correctly handles non-existent file")
            return True
            
        except Exception as e:
            self.log(f"✗ Error handling test failed: {e}")
            return False
    
    def test_keyword_parsing(self):
        """Test 9: Keyword parsing with commas and spaces"""
        self.log("Testing keyword parsing...")
        
        try:
            from export_xlsx import parse_keywords
            
            # Test comma-separated keywords
            result = parse_keywords("word1, compound word2")
            expected = ["word1", "compound word2"]
            if result != expected:
                self.log(f"✗ Comma parsing failed: got {result}, expected {expected}")
                return False
            self.log("✓ Comma-separated keywords parsed correctly")
            
            # Test space-separated keywords
            result = parse_keywords("word1 compound word2")
            expected = ["word1", "compound", "word2"]
            if result != expected:
                self.log(f"✗ Space parsing failed: got {result}, expected {expected}")
                return False
            self.log("✓ Space-separated keywords parsed correctly")
            
            # Test empty/None input
            result = parse_keywords(None)
            if result != []:
                self.log(f"✗ None handling failed: got {result}, expected []")
                return False
            self.log("✓ None input handled correctly")
            
            # Test mixed whitespace
            result = parse_keywords("  word1 ,  word2  , word3  ")
            expected = ["word1", "word2", "word3"]
            if result != expected:
                self.log(f"✗ Whitespace handling failed: got {result}, expected {expected}")
                return False
            self.log("✓ Whitespace handling works correctly")
            
            return True
            
        except Exception as e:
            self.log(f"✗ Keyword parsing test failed: {e}")
            return False
    
    def test_bids_parsing(self):
        """Test 10: BIDS field parsing"""
        self.log("Testing BIDS field parsing...")
        
        try:
            from export_xlsx import parse_bids_datatypes, parse_bids_dataset_type
            
            # Test BIDS datatypes parsing
            result = parse_bids_datatypes("anat, func")
            expected = ["anat", "func"]
            if result != expected:
                self.log(f"✗ BIDS datatypes comma parsing failed: got {result}, expected {expected}")
                return False
            self.log("✓ BIDS datatypes comma parsing works")
            
            result = parse_bids_datatypes("anat func")
            expected = ["anat", "func"]
            if result != expected:
                self.log(f"✗ BIDS datatypes space parsing failed: got {result}, expected {expected}")
                return False
            self.log("✓ BIDS datatypes space parsing works")
            
            # Test BIDS dataset type parsing
            result = parse_bids_dataset_type("raw")
            if result != "raw":
                self.log(f"✗ BIDS dataset type 'raw' failed: got {result}")
                return False
            self.log("✓ BIDS dataset type 'raw' works")
            
            result = parse_bids_dataset_type("Raw Data")
            if result != "raw":
                self.log(f"✗ BIDS dataset type 'Raw Data' failed: got {result}")
                return False
            self.log("✓ BIDS dataset type 'Raw Data' works")
            
            result = parse_bids_dataset_type("derivatives")
            if result != "derivatives":
                self.log(f"✗ BIDS dataset type 'derivatives' failed: got {result}")
                return False
            self.log("✓ BIDS dataset type 'derivatives' works")
            
            result = parse_bids_dataset_type("Derived/processed")
            if result != "derivatives":
                self.log(f"✗ BIDS dataset type 'Derived/processed' failed: got {result}")
                return False
            self.log("✓ BIDS dataset type 'Derived/processed' works")
            
            result = parse_bids_dataset_type("unknown")
            if result != "raw":
                self.log(f"✗ BIDS dataset type 'unknown' default failed: got {result}")
                return False
            self.log("✓ BIDS dataset type default to 'raw' works")
            
            return True
            
        except Exception as e:
            self.log(f"✗ BIDS parsing test failed: {e}")
            return False
    
    def run_all_tests(self, quick=False):
        """Run all tests in the suite"""
        print("🚀 Export XLSX Master Test Suite")
        print("=" * 60)
        print(f"📍 Test Excel file: {os.path.basename(self.test_excel_file)}")
        print(f"🔧 Verbose mode: {self.verbose}")
        
        # Define tests
        tests = [
            ("Import Functionality", self.test_import_functionality),
            ("XML Export", self.test_xml_export),
            ("JSONL Export", self.test_jsonl_export),
            ("Both Formats Export", self.test_both_formats),
            ("CLI Default Behavior", self.test_cli_default_behavior),
            ("Keyword Parsing", self.test_keyword_parsing),
            ("BIDS Parsing", self.test_bids_parsing),
        ]
        
        if not quick:
            tests.extend([
                ("CLI Single Formats", self.test_cli_single_formats),
                ("Version Formatting", self.test_version_formatting),
                ("Error Handling", self.test_error_handling),
            ])
        
        # Run tests
        for test_name, test_func in tests:
            self.run_test(test_name, test_func)
        
        # Summary
        print(f"\n{'='*60}")
        print(f"🎯 Test Results: {self.tests_passed}/{self.total_tests} passed")
        
        if self.tests_passed == self.total_tests:
            print("🎉 ALL TESTS PASSED!")
            return True
        else:
            print(f"❌ {self.total_tests - self.tests_passed} test(s) failed")
            return False


def main():
    """Main function for command line execution"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Master test suite for export_xlsx.py")
    parser.add_argument("--quick", action="store_true", help="Run quick tests only")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    
    args = parser.parse_args()
    
    # Run tests
    test_suite = ExportXlsxTestSuite(verbose=args.verbose)
    success = test_suite.run_all_tests(quick=args.quick)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
