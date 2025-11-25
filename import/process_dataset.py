#!/usr/bin/env python3
"""
Complete dataset processing pipeline CLI

This script provides a command-line interface for the complete PublicnEUro dataset
processing workflow, from Excel metadata to catalog integration.

Usage Examples:
    # Process dataset using full path to Excel file and data directory
    python process_dataset.py /openneuropet/DataCatalogue/import/data_import/PNC00002 hedit/PN000016 multimodal total-body source data 18F-FDG PET-CT-MRI/PublicnEUro_PN000016.xlsx dpn002/raw/PN000016/source
    
    # Process with pre-generated file list in same directory as Excel
    python process_dataset.py /openneuropet/DataCatalogue/import/data_import/PNC00002 hedit/PN000016 multimodal total-body source data 18F-FDG PET-CT-MRI/PublicnEUro_PN000016.xlsx /openneuropet/DataCatalogue/import/data_import/PNC00002 hedit/PN000016 multimodal total-body source data 18F-FDG PET-CT-MRI/allfiles.jsonl
    
    # Process with custom source and agent names
    python process_dataset.py data_import/PNC00002\ hedy/PN000015\ multimodal\ total-body\ dynamic\ 18F-FDG\ PET-CT-MRI/PublicnEUro_PN000015.xlsx /path/to/data/ --source PublicnEUro --agent "Cyril Pernet"
    
    # Python API usage
    from process_dataset import process_dataset
    result = process_dataset(
        excel_file='data_import/PNC00002 hedy/PN000015 multimodal total-body dynamic 18F-FDG PET-CT-MRI/PublicnEUro_PN000015.xlsx',
        file_list_source='/path/to/dataset/',  # or 'data_import/.../allfiles.jsonl'
        source_name='PublicnEUro',
        agent_name='Cyril Pernet'
    )
"""

import argparse
import sys
import os
import subprocess
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from export_xlsx import export_xlsx_to_both
from file_metadata_utils import process_file_metadata
from find_catalogue_set_file import find_catalogue_set_file
import json
import re


