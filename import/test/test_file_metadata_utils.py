#!/usr/bin/env python3
"""
Test suite for file_metadata_utils.py

Tests the functionality of get_file_info() and process_file_metadata()
using fake test files and the PublicnEUro_test.jsonl dataset.
"""

import sys
import os
import tempfile
import json

# Add parent directory to path for imports
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)
sys.path.insert(0, parent_dir)


class FileMetadataTestSuite:
    """Test suite for file metadata processing utilities"""
    
    def __init__(self, verbose=False):
        self.verbose = verbose
        self.tests_passed = 0
        self.total_tests = 0
        self.test_dir = script_dir
        self.fake_files_dir = os.path.join(self.test_dir, "fake_files")
        self.test_dataset_jsonl = os.path.join(self.test_dir, "PublicnEUro_test.jsonl")
        
        # Verify test files exist
        if not os.path.exists(self.fake_files_dir):
            print(f"❌ Test fake files directory not found: {self.fake_files_dir}")
            sys.exit(1)
            
        if not os.path.exists(self.test_dataset_jsonl):
            print(f"❌ Test dataset JSONL not found: {self.test_dataset_jsonl}")
            sys.exit(1)
    
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
                print("   ✅ PASSED")
                self.tests_passed += 1
            else:
                print("   ❌ FAILED")
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
    
    def test_get_file_info_function(self):
        """Test 1: get_file_info function"""
        self.log("Testing get_file_info function...")
        
        try:
            from file_metadata_utils import get_file_info
            
            # Test scanning the fake files directory
            file_info = get_file_info(self.fake_files_dir, save_to_file=False)
            
            if not isinstance(file_info, list):
                self.log(f"✗ Expected list, got {type(file_info)}")
                return False
            
            if len(file_info) == 0:
                self.log("✗ No files found in fake_files directory")
                return False
            
            self.log(f"✓ Found {len(file_info)} files/directories")
            
            # Check that we have expected file types 
            # README (plain text) should be included, README.yml should be excluded
            # dataset_description.json and participants.tsv are covered by their extensions
            paths = [item['path'] for item in file_info]
            expected_files = ['dataset_description.json', 'participants.tsv', 'README']
            excluded_files = ['README.yml']  # Files that should NOT be included (not BIDS standard)
            
            for expected in expected_files:
                if not any(expected in path for path in paths):
                    self.log(f"✗ Expected file not found: {expected}")
                    return False
            
            for excluded in excluded_files:
                if any(excluded in path for path in paths):
                    self.log(f"✗ Excluded file incorrectly included: {excluded}")
                    return False
            
            self.log("✓ Expected files found and excluded files properly filtered")
            
            # Verify structure
            for item in file_info:
                if 'path' not in item or 'contentbytesize' not in item:
                    self.log(f"✗ Invalid file info structure: {item}")
                    return False
            
            self.log("✓ File info structure is correct")
            return True
            
        except Exception as e:
            self.log(f"✗ get_file_info test failed: {e}")
            return False
    
    def test_get_file_info_save_to_file(self):
        """Test 2: get_file_info with file saving"""
        self.log("Testing get_file_info with file saving...")
        
        try:
            from file_metadata_utils import get_file_info
            
            # Use temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as tmp_file:
                temp_path = tmp_file.name
            
            try:
                # Test saving to file
                file_info = get_file_info(
                    self.fake_files_dir, 
                    save_to_file=True, 
                    output_file=os.path.basename(temp_path)
                )
                
                # Check that file was created
                if not os.path.exists(os.path.basename(temp_path)):
                    self.log("✗ Output file was not created")
                    return False
                
                # Read and verify file contents
                with open(os.path.basename(temp_path), 'r') as f:
                    lines = f.readlines()
                
                if len(lines) != len(file_info):
                    self.log(f"✗ File has {len(lines)} lines, expected {len(file_info)}")
                    return False
                
                # Verify each line is valid JSON
                for i, line in enumerate(lines):
                    try:
                        json.loads(line.strip())
                    except json.JSONDecodeError as e:
                        self.log(f"✗ Invalid JSON on line {i+1}: {e}")
                        return False
                
                self.log("✓ File saved and contents are valid")
                return True
                
            finally:
                # Cleanup
                for file_to_remove in [temp_path, os.path.basename(temp_path)]:
                    if os.path.exists(file_to_remove):
                        os.remove(file_to_remove)
                        
        except Exception as e:
            self.log(f"✗ File saving test failed: {e}")
            return False
    
    def test_process_file_metadata_with_directory(self):
        """Test 3: process_file_metadata with directory input"""
        self.log("Testing process_file_metadata with directory...")
        
        try:
            from file_metadata_utils import process_file_metadata
            
            # Use temporary output file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as tmp_file:
                temp_output = tmp_file.name
            
            try:
                # Process with directory input
                output_file = process_file_metadata(
                    self.test_dataset_jsonl,
                    self.fake_files_dir,
                    source_name='test',
                    agent_name='test',
                    output_file=temp_output
                )
                
                if not os.path.exists(output_file):
                    self.log(f"✗ Output file not created: {output_file}")
                    return False
                
                # Read and verify output
                with open(output_file, 'r') as f:
                    lines = f.readlines()
                
                if len(lines) < 2:  # Should have dataset + at least one file
                    self.log(f"✗ Expected at least 2 lines, got {len(lines)}")
                    return False
                
                # Check first line is dataset
                first_line = json.loads(lines[0].strip())
                if first_line.get('type') != 'dataset':
                    self.log("✗ First line should be dataset type")
                    return False
                
                # Check subsequent lines are files
                file_count = 0
                for line in lines[1:]:
                    item = json.loads(line.strip())
                    if item.get('type') == 'file':
                        file_count += 1
                        
                        # Verify required fields
                        required_fields = ['dataset_id', 'dataset_version', 'path', 'contentbytesize']
                        for field in required_fields:
                            if field not in item:
                                self.log(f"✗ Missing field '{field}' in file item")
                                return False
                
                if file_count == 0:
                    self.log("✗ No file items found")
                    return False
                
                self.log(f"✓ Generated output with dataset + {file_count} files")
                return True
                
            finally:
                if os.path.exists(temp_output):
                    os.remove(temp_output)
                    
        except Exception as e:
            self.log(f"✗ Directory processing test failed: {e}")
            return False
    
    def test_process_file_metadata_with_file_list(self):
        """Test 4: process_file_metadata with generated file list"""
        self.log("Testing process_file_metadata with file list...")
        
        try:
            from file_metadata_utils import get_file_info, process_file_metadata
            
            # First generate a file list
            with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as tmp_list:
                temp_list_file = tmp_list.name
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as tmp_output:
                temp_output_file = tmp_output.name
            
            try:
                # Generate file list
                file_info = get_file_info(
                    self.fake_files_dir,
                    save_to_file=True,
                    output_file=os.path.basename(temp_list_file)
                )
                
                # Use the generated file list
                output_file = process_file_metadata(
                    self.test_dataset_jsonl,
                    os.path.basename(temp_list_file),
                    source_name='test',
                    agent_name='test',
                    output_file=temp_output_file
                )
                
                if not os.path.exists(output_file):
                    self.log(f"✗ Output file not created: {output_file}")
                    return False
                
                # Verify output structure
                with open(output_file, 'r') as f:
                    lines = f.readlines()
                
                # Should have same number of files as the generated list + 1 for dataset
                expected_lines = len(file_info) + 1
                if len(lines) != expected_lines:
                    self.log(f"✗ Expected {expected_lines} lines, got {len(lines)}")
                    return False
                
                self.log(f"✓ File list processing successful with {len(lines)} lines")
                return True
                
            finally:
                # Cleanup
                for file_to_remove in [temp_list_file, temp_output_file, os.path.basename(temp_list_file)]:
                    if os.path.exists(file_to_remove):
                        os.remove(file_to_remove)
                        
        except Exception as e:
            self.log(f"✗ File list processing test failed: {e}")
            return False
    
    def test_legacy_function(self):
        """Test 5: Legacy listjl2filetype function"""
        self.log("Testing legacy listjl2filetype function...")
        
        try:
            from file_metadata_utils import listjl2filetype, get_file_info
            
            # Generate a temporary file list
            with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as tmp_list:
                temp_list_file = tmp_list.name
            
            try:
                # Generate file list first
                get_file_info(
                    self.fake_files_dir,
                    save_to_file=True,
                    output_file=os.path.basename(temp_list_file)
                )
                
                # Use legacy function
                output_file = listjl2filetype(
                    self.test_dataset_jsonl,
                    os.path.basename(temp_list_file),
                    'test',
                    'test'
                )
                
                if not os.path.exists(output_file):
                    self.log(f"✗ Legacy function output not created: {output_file}")
                    return False
                
                # Basic validation
                with open(output_file, 'r') as f:
                    lines = f.readlines()
                
                if len(lines) < 2:
                    self.log("✗ Legacy function output too short")
                    return False
                
                self.log("✓ Legacy function works correctly")
                
                # Cleanup output
                if os.path.exists(output_file):
                    os.remove(output_file)
                
                return True
                
            finally:
                # Cleanup
                for file_to_remove in [temp_list_file, os.path.basename(temp_list_file)]:
                    if os.path.exists(file_to_remove):
                        os.remove(file_to_remove)
                        
        except Exception as e:
            self.log(f"✗ Legacy function test failed: {e}")
            return False
    
    def run_all_tests(self, quick=False):
        """Run all tests in the suite"""
        print("🚀 File Metadata Utils Test Suite")
        print("=" * 60)
        print(f"📁 Test directory: {self.test_dir}")
        print(f"📄 Dataset JSONL: {os.path.basename(self.test_dataset_jsonl)}")
        print(f"📂 Fake files: {os.path.basename(self.fake_files_dir)}")
        print(f"🔧 Verbose mode: {self.verbose}")
        
        # Define tests
        tests = [
            ("Get File Info Function", self.test_get_file_info_function),
            ("Get File Info Save to File", self.test_get_file_info_save_to_file),
            ("Process with Directory", self.test_process_file_metadata_with_directory),
            ("Process with File List", self.test_process_file_metadata_with_file_list),
            ("Legacy Function", self.test_legacy_function),
        ]
        
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
    
    parser = argparse.ArgumentParser(description="Test suite for file_metadata_utils.py")
    parser.add_argument("--quick", action="store_true", help="Run quick tests only")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    
    args = parser.parse_args()
    
    # Run tests
    test_suite = FileMetadataTestSuite(verbose=args.verbose)
    success = test_suite.run_all_tests(quick=args.quick)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
