#!/usr/bin/env python3
"""
Update existing dataset.json files with size information in their descriptions.

This script:
1. Reads size data from PublicnEUro ID Dataset name Dataset size.txt
2. Uses find_catalogue_set_file to find all dataset JSON files
3. Updates the description field to append (total size: XGB)
4. Skips PN000003 subdatasets (fsl-*, spm-*)
"""

import os
import sys
import json
import re

# Add parent directory to path for imports
script_dir = os.path.dirname(os.path.abspath(__file__))


def load_size_data(txt_file):
    """
    Load size data from the text file.
    Returns dict: {PN_ID: size_in_gb}
    """
    size_data = {}
    
    with open(txt_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Skip header line
    for line in lines[1:]:
        line = line.strip()
        if not line:
            continue
        
        parts = line.split('\t')
        if len(parts) >= 3:
            pn_id = parts[0].strip()
            size_gb = parts[2].strip()
            
            # Convert size to float
            try:
                size_data[pn_id] = float(size_gb)
            except ValueError:
                print(f"Warning: Could not parse size for {pn_id}: {size_gb}")
    
    return size_data


def should_skip_dataset(dataset_path):
    """
    Check if this is a PN000003 subdataset that should be skipped.
    Returns True if path contains fsl or spm (case insensitive)
    """
    path_lower = dataset_path.lower()
    # Check if it's a PN000003 subdataset
    if 'pn000003' in path_lower:
        # Check for fsl or spm in the path (not just with dash)
        if 'fsl' in path_lower or 'spm' in path_lower:
            return True
    return False


def extract_pn_id_from_path(dataset_path):
    """
    Extract PN ID from the dataset path.
    Example: 'PN000001 OpenNeuroPET Phantoms/V1' -> 'PN000001'
    For PN000003 subdatasets, returns 'PN000003' (parent ID)
    """
    # First check if this is a PN000003 subdataset
    if should_skip_dataset(dataset_path):
        return None  # Will be skipped anyway
    
    # Extract the PN ID (just the number part)
    match = re.search(r'(PN\d{6})', dataset_path)
    if match:
        return match.group(1)
    return None


def update_dataset_description(dataset_json_path, size_gb):
    """
    Update the description field in dataset.json to append size.
    Returns True if updated, False otherwise.
    """
    try:
        # Read the JSON file
        with open(dataset_json_path, 'r', encoding='utf-8') as f:
            dataset = json.load(f)
        
        # Check if it's a dataset type and has description
        if dataset.get('type') != 'dataset':
            print(f"  Skipping {dataset_json_path}: not a dataset type")
            return False
        
        if 'description' not in dataset:
            print(f"  Skipping {dataset_json_path}: no description field")
            return False
        
        description = dataset['description']
        
        # Check if size is already appended
        if '(total size:' in description.lower():
            print(f"  Skipping {dataset_json_path}: size already present")
            return False
        
        # Append size to description
        new_description = f"{description} (total size: {size_gb}GB)"
        dataset['description'] = new_description
        
        # Write back to file
        with open(dataset_json_path, 'w', encoding='utf-8') as f:
            json.dump(dataset, f, indent=2, ensure_ascii=False)
        
        print(f"  ✓ Updated: {dataset_json_path}")
        print(f"    New description: {new_description[:100]}...")
        return True
        
    except Exception as e:
        print(f"  ✗ Error updating {dataset_json_path}: {e}")
        return False


def main():
    """Main function to update all datasets."""
    print("=" * 80)
    print("Dataset Size Update Script")
    print("=" * 80)
    
    # Paths
    size_file = os.path.join(script_dir, "PublicnEUro ID Dataset name Dataset size.txt")
    metadata_dir = os.path.join(os.path.dirname(script_dir), "metadata")
    
    print(f"\n📄 Size data file: {size_file}")
    print(f"📁 Metadata directory: {metadata_dir}")
    
    # Load size data
    print("\n1. Loading size data...")
    size_data = load_size_data(size_file)
    print(f"   Loaded size data for {len(size_data)} datasets:")
    for pn_id, size in sorted(size_data.items()):
        print(f"     {pn_id}: {size} GB")
    
    # Find all dataset JSON files
    print("\n2. Finding dataset JSON files...")
    os.chdir(metadata_dir)
    
    # Simply walk through all PN* directories
    dataset_files = []
    
    for pn_dir in os.listdir(metadata_dir):
        if not pn_dir.startswith('PN'):
            continue
        
        pn_path = os.path.join(metadata_dir, pn_dir)
        if not os.path.isdir(pn_path):
            continue
        
        # Skip PN000003 subdatasets early
        if should_skip_dataset(pn_dir):
            print(f"   ⊘ Skipping PN000003 subdataset: {pn_dir}")
            continue
        
        # Look for V* directories
        for version_dir in os.listdir(pn_path):
            if not version_dir.startswith('V'):
                continue
            
            version_path = os.path.join(pn_path, version_dir)
            if not os.path.isdir(version_path):
                continue
            
            # Find the JSON file with type=dataset
            for root, dirs, files in os.walk(version_path):
                for file in files:
                    if file.endswith('.json'):
                        json_path = os.path.join(root, file)
                        try:
                            with open(json_path, 'r', encoding='utf-8') as f:
                                data = json.load(f)
                            if data.get('type') == 'dataset':
                                dataset_files.append((f"{pn_dir}/{version_dir}", json_path))
                                break  # Found dataset for this version
                        except:
                            pass
                if dataset_files and dataset_files[-1][0] == f"{pn_dir}/{version_dir}":
                    break  # Found dataset for this version, stop searching
    
    print(f"   Found {len(dataset_files)} dataset files")
    
    # Process each dataset
    print("\n3. Processing datasets...")
    updated_count = 0
    skipped_count = 0
    
    for dir_path, json_path in dataset_files:
        print(f"\n📦 Processing: {dir_path}")
        
        # Extract PN ID
        pn_id = extract_pn_id_from_path(dir_path)
        if not pn_id:
            print(f"  ⊘ Skipped: Could not extract PN ID or is PN000003 subdataset")
            skipped_count += 1
            continue
        
        # Get size for this dataset
        if pn_id not in size_data:
            print(f"  ⊘ No size data found for {pn_id}")
            skipped_count += 1
            continue
        
        size_gb = size_data[pn_id]
        print(f"  📊 Size: {size_gb} GB")
        print(f"  📄 JSON file: {os.path.relpath(json_path, metadata_dir)}")
        
        # Update the dataset
        if update_dataset_description(json_path, size_gb):
            updated_count += 1
        else:
            skipped_count += 1
    
    # Summary
    print("\n" + "=" * 80)
    print("Summary")
    print("=" * 80)
    print(f"✓ Updated: {updated_count} datasets")
    print(f"⊘ Skipped: {skipped_count} datasets")
    print(f"📊 Total processed: {len(dataset_files)} files")


if __name__ == "__main__":
    main()
