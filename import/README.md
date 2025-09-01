# PublicnEUro Data Import Utilities

This directory contains utilities for processing and managing PublicnEUro dataset metadata files.

## Main Utilities

### `export_xlsx.py`

Converts Excel metadata files to XML (CrossRef format) and/or JSONL (data catalog format) with intelligent field parsing and validation.

#### Python API Usage

```python
# Import functions
from export_xlsx import export_xlsx_to_xml, export_xlsx_to_jsonl, export_xlsx_to_both

# Export to XML only (CrossRef format)
xml_file = export_xlsx_to_xml('input.xlsx', 'output.xml')

# Export to JSONL only (data catalog format)
jsonl_file = export_xlsx_to_jsonl('input.xlsx', 'output.jsonl')

# Export to both formats
xml_file, jsonl_file = export_xlsx_to_both('input.xlsx')
```

#### Command Line Usage

```bash
# Generate both XML and JSONL (DEFAULT BEHAVIOR)
python export_xlsx.py input.xlsx

# Generate specific format only
python export_xlsx.py input.xlsx xml              # XML only
python export_xlsx.py input.xlsx jsonl            # JSONL only

# With custom output paths
python export_xlsx.py input.xlsx xml custom.xml
python export_xlsx.py input.xlsx jsonl custom.jsonl
```

### `find_catalogue_set_file.py`

Searches for dataset files in the catalog directory structure. Finds JSON files containing `"type": "dataset"` within the metadata hierarchy.

#### Import and Usage

```python
# Import function
from find_catalogue_set_file import find_catalogue_set_file as fs

# Search for datasets by PN number pattern
results = fs("PN000001*/V1")                    # Search PN000001 datasets
results = fs("metadata/PN000011*/V1")           # With metadata prefix
results = fs("PN000002*/V1")                    # Any PN number works

# Access results
for key, info in results.items():
    print(f"Dataset: {info['directory']}")
    print(f"Version: {info['version']}")
    print(f"Path: {info['relative_path']}")
    print(f"Name: {info['metadata']['name']}")
```

#### CLI Usage

```bash
# Run with default pattern (PN000011*/V1)
python find_catalogue_set_file.py

# The function is primarily designed for Python import usage
```

#### Return Structure

The function returns a dictionary with dataset information:

```python
{
    'PN000001OpenNeuroPETPhantoms_V1': {
        'path': 'full/path/to/dataset.json',
        'relative_path': 'metadata/PN000001.../dataset.json',
        'directory': 'PN000001 OpenNeuroPET Phantoms',
        'version': 'V1',
        'metadata': {  # Full dataset metadata
            'type': 'dataset',
            'name': 'OpenNeuroPET Phantoms',
            'dataset_id': 'PN000001 OpenNeuroPET Phantoms',
            'authors': [...],
            # ... additional metadata
        }
    }
}
```

### `file_metadata_utils.py`

Processes dataset metadata and file listings into comprehensive catalog entries. Combines file scanning functionality with dataset metadata to create complete JSONL catalogs.

#### Python API

```python
# Import functions
from file_metadata_utils import get_file_info, process_file_metadata

# Method 1: Direct directory scanning
# Automatically scans directory for BIDS-compliant files
output_file = process_file_metadata(
    dataset_jsonl='PublicnEUro_test.jsonl',
    file_list_source='/path/to/dataset/directory',  # Directory to scan
    source_name='PublicnEUro',
    agent_name='DataProcessor'
)

# Method 2: Using pre-generated file list
# First generate file list, then process
file_list = get_file_info('/path/to/dataset', save_to_file=True, output_file='my_files.jsonl')
output_file = process_file_metadata(
    dataset_jsonl='PublicnEUro_test.jsonl', 
    file_list_source='my_files.jsonl',  # Pre-generated JSONL file
    source_name='PublicnEUro',
    agent_name='DataProcessor'
)

# Method 3: Using file info array directly
file_info = get_file_info('/path/to/dataset')  # Returns list of dicts
output_file = process_file_metadata(
    dataset_jsonl='PublicnEUro_test.jsonl',
    file_list_source=file_info,  # Direct list of file info dictionaries
    source_name='PublicnEUro', 
    agent_name='DataProcessor'
)
```

#### Key Features

- **Three Input Methods**:
  - **Directory Path**: Automatically scans directory for BIDS files
  - **File List JSONL**: Uses pre-generated file list from `get_file_info()`
  - **File Info Array**: Direct list of file information dictionaries
- **BIDS Compliance**: Automatically detects BIDS file types (.json, .nii.gz, .tsv, plain README, etc.)
- **Metadata Integration**: Combines dataset metadata with individual file information
- **Legacy Support**: Includes `listjl2filetype()` for backward compatibility

## Supported Formats

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

## Features

