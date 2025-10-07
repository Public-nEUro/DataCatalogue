# PublicnEUro Data Processing Tools

This directory contains three main utility modules for processing dataset metadata and files in the PublicnEUro data catalog.

**Complete Workflow Overview:**

1. **Convert** Excel metadata to XML/JSONL formats (`export_xlsx.py`)
2. **Generate** file catalog from data directory (`file_metadata_utils.py`)
3. **Validate & Import** to datalad catalog (manual `datalad catalog-validate` + `datalad catalog-add`)
4. **Find & Organize** datasets in catalog (`find_catalogue_set_file.py`)

*Note: The CLI tool (`process_dataset.py`) automates all steps including datalad operations.*

## Quick Start

### Complete Workflow (Recommended)

For the full dataset processing pipeline, use the CLI tool:

```bash
# Complete workflow: Excel → XML/JSONL → File catalog → Datalad import → Catalog integration
python process_dataset.py metadata.xlsx /path/to/data/ "PN000011*/V1"

# With custom source and agent names
python process_dataset.py metadata.xlsx /path/to/data/ "PN000011*/V1" --source MySource --agent MyAgent
```

This CLI tool automates the complete workflow including datalad catalog validation and import.

### Individual Tool Usage

```python
# 1. Convert Excel metadata to XML/JSONL
from export_xlsx import export_xlsx_to_both
xml_file, jsonl_file = export_xlsx_to_both('dataset.xlsx')

# 2. Generate file catalog
from file_metadata_utils import process_file_metadata
catalog = process_file_metadata(jsonl_file, '/path/to/data/', 'source', 'agent')

# 3. Validate and import to datalad catalog (manual datalad commands)
# datalad catalog-validate --metadata catalog_file
# datalad catalog-add --catalog ../DataCatalogue --metadata catalog_file

# 4. Find datasets in catalog and optionally reorder children
from find_catalogue_set_file import find_catalogue_set_file
results = find_catalogue_set_file("PN000011*/V1", reorder_children=True)
```

**Note:** Steps 3 (datalad validation/import) is handled automatically by the CLI tool but requires manual execution when using individual tools.

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

Check the user information from the Excel file, this is the reason the export csan fail.

### 📁 file_metadata_utils.py - File Catalog Generator

Creates comprehensive file listings and metadata catalogs.

**Key Functions:**

- `process_file_metadata(dataset_jsonl, /path_to_dataset/, source_name, agent_name)` - Create catalog adding files from dataset folder

  Alternatively do:
- `get_file_info(directory_path)` - Scan directory for files and create a file list
- `process_file_metadata(dataset_jsonl, file_source, source_name, agent_name)` - Create catalog mergng the file list

**Features:**

- BIDS-compliant file recognition
- Excludes code directories automatically
- Flexible input (directories, file lists, or data)
- Metadata integration

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

Child ordering follows BIDS conventions: `source` → `code` → `files` → `sub-*` (numeric) → `sub-*` (alpha) → `others`

## Command Line Usage

```bash
# Complete workflow pipeline
python process_dataset.py metadata.xlsx /path/to/data/ "PN000011*/V1"
python process_dataset.py metadata.xlsx /path/to/data/ "PN000011*/V1" --source CustomSource --agent CustomAgent

# Individual tool usage
# Export Excel to both formats
python export_xlsx.py dataset_metadata.xlsx

# Generate file catalog (requires previous step)
python -c "from file_metadata_utils import process_file_metadata; process_file_metadata('dataset.jsonl', '/path/to/data/', 'source', 'agent')"

# Manual datalad catalog operations (required between steps 2 and 4)
datalad catalog-validate --metadata catalog_file.jsonl
datalad catalog-add --catalog ../DataCatalogue --metadata catalog_file.jsonl

# Find datasets with interactive reordering prompt
python find_catalogue_set_file.py

# Find specific dataset and reorder programmatically
python -c "from find_catalogue_set_file import find_catalogue_set_file; find_catalogue_set_file('PN000011*/V1', reorder_children=True)"

# Run from test directory
cd test
python simple_test.py
python test_process_dataset_cli.py  # Test the new CLI
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
python test_process_dataset_cli.py   # Test complete workflow CLI
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