def process_dataset(excel_file, file_list_source, source_name='Local_Processing', agent_name='Pipeline'):
    """
    Process complete dataset from Excel to catalog with datalad import
    
    Args:
        excel_file (str): Path to Excel metadata file
        file_list_source (str): Path to dataset directory or file list JSONL
        source_name (str): Name of the processing source
        agent_name (str): Name of the processing agent
        
    Returns:
        dict: Processing results with file paths and found datasets
        
    Workflow:
        1. Convert Excel metadata to XML/JSONL
        2. Generate file catalog from data directory or file list
        3. Validate and import dataset into datalad catalog
        4. Find and optionally reorder dataset children (auto-detects pattern from JSONL)
    """
    print(f"Starting dataset processing pipeline...")
    print(f"Excel file: {excel_file}")
    print(f"File list source: {file_list_source}")
    
    try:
        # Step 1: Convert Excel metadata
        print("\n📊 Step 1: Converting Excel metadata to XML/JSONL...")
        xml_file, jsonl_file = export_xlsx_to_both(excel_file)
        print(f"✅ Created: {xml_file}")
        print(f"✅ Created: {jsonl_file}")
        
        # Step 2: Generate file catalog
        print("\n📁 Step 2: Generating file catalog...")
        catalog_file = process_file_metadata(
            dataset_jsonl=jsonl_file,
            file_list_source=file_list_source,
            source_name=source_name,
            agent_name=agent_name
        )
        print(f"✅ Created catalog: {catalog_file}")
        
        # Step 2.5: Extract dataset pattern from generated JSONL
        print("\n🔍 Extracting dataset pattern from JSONL...")
        with open(jsonl_file, 'r') as f:
            dataset_metadata = json.loads(f.readline())
        
        # Extract PN ID from dataset_id field (e.g., "PN000015 A multimodal..." -> "PN000015")
        dataset_id = dataset_metadata.get('dataset_id', '')
        pn_match = re.match(r'(PN[C]?\d+)', dataset_id)
        pn_id = pn_match.group(1) if pn_match else 'PN*'
        
        # Extract version (e.g., "V1")
        dataset_version = dataset_metadata.get('dataset_version', 'V1')
        
        # Build pattern (e.g., "PN000015*/V1")
        dataset_pattern = f"{pn_id}*/{dataset_version}"
        print(f"   Auto-detected pattern: {dataset_pattern}")
        
        # Step 3: Import dataset into datalad catalog
        print("\n📥 Step 3: Importing dataset into datalad catalog...")
        import subprocess
        
        # First validate the dataset
        validate_cmd = ['datalad', 'catalog-validate', '--metadata', catalog_file]
        print(f"   Validating: {' '.join(validate_cmd)}")
        validate_result = subprocess.run(validate_cmd, capture_output=True, text=True)
        
        if validate_result.returncode != 0:
            print(f"⚠️  Validation warning: {validate_result.stderr}")
            print("   Continuing with import...")
        else:
            print("✅ Validation successful")
        
        # Determine catalog root (parent of import directory)
        import_dir = os.path.dirname(os.path.abspath(__file__))
        catalog_root = os.path.dirname(import_dir)  # Go up from import/ to DataCatalogue/
        parent_dir = os.path.dirname(catalog_root)  # Go up to the directory containing DataCatalogue/
        catalog_name = os.path.basename(catalog_root)  # Should be 'DataCatalogue'
        
        # Make catalog_file absolute for datalad command
        abs_catalog_file = os.path.abspath(catalog_file)
        
        # Then import to catalog (run from parent directory)
        import_cmd = ['datalad', 'catalog-add', '--catalog', catalog_name, '--metadata', abs_catalog_file]
        print(f"   Importing: {' '.join(import_cmd)}")
        print(f"   Working directory: {parent_dir}")
        import_result = subprocess.run(import_cmd, capture_output=True, text=True, cwd=parent_dir)
        
        if import_result.returncode != 0:
            print(f"❌ Import failed: {import_result.stderr}")
            raise Exception(f"Failed to import dataset to catalog: {import_result.stderr}")
        else:
            print("✅ Dataset imported to catalog")
        
        # Step 4: Verify in catalog and reorder children
        print("\n🔍 Step 4: Finding dataset in catalog and reordering children...")
        results = find_catalogue_set_file(dataset_pattern, reorder_children=True)
        found_datasets = list(results.keys()) if results else []
        
        if found_datasets:
            print(f"✅ Found {len(found_datasets)} dataset(s): {found_datasets}")
        else:
            print("⚠️  No datasets found matching pattern")
        
        result = {
            'xml': xml_file,
            'jsonl': jsonl_file,
            'catalog': catalog_file,
            'found': found_datasets
        }
        
        print(f"\n🎉 Processing complete!")
        return result
        
    except Exception as e:
        print(f"\n❌ Error during processing: {str(e)}")
        raise


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description='Complete PublicnEUro dataset processing pipeline: Excel → XML/JSONL → File catalog → Datalad import → Catalog integration',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s data.xlsx /path/to/data
  %(prog)s metadata.xlsx ./file_list.jsonl --source MySource --agent MyAgent
  
Workflow:
  1. Convert Excel metadata to XML/JSONL formats
  2. Generate file catalog from data directory or file list
  3. Auto-detect dataset pattern from generated JSONL (PN ID + version)
  4. Validate and import dataset into datalad catalog
  5. Find dataset in catalog and reorder children
        """
    )
    
    parser.add_argument('excel_file', 
                       help='Path to Excel metadata file')
    parser.add_argument('file_list_source', 
                       help='Path to dataset directory or file list JSONL')
    parser.add_argument('--source', 
                       default='Local_Processing',
                       help='Name of the processing source (default: Local_Processing)')
    parser.add_argument('--agent', 
                       default='Pipeline',
                       help='Name of the processing agent (default: Pipeline)')
    parser.add_argument('--verbose', '-v', 
                       action='store_true',
                       help='Enable verbose output')
    
    args = parser.parse_args()
    
    # Validate input files/directories
    if not os.path.exists(args.excel_file):
        print(f"❌ Excel file not found: {args.excel_file}")
        sys.exit(1)
        
    if not os.path.exists(args.file_list_source):
        print(f"❌ File list source not found: {args.file_list_source}")
        sys.exit(1)
    
    try:
        result = process_dataset(
            excel_file=args.excel_file,
            file_list_source=args.file_list_source,
            source_name=args.source,
            agent_name=args.agent
        )
        
        if args.verbose:
            print(f"\nDetailed results: {result}")
            
        print(f"\n📋 Summary:")
        print(f"   XML file: {result['xml']}")
        print(f"   JSONL file: {result['jsonl']}")
        print(f"   Catalog file: {result['catalog']}")
        print(f"   Found datasets: {len(result['found'])}")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Process interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Pipeline failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()