- **Default Both Formats**: Automatically generates both XML and JSONL
- **Enhanced Keyword Parsing**: Smart parsing with comma vs space detection
  - `'word1, compound word2'` → `['word1', 'compound word2']`
  - `'word1 compound word2'` → `['word1', 'compound', 'word2']`
- **Robust BIDS Field Processing**:
  - **BIDS Data Types**: Supports comma or space separation (`'anat, func'` or `'anat func'`)
  - **BIDS Dataset Type**: Validates and enforces 'raw' or 'derivatives' values
- **Path Independence**: All files can be run from any directory
- **Automatic Path Detection**: Scripts automatically find required files
- **Error Handling**: Graceful handling of missing files or import errors
- **Cross-Platform**: Works on Windows, Linux, and macOS
- **Version Formatting**: Consistent V+number formatting (fixes VV1 → V1)
- **DOI Processing**: Handles various DOI input formats
- **Pattern Matching**: Flexible PN number pattern support

## Testing

### Master Test Suite

The comprehensive test suite validates all functionality using `test/PublicnEUro_test.xlsx`.

#### Running Tests

```bash
cd test
python test_master_export_xlsx.py                 # Run all tests
python test_master_export_xlsx.py --quick         # Quick tests only  
python test_master_export_xlsx.py --verbose       # Detailed output
```

#### Test Coverage

The master test suite covers:

- ✅ Module import functionality
- ✅ XML export (CrossRef format validation)
- ✅ JSONL export (data catalog format validation)
- ✅ Both formats export
- ✅ CLI default behavior (both formats)
- ✅ Enhanced keyword parsing (comma vs space detection)
- ✅ BIDS field processing (datatypes and dataset type validation)
- ✅ CLI single format options (xml/jsonl)
- ✅ Version formatting (V1, not VV1)
- ✅ Error handling for invalid inputs

#### Available Test Files

- `test_master_export_xlsx.py` - Comprehensive test suite
- `test_find_catalogue.py` - Tests for catalog search functionality  
- `test_file_metadata_utils.py` - Tests for file metadata processing
- `compare_xml_files.py` - XML comparison utilities

## File Structure

```text
import/
├── export_xlsx.py                    # Main Excel to XML/JSONL utility
├── find_catalogue_set_file.py        # Catalog dataset search utility
├── file_metadata_utils.py            # File scanning and metadata processing
├── README.md                         # This documentation
└── test/                            # Test directory
    ├── PublicnEUro_test.xlsx         # Test Excel file
    ├── PublicnEUro_test.jsonl        # Test dataset JSONL
    ├── fake_files/                   # Test file structure
    ├── test_master_export_xlsx.py   # Comprehensive test suite
    ├── test_find_catalogue.py       # Catalog search tests
    ├── test_file_metadata_utils.py  # File metadata processing tests
    └── compare_xml_files.py         # XML comparison utilities
```

## Examples

### Complete Workflow Example

```python
# Import utilities
from export_xlsx import export_xlsx_to_both
from find_catalogue_set_file import find_catalogue_set_file as fs

# 1. Find existing datasets in catalog
results = fs("PN000001*/V1")
print(f"Found {len(results)} datasets")

# 2. Convert new Excel file to both formats
xml_file, jsonl_file = export_xlsx_to_both('new_dataset.xlsx')
print(f"Generated: {xml_file}, {jsonl_file}")
```

### Batch Processing Example

```python
import os
from export_xlsx import export_xlsx_to_both

# Process all Excel files in a directory
excel_dir = "data_import"
for file in os.listdir(excel_dir):
    if file.endswith('.xlsx'):
        excel_path = os.path.join(excel_dir, file)
        xml_file, jsonl_file = export_xlsx_to_both(excel_path)
        print(f"Processed: {file} → {os.path.basename(xml_file)}, {os.path.basename(jsonl_file)}")
```

### File Metadata Processing Example

```python
from export_xlsx import export_xlsx_to_jsonl
from file_metadata_utils import get_file_info, process_file_metadata

# 1. Convert Excel to JSONL dataset metadata
dataset_jsonl = export_xlsx_to_jsonl('dataset_metadata.xlsx')

# Method A: Direct directory scanning (most common)
catalog_file = process_file_metadata(
    dataset_jsonl=dataset_jsonl,
    file_list_source='/path/to/dataset/files',  # Directory to scan
    source_name='PublicnEUro',
    agent_name='DataCatalogBot'
)

# Method B: Two-step process with file list generation
# Step 1: Generate file list
file_list = get_file_info('/path/to/dataset/files', save_to_file=True, output_file='files.jsonl')
# Step 2: Process with pre-generated list
catalog_file = process_file_metadata(
    dataset_jsonl=dataset_jsonl,
    file_list_source='files.jsonl',  # Pre-generated file list
    source_name='PublicnEUro',
    agent_name='DataCatalogBot'
)

print(f"Generated comprehensive catalog: {catalog_file}")
```
