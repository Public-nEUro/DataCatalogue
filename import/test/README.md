# Test Suite for Export Functions

This directory contains all test files for the export functionality.

## Test Files

### Main Test Suites

- **`test_master_export_xlsx.py`** - Comprehensive test suite for all export_xlsx.py functionality
- **`test_file_metadata_utils.py`** - Tests for file metadata utilities
- **`test_find_catalogue.py`** - Tests for catalogue finding functionality
- **`test_pattern_matching.py`** - Tests for pattern matching

### Simple Tests

- **`simple_test.py`** - Basic test for export functionality
- **`test_export_both.py`** - Test for exporting both XML and JSONL formats

### Verification Scripts

- **`check_dua.py`** - Verify DUA content in exported JSONL
- **`check_test_data.py`** - Check validation functionality and metadata parsing
- **`compare_xml_files.py`** - Compare XML file outputs

### Test Data

- **`PublicnEUro_test.xlsx`** - Test Excel file with sample data
- **`PublicnEUro_test.jsonl`** - Expected JSONL output
- **`PublicnEUro_test.xml`** - Expected XML output
- **`fake_files/`** - Directory with fake files for testing

## Running Tests

To run the comprehensive test suite:

```bash
cd test
python test_master_export_xlsx.py
```

To run individual tests:

```bash
python simple_test.py
python check_dua.py
python check_test_data.py
```

## Notes

All test files have been configured to properly import from the parent directory using:

```python
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
```
