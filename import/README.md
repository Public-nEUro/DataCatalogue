# PublicnEUro Data Processing Tools

This directory contains three main utility modules for processing dataset metadata and files in the PublicnEUro data catalog.

## Quick Start

```python
# 1. Convert Excel metadata to XML/JSONL
from export_xlsx import export_xlsx_to_both
xml_file, jsonl_file = export_xlsx_to_both('dataset.xlsx')

# 2. Generate file catalog
from file_metadata_utils import process_file_metadata
catalog = process_file_metadata(jsonl_file, '/path/to/data/', 'source', 'agent')

# 3. Find datasets in catalog and optionally reorder children
from find_catalogue_set_file import find_catalogue_set_file
results = find_catalogue_set_file("PN000011*/V1", reorder_children=True)
```

## Tools Overview

### 🔧 export_xlsx.py - Excel to XML/JSONL Converter

Converts Excel metadata files to XML (CrossRef) and JSONL (web catalog) formats.

**Key Functions:**

- `export_xlsx_to_both(excel_file)` - Export to both formats (recommended)
- `export_xlsx_to_xml(excel_file)` - Export to XML only
- `export_xlsx_to_jsonl(excel_file)` - Export to JSONL only

**Features:**

- DUA extraction from Excel cells D3/B1
- 5-category validation system
- Empty value filtering
- BIDS dataset support
- Line break preservation for web display

**Excel Requirements:**

Your Excel file needs these sheets: `dataset_info`, `participants_info`, `DUA`, `authors`, `funding`, `publications`

### 📁 file_metadata_utils.py - File Catalog Generator

Creates comprehensive file listings and metadata catalogs.

**Key Functions:**

- `get_file_info(directory_path)` - Scan directory for files
- `process_file_metadata(dataset_jsonl, file_source, source_name, agent_name)` - Create catalog

**Features:**

- BIDS-compliant file recognition
- Excludes code directories automatically
- Flexible input (directories, file lists, or data)
- Metadata integration

**Related Tools:**

For reordering dataset children after file processing, use `find_catalogue_set_file.py`:

```python
# Reorder children in catalog JSON file
from find_catalogue_set_file import reorder_dataset_children
reorder_dataset_children('/path/to/dataset.json')

# Find datasets and auto-reorder children  
from find_catalogue_set_file import find_catalogue_set_file
results = find_catalogue_set_file("PN*/V*", reorder_children=True)
```

Child ordering follows BIDS conventions: `source` → `code` → `files` → `sub-*` (numeric) → `sub-*` (alpha) → `others`

### 🔍 find_catalogue_set_file.py - Dataset Locator & Organizer

Finds dataset files in catalog directory structures and optionally reorders dataset children.

**Key Functions:**

- `find_catalogue_set_file(pattern, reorder_children=None)` - Find datasets by pattern with optional reordering
- `find_jsonl_dataset(folder)` - Find dataset files in folder
- `reorder_dataset_children(file_path)` - Reorder children in a dataset file
- `sort_children(children)` - Sort dataset children according to rules

**Pattern Examples:**

- `"PN000011*/V1"` - Specific dataset and version
- `"PN000001*"` - All versions of dataset
- `"metadata/PN000003*"` - Search in metadata directory

**Reordering Features:**

The tool can automatically reorder dataset children according to these rules:

1. **"source"** directory first
2. **"code"** directory second  
3. All **files** (`"type": "file"`)
4. **"sub-*"** directories sorted numerically (sub-01, sub-02...) or alphabetically
5. Other directories last

**Reordering Options:**

- `reorder_children=None` - Interactive prompt (default)
- `reorder_children=True` - Automatic reordering
- `reorder_children=False` - No reordering

```python
# Interactive mode - will prompt user
results = find_catalogue_set_file('PN*/V*')

# Force reordering without prompt  
results = find_catalogue_set_file('PN*/V*', reorder_children=True)

# Skip reordering without prompt
results = find_catalogue_set_file('PN*/V*', reorder_children=False)
```

## Complete Workflow Example

```python
#!/usr/bin/env python3
"""Complete dataset processing pipeline"""

from export_xlsx import export_xlsx_to_both
from file_metadata_utils import process_file_metadata
from find_catalogue_set_file import find_catalogue_set_file

def process_dataset(excel_file, data_directory, dataset_pattern):
    """Process complete dataset from Excel to catalog"""
    
    # Step 1: Convert Excel metadata
    xml_file, jsonl_file = export_xlsx_to_both(excel_file)
    
    # Step 2: Generate file catalog
    catalog_file = process_file_metadata(
        dataset_jsonl=jsonl_file,
        file_list_source=data_directory,
        source_name='Local_Processing',
        agent_name='Pipeline'
    )
    
    # Step 3: Verify in catalog and reorder children
    results = find_catalogue_set_file(dataset_pattern, reorder_children=True)
    
    return {
        'xml': xml_file,
        'jsonl': jsonl_file,
        'catalog': catalog_file,
        'found': list(results.keys())
    }

# Usage
result = process_dataset(
    excel_file='PN000011_metadata.xlsx',
    data_directory='/data/PN000011/',
    dataset_pattern='PN000011*/V1'
)
print(f"Processing complete: {result}")
```

## Command Line Usage

```bash
# Export Excel to both formats
python export_xlsx.py dataset_metadata.xlsx

# Find datasets with interactive reordering prompt
python find_catalogue_set_file.py

# Find specific dataset and reorder programmatically
python -c "from find_catalogue_set_file import find_catalogue_set_file; find_catalogue_set_file('PN000011*/V1', reorder_children=True)"

# Run from test directory
cd test
python simple_test.py
```

## File Structure Requirements

```text
your_dataset/
├── metadata.xlsx          # Excel metadata file
├── sub-01/               # BIDS subject directories
│   ├── anat/
│   └── func/
├── sub-02/
└── derivatives/          # Processed data
```

## Validation and Error Handling

The tools provide comprehensive validation:

- **dataset_info**: Title, description, DOI validation
- **participants**: Sample size, demographics
- **dua**: Terms and restrictions
- **authors**: Author information
- **data_curators**: Curator details

Use `skip_validation=True` for testing purposes.

## Testing

Comprehensive test suite available in `/test` directory:

```bash
cd test
python test_master_export_xlsx.py    # Full test suite
python simple_test.py                # Basic functionality
python check_dua.py                  # DUA content verification
```

## Requirements

- Python 3.7+
- pandas, openpyxl
- Properly formatted Excel files
- Read/write access to data directories

## Troubleshooting

**Common Issues:**

1. **Import errors**: Ensure files are in Python path
2. **Excel format**: Check required sheets exist
3. **File permissions**: Verify directory access
4. **Empty values**: Use validation feedback to fix metadata
5. **Dataset reordering**: Ensure dataset files are writable and valid JSON

**Reordering Notes:**

- Reordering only works on files with `"type": "dataset"`
- Original file is overwritten - backup important files first
- Invalid JSON files are skipped with warning messages
- Use `reorder_children=False` to disable reordering

**Getting Help:**

- Check `/test/README.md` for detailed testing info
- Review function docstrings for parameter details
- Use `verbose=True` for detailed logging
