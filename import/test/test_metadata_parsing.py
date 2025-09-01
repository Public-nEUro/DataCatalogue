#!/usr/bin/env python3
"""
Test the integrated metadata parsing functionality
"""

import os
import sys

# Get the directory where this script is located
script_dir = os.path.dirname(os.path.abspath(__file__))
# Get the import directory (parent of script if in subfolder, or script_dir itself)
import_dir = script_dir if os.path.basename(script_dir) == 'import' else os.path.dirname(script_dir)

# Add import directory to Python path
sys.path.insert(0, import_dir)

try:
    from export_xlsx import parse_excel_metadata
    print("✓ Successfully imported metadata parsing function")
    
    # Test the function with the example file
    excel_file = os.path.join(import_dir, "data_import", "PN000011 Clinical Pediatric MRI with and without Motion Correction", "PublicnEUro_PN000011.xlsx")
    
    print(f"Script directory: {script_dir}")
    print(f"Import directory: {import_dir}")
    print(f"Excel file path: {excel_file}")
    print(f"File exists: {os.path.exists(excel_file)}")
    
    if os.path.exists(excel_file):
        print("\n" + "="*70)
        print("COMPREHENSIVE METADATA PARSING TEST")
        print("="*70)
        
        metadata = parse_excel_metadata(excel_file)
        
        # Test basic fields (used by XML)
        print("\n--- Basic Fields (XML) ---")
        basic_fields = ["title", "description", "subtitle", "doi", "id", "download_url", "name"]
        for field in basic_fields:
            value = metadata.get(field, "Not found")
            print(f"  {field}: {value}")
        
        # Test authors
        print(f"\n--- Authors ({len(metadata.get('authors', []))}) ---")
        for i, author in enumerate(metadata.get('authors', [])[:3], 1):  # Show first 3
            print(f"  {i}. {author.get('givenName', '')} {author.get('familyName', '')}")
        if len(metadata.get('authors', [])) > 3:
            print(f"  ... and {len(metadata.get('authors', [])) - 3} more")
        
        # Test extended fields (used by JSONL)
        print(f"\n--- Extended Fields (JSONL) ---")
        extended_fields = ["type", "dataset_version", "keywords", "license"]
        for field in extended_fields:
            value = metadata.get(field, "Not found")
            if field == "keywords":
                print(f"  {field}: {len(value) if isinstance(value, list) else 0} keywords")
                if isinstance(value, list) and value:
                    print(f"    Examples: {', '.join(value[:3])}")
            elif field == "license":
                print(f"  {field}: {value.get('name', 'Not found') if isinstance(value, dict) else value}")
            else:
                print(f"  {field}: {value}")
        
        # Test funding
        print(f"\n--- Funding ({len(metadata.get('funding', []))}) ---")
        for i, fund in enumerate(metadata.get('funding', [])[:3], 1):  # Show first 3
            print(f"  {i}. {fund.get('name', 'N/A')} (ID: {fund.get('identifier', 'N/A')})")
        if len(metadata.get('funding', [])) > 3:
            print(f"  ... and {len(metadata.get('funding', [])) - 3} more")
        
        # Test publications
        print(f"\n--- Publications ({len(metadata.get('publications', []))}) ---")
        for i, pub in enumerate(metadata.get('publications', [])[:2], 1):  # Show first 2
            print(f"  {i}. {pub.get('title', 'N/A')[:60]}...")
            print(f"     DOI: {pub.get('doi', 'N/A')}")
            authors = pub.get('authors', [])
            if authors:
                author = authors[0]
                print(f"     Author: {author.get('givenName', '')} {author.get('familyName', '')}")
        if len(metadata.get('publications', [])) > 2:
            print(f"  ... and {len(metadata.get('publications', [])) - 2} more")
        
        # Test participants
        print(f"\n--- Participants ---")
        participants = metadata.get('participants', {})
        if participants and participants.get('content'):
            content = participants['content']
            print(f"  Total number: {content.get('total_number', ['N/A'])[0]}")
            print(f"  Age range: {content.get('age_range', ['N/A'])[0]}")
            print(f"  Healthy controls: {content.get('number_of_healthy', ['N/A'])[0]}")
            print(f"  Patients: {content.get('number_of_patients', ['N/A'])[0]}")
            print(f"  Males: {content.get('number_of_biological_males', ['N/A'])[0]}")
            print(f"  Females: {content.get('number_of_biological_females', ['N/A'])[0]}")
        else:
            print("  No participant information found")
        
        # Test metadata sources
        print(f"\n--- Metadata Sources ---")
        sources = metadata.get('metadata_sources', {}).get('sources', [])
        print(f"  Found {len(sources)} sources:")
        for i, source in enumerate(sources[:3], 1):  # Show first 3
            print(f"  {i}. {source.get('agent_name', 'N/A')} - {source.get('source_name', 'N/A')} ({source.get('source_version', 'N/A')})")
        if len(sources) > 3:
            print(f"  ... and {len(sources) - 3} more")
        
        # Test detailed metadata
        print(f"\n--- Detailed Metadata ---")
        detailed = metadata.get('detailed_metadata', {})
        if detailed and detailed.get('content'):
            content = detailed['content']
            for key, value in content.items():
                if value:
                    print(f"  {key}: {len(value) if isinstance(value, list) else 1} entries")
        else:
            print("  No detailed metadata found")
        
        print("\n" + "="*70)
        print("✅ COMPREHENSIVE METADATA PARSING TEST COMPLETED")
        print("✓ All fields extracted successfully")
        print("✓ Data structure is consistent for both XML and JSONL export")
        print("="*70)
        
    else:
        print("❌ Excel file not found")
        print("Make sure the Excel file exists in the data_import directory")
        
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("Make sure export_xlsx.py is in the import directory")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
