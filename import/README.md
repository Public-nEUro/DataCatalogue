# Export XLSX Utility

This directory contains the `export_xlsx.py` utility and related test/demo files for converting Excel metadata files to XML and JSONL formats for CrossRef submission and data catalog integration.

## Main Function

### `export_xlsx.py`

The main utility that converts Excel metadata files to XML and/or JSONL formats. This combines the functionality of the original `xlsx2xml.py`, `xml_dict.json`, and `xlsx2jsonl.py` into a single, self-contained module.

**Usage:**

```python
# As imported functions
from export_xlsx import export_xlsx_to_xml, export_xlsx_to_jsonl, export_xlsx_to_both

# Export to XML only
xml_file = export_xlsx_to_xml('input.xlsx', 'output.xml')

# Export to JSONL only  
jsonl_file = export_xlsx_to_jsonl('input.xlsx', 'output.jsonl')

# Export to both formats
xml_file, jsonl_file = export_xlsx_to_both('input.xlsx')

# Command line usage (Default: Both XML and JSONL)
python export_xlsx.py input.xlsx                    # Both formats (default)
python export_xlsx.py input.xlsx xml output.xml     # XML only 
python export_xlsx.py input.xlsx jsonl output.jsonl # JSONL only
```

## Formats Supported

### XML Format
- **Purpose**: CrossRef DOI registration
- **Structure**: CrossRef 5.3.0 schema compliant
- **Features**: DOI formatting, author management, pretty printing
- **Output**: Clean XML with proper namespaces and indentation

### JSONL Format  
- **Purpose**: Data catalog integration
- **Structure**: Single-line JSON with comprehensive metadata
- **Features**: Funding info, publications, participants, detailed metadata
- **Output**: Complete dataset description for catalog systems

## Test Files

All test files are designed to work from any directory and will automatically locate the necessary files and modules.

### `test_export.py`

Basic test of the XML export functionality using the example PN000011 Excel file.

### `test_function.py`

Comprehensive test that demonstrates the full XML export process and shows the generated XML output.

### `test_jsonl_export.py`

Tests the JSONL export functionality and validates the generated JSONL structure.

### `test_both_formats.py`

Tests both XML and JSONL export together, validates both outputs, and checks data consistency between formats.

### `test_metadata_parsing.py`

Comprehensive test of the integrated metadata parsing that shows all extracted fields for both formats.

### `test_doi_extraction.py`

Tests the DOI extraction functionality with various input formats.

### `test_version_formatting.py`

Tests the version formatting functionality to ensure proper V + number format.

### `compare_xml_files.py`

Compares XML files to identify differences between backup and generated files.

### `verify_doi_format.py`

Verifies that the DOI format matches expected output.

## Demo Files

### `demo_export_xlsx.py`

Demonstrates the functionality and features of the export_xlsx module.

### `demo_url_fix.py`

Shows how the version formatting fix works for URL generation.

## Features

- **Path Independence**: All files can be run from any directory
- **Automatic Path Detection**: Scripts automatically find the import directory and data files
- **Error Handling**: Graceful handling of missing files or import errors
- **Cross-Platform**: Works on Windows, Linux, and macOS
- **Dual Format Support**: Generate XML for CrossRef and JSONL for data catalogs
- **Integrated Parsing**: Single metadata extraction for both output formats
- **Version Formatting**: Consistent V+number formatting (fixes VV1 → V1)
- **DOI Processing**: Handles various DOI input formats

## File Structure

```
import/
├── export_xlsx.py                    # Main utility (XML + JSONL)
├── test_export.py                   # Basic XML test
├── test_function.py                 # Comprehensive XML test  
├── test_jsonl_export.py             # JSONL export test
├── test_both_formats.py             # Both formats test
├── test_metadata_parsing.py         # Metadata parsing test
├── test_doi_extraction.py           # DOI extraction test
├── test_version_formatting.py       # Version formatting test
├── compare_xml_files.py             # XML comparison tool
├── verify_doi_format.py            # DOI format verification
├── demo_export_xlsx.py              # Functionality demo
├── demo_url_fix.py                  # URL fix demo
├── README.md                        # This file
└── data_import/
    └── PN000011 Clinical Pediatric MRI.../
        ├── PublicnEUro_PN000011.xlsx
        ├── PublicnEUro_PN000011.xml
        └── PublicNeuro_PN000011_backup.xml
```

## Running Tests

You can run any test file from any directory:

```bash
# Test XML export
python test_export.py

# Test JSONL export  
python test_jsonl_export.py

# Test both formats
python test_both_formats.py

# Test comprehensive metadata parsing
python test_metadata_parsing.py

# From any other directory
python /path/to/import/test_export.py
```

## Integration Summary

The new `export_xlsx.py` successfully integrates:

1. **Original `xlsx2xml.py`**: XML generation for CrossRef
2. **Original `xml_dict.json`**: XML template (now embedded)
3. **Original `xlsx2jsonl.py`**: JSONL generation for catalogs
4. **Shared parsing**: Single metadata extraction for both formats
5. **Enhanced features**: Better error handling, path independence, version fixes

## Key Improvements

1. **Eliminated Redundancy**: Single metadata parsing for both XML and JSONL
2. **Fixed Version Bug**: VV1 → V1 formatting corrected
3. **Added JSONL Support**: Complete data catalog integration
4. **Comprehensive Testing**: Tests for all functionality and edge cases
5. **Better Documentation**: Clear usage examples and feature descriptions
6. **Path Independence**: Works from any directory without configuration

## Command Line Examples

```bash
# Generate both XML and JSONL (NEW DEFAULT)
python export_xlsx.py data.xlsx

# Generate specific format only
python export_xlsx.py data.xlsx xml output.xml
python export_xlsx.py data.xlsx jsonl output.jsonl

# Single format without custom output path
python export_xlsx.py data.xlsx xml      # Creates data.xml
python export_xlsx.py data.xlsx jsonl    # Creates data.jsonl
```

## Summary of Changes (v2.0)

### New Default Behavior

- **Default Output**: Both XML and JSONL files are generated automatically
- **Simplified Usage**: No format flags needed for dual output
- **Streamlined Interface**: Cleaner command line syntax

### Migration Guide

- **Old v1.0**: `python export_xlsx.py input.xlsx --format both`
- **New v2.0**: `python export_xlsx.py input.xlsx` (same result, simpler syntax)
