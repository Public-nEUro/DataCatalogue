#!/usr/bin/env python3
"""
Complete dataset processing pipeline CLI

This script provides a command-line interface for the complete PublicnEUro dataset
processing workflow, from Excel metadata to catalog integration.
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


def process_dataset(excel_file, data_directory, dataset_pattern, source_name='Local_Processing', agent_name='Pipeline'):
    """
    Process complete dataset from Excel to catalog with datalad import
    
    Args:
        excel_file (str): Path to Excel metadata file
        data_directory (str): Path to dataset directory
        dataset_pattern (str): Pattern to find dataset in catalog (e.g., 'PN000011*/V1')
        source_name (str): Name of the processing source
        agent_name (str): Name of the processing agent
        
    Returns:
        dict: Processing results with file paths and found datasets
        
    Workflow:
        1. Convert Excel metadata to XML/JSONL
        2. Generate file catalog from data directory
        3. Validate and import dataset into datalad catalog
        4. Find and optionally reorder dataset children
    """
    print(f"Starting dataset processing pipeline...")
    print(f"Excel file: {excel_file}")
    print(f"Data directory: {data_directory}")
    print(f"Dataset pattern: {dataset_pattern}")
    
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
            file_list_source=data_directory,
            source_name=source_name,
            agent_name=agent_name
        )
        print(f"✅ Created catalog: {catalog_file}")
        
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
        
        # Then import to catalog
        import_cmd = ['datalad', 'catalog-add', '--catalog', '../DataCatalogue', '--metadata', catalog_file]
        print(f"   Importing: {' '.join(import_cmd)}")
        import_result = subprocess.run(import_cmd, capture_output=True, text=True)
        
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
  %(prog)s data.xlsx /path/to/data "PN000011*/V1"
  %(prog)s metadata.xlsx ./dataset_folder "PN*" --source MySource --agent MyAgent
  
Workflow:
  1. Convert Excel metadata to XML/JSONL formats
  2. Generate file catalog from data directory  
  3. Validate and import dataset into datalad catalog
  4. Find dataset in catalog and reorder children
        """
    )
    
    parser.add_argument('excel_file', 
                       help='Path to Excel metadata file')
    parser.add_argument('data_directory', 
                       help='Path to dataset directory')
    parser.add_argument('dataset_pattern', 
                       help='Pattern to find dataset in catalog (e.g., "PN000011*/V1")')
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
        
    if not os.path.exists(args.data_directory):
        print(f"❌ Data directory not found: {args.data_directory}")
        sys.exit(1)
    
    try:
        result = process_dataset(
            excel_file=args.excel_file,
            data_directory=args.data_directory,
            dataset_pattern=args.dataset_pattern,
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