"""
Combined functionality from findset.py and execute_findset.py
Finds JSON files containing '"type": "dataset"' in catalog directory structures.
Includes functionality to reorder dataset children.

Usage:
    # Command line execution (interactive mode):
    python find_catalogue_set_file.py
    
    # Programmatic usage:
    from find_catalogue_set_file import find_catalogue_set_file
    
    # Find all datasets matching pattern:
    results = find_catalogue_set_file("PN*/V*")
    
    # Find specific dataset version:
    results = find_catalogue_set_file("PN000011*/V1")
    
    # Find datasets in metadata directory:
    results = find_catalogue_set_file("metadata/PN000001*/V*")
    
    # Silent mode without verbose output:
    results = find_catalogue_set_file("PN*/V*", verbose=False)
    
    # Auto-reorder children without prompting:
    results = find_catalogue_set_file("PN*/V*", reorder_children=True)
    
    # Specify custom base path:
    results = find_catalogue_set_file("PN*/V*", base_path="/path/to/DataCatalogue")
    
    # Use absolute path to specific dataset directory (Windows):
    results = find_catalogue_set_file(r"D:\DataCatalogue\metadata\PN000009 Dataset\V1")
    
    # Use absolute path to specific dataset directory (Unix/Linux/Mac):
    results = find_catalogue_set_file("/home/user/DataCatalogue/metadata/PN000009 Dataset/V1")

Functions:
    - find_catalogue_set_file(): Main function to find and process datasets
    - sort_children(): Sort dataset children according to BIDS conventions
    - reorder_dataset_children(): Reorder children in a specific dataset file
    - find_jsonl_dataset(): Find dataset files in folder structures
    - fetch_set(): Search for dataset files in flat directory structure

Pattern formats supported:
    - "PN*/V*" : All datasets, all versions
    - "PN000011*/V1" : Specific dataset prefix, specific version  
    - "metadata/PN000001*/V*" : Datasets in metadata directory
    - Absolute paths: Cross-platform file system paths to specific dataset directories
    
Returns:
    Dictionary with dataset information including paths, metadata, and file details.
    All paths in results are normalized for cross-platform compatibility.
"""

import os
import json
import re


def sort_children(children):
    """
    Sort children according to the specified rules.
    
    Args:
        children (list): List of child items from dataset JSON
        
    Returns:
        list: Sorted list of children
    """
    source_items = []
    code_items = []
    file_items = []
    sub_numeric_items = []
    sub_alpha_items = []
    other_items = []
    
    # Categorize children
    for child in children:
        name = child.get('name', '')
        child_type = child.get('type', '')
        
        if name == 'source':
            source_items.append(child)
        elif name == 'code':
            code_items.append(child)
        elif child_type == 'file':
            file_items.append(child)
        elif name.startswith('sub-'):
            # Extract the part after 'sub-'
            sub_part = name[4:]  # Remove 'sub-' prefix
            
            # Check if it's numeric (with possible leading zeros)
            if re.match(r'^\d+$', sub_part):
                # Numeric: sort by integer value
                child['_sort_key'] = int(sub_part)
                sub_numeric_items.append(child)
            else:
                # Alphabetic: sort alphabetically
                child['_sort_key'] = sub_part
                sub_alpha_items.append(child)
        else:
            other_items.append(child)
    
    # Sort the sub-* items
    sub_numeric_items.sort(key=lambda x: x['_sort_key'])
    sub_alpha_items.sort(key=lambda x: x['_sort_key'])
    
    # Remove the temporary sort keys
    for item in sub_numeric_items + sub_alpha_items:
        if '_sort_key' in item:
            del item['_sort_key']
    
    # Combine in the specified order
    sorted_children = (
        source_items + 
        code_items + 
        file_items + 
        sub_numeric_items + 
        sub_alpha_items + 
        other_items
    )
    
    return sorted_children


def reorder_dataset_children(file_path, verbose=True):
    """
    Reorder children in a dataset JSON file.
    
    Args:
        file_path (str): Path to the dataset JSON file
        verbose (bool): Whether to print progress messages
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Read the JSON file
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Check if it's a dataset file and has children
        if data.get('type') != 'dataset':
            if verbose:
                print(f"   ⚠️  File is not a dataset type")
            return False
            
        if 'children' not in data:
            if verbose:
                print(f"   ⚠️  No children found in dataset")
            return False
        
        original_count = len(data['children'])
        if verbose:
            print(f"   📋 Reordering {original_count} children...")
        
        # Sort the children
        data['children'] = sort_children(data['children'])
        
        # Write back to file
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        
        if verbose:
            print(f"   ✅ Children reordered and file updated")
        return True
        
    except Exception as e:
        if verbose:
            print(f"   ❌ Error reordering: {e}")
        return False


def find_jsonl_dataset(folder):
    """
    Finds a JSON file containing '"type": "dataset"'.
    If the folder is 'metadata', it lists all datasets and returns a dictionary.
    
    Args:
        folder (str): Path to the folder to search
        
    Returns:
        dict or str: Dictionary of datasets if folder is 'metadata', 
                    otherwise path to dataset file or 'not found'
    """
    foldername = os.path.basename(folder)
    
    if foldername == 'metadata':
        dataset_file = {}
        for datasetname in os.listdir(folder):
            dataset_path = os.path.join(folder, datasetname)
            if os.path.isdir(dataset_path) and datasetname.startswith('PN'):
                for version in os.listdir(dataset_path):
                    version_path = os.path.join(dataset_path, version)
                    if os.path.isdir(version_path):
                        field = f"{datasetname}_{version}"
                        field = field.replace(' ', '').replace('-', '').replace(':', '')
                        dataset_file[field] = fetch_set(version_path)
        return dataset_file
    else:
        return fetch_set(folder)


def fetch_set(folder):
    """
    Searches for a dataset file in the current flat directory structure.
    
    Args:
        folder (str): Path to the folder to search
        
    Returns:
        str: Path to dataset file or 'not found' if none found
    """
    dataset_file = 'not found'
    
    for item in os.listdir(folder):
        item_path = os.path.join(folder, item)
        if os.path.isdir(item_path):
            for sub_item in os.listdir(item_path):
                sub_item_path = os.path.join(item_path, sub_item)
                if os.path.isfile(sub_item_path):
                    try:
                        with open(sub_item_path, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                        if isinstance(data, dict) and data.get('type', '').lower() == 'dataset':
                            dataset_file = sub_item_path
                            print(f'dataset file found {dataset_file}')
                    except (json.JSONDecodeError, UnicodeDecodeError):
                        continue
    
    return dataset_file


def find_catalogue_set_file(target_pattern="PN*/V*", base_path=None, verbose=True, reorder_children=None):
    """
    Main function to find dataset files in catalog directory structures.
    Combines the functionality of findset.py and execute_findset.py.
    
    Args:
        target_pattern (str): Pattern to search for (e.g., "PN000011*/V1", "metadata/PN000001*/V1")
                             or absolute path to specific dataset directory (cross-platform supported)
                             (e.g., r"D:\DataCatalogue\metadata\PN000009 Dataset\V1" or 
                              "/home/user/DataCatalogue/metadata/PN000009 Dataset/V1")
        base_path (str): Base path to search from (default: auto-detect DataCatalogue)
        verbose (bool): Whether to print detailed output (default: True)
        reorder_children (bool): Whether to reorder dataset children (None=ask user, True=yes, False=no)
        
    Returns:
        dict: Dictionary containing found datasets and their information
    """
    if verbose:
        print("🔍 Finding catalog dataset files")
        print("=" * 60)
    
    # Auto-detect base path if not provided
    if base_path is None:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        # Assume we're in the import directory, go up to DataCatalogue
        base_path = os.path.dirname(script_dir)
    
    # Change to the base directory
    original_cwd = os.getcwd()
    os.chdir(base_path)
    
    if verbose:
        print(f"📍 Working directory: {os.getcwd()}")
    
    try:
        results = {}
        
        # Check if target_pattern is an absolute path to a specific directory
        if os.path.isabs(target_pattern) and os.path.exists(target_pattern):
            if verbose:
                print(f"🎯 Processing absolute path: {target_pattern}")
            
            # Normalize path for cross-platform compatibility
            normalized_path = os.path.normpath(target_pattern)
            path_parts = normalized_path.replace('\\', '/').split('/')
            
            # Find PN directory and version
            pn_dir = None
            version = None
            
            for i, part in enumerate(path_parts):
                if part.startswith('PN') and i < len(path_parts) - 1:
                    pn_dir = part
                    version = path_parts[i + 1]
                    break
            
            if pn_dir and version:
                if verbose:
                    print(f"📂 Detected: {pn_dir}/{version}")
                
                # Use fetch_set to find dataset files in the target directory
                try:
                    result = fetch_set(normalized_path)
                    if result != 'not found':
                        if verbose:
                            print(f"   ✅ Dataset file found: {result}")
                        
                        # Store result
                        dataset_key = f"{pn_dir}_{version}".replace(' ', '').replace('-', '').replace(':', '')
                        results[dataset_key] = {
                            'path': result,
                            'relative_path': os.path.relpath(result, base_path),
                            'directory': pn_dir,
                            'version': version
                        }
                        
                        # Try to read and display dataset info
                        try:
                            with open(result, 'r', encoding='utf-8') as f:
                                dataset_data = json.load(f)
                            
                            results[dataset_key]['metadata'] = dataset_data
                            
                            if verbose:
                                print(f"   📋 Dataset info:")
                                print(f"      - Type: {dataset_data.get('type', 'N/A')}")
                                print(f"      - Name: {dataset_data.get('name', 'N/A')}")
                                print(f"      - ID: {dataset_data.get('dataset_id', 'N/A')}")
                                if 'dataset_version' in dataset_data:
                                    print(f"      - Version: {dataset_data.get('dataset_version', 'N/A')}")
                                if 'authors' in dataset_data:
                                    print(f"      - Authors: {len(dataset_data['authors'])} author(s)")
                                    
                        except Exception as e:
                            if verbose:
                                print(f"   ⚠️  Could not read dataset details: {e}")
                    else:
                        if verbose:
                            print(f"   ❌ No dataset file found in {target_pattern}")
                        
                except Exception as e:
                    if verbose:
                        print(f"   ❌ Error processing {target_pattern}: {e}")
            else:
                if verbose:
                    print(f"❌ Could not extract PN directory and version from path: {target_pattern}")
            
            # Skip to the end for reordering check
            if verbose:
                print(f"\n📊 Summary: Found {len(results)} dataset(s)")
        
        else:
            # Original pattern-based logic
            # Parse target pattern
            # Handle patterns like "metadata/PN000001*/V1" or "PN000001*/V1"
            if target_pattern.startswith("metadata/"):
                # Remove "metadata/" prefix
                pattern = target_pattern[9:]  # Remove "metadata/"
                metadata_path = "metadata"
            else:
                pattern = target_pattern
                metadata_path = "metadata"
            
            if verbose:
                print(f"🎯 Target pattern: {target_pattern}")
                print(f"📂 Parsed pattern: {pattern}")
            
            if not os.path.exists(metadata_path):
                if verbose:
                    print(f"❌ Metadata directory not found: {metadata_path}")
                return results
            
            # Extract PN number and version from pattern
            # Patterns like "PN*/V*" or "PN000011*/V1"
            if "*/" in pattern and pattern.split("/")[-1].startswith("V"):
                pn_prefix = pattern.split("*/")[0]  # e.g., "PN000001" or "PN"
                version_pattern = pattern.split("/")[-1]    # e.g., "V1" or "V*"
                
                if verbose:
                    print(f"🔍 Looking for directories starting with: {pn_prefix}")
                    print(f"🔢 Target version pattern: {version_pattern}")
                
                # Look for matching PN directories
                matching_dirs = []
                for item in os.listdir(metadata_path):
                    if item.startswith(pn_prefix):
                        matching_dirs.append(item)
                
                if not matching_dirs:
                    if verbose:
                        print(f"❌ No directories found starting with {pn_prefix}")
                    return results
                
                if verbose:
                    print(f"📁 Found matching directories: {matching_dirs}")
                
                # Process each matching directory's version subdirectories
                for pn_dir in matching_dirs:
                    pn_path = os.path.join(metadata_path, pn_dir)
                    
                    if not os.path.isdir(pn_path):
                        continue
                    
                    # Find version directories that match the version pattern
                    matching_versions = []
                    for version_item in os.listdir(pn_path):
                        version_item_path = os.path.join(pn_path, version_item)
                        if os.path.isdir(version_item_path):
                            if version_pattern == "V*" and version_item.startswith("V"):
                                matching_versions.append(version_item)
                            elif version_pattern == version_item:
                                matching_versions.append(version_item)
                    
                    if not matching_versions:
                        if verbose:
                            print(f"\n📂 Processing: {pn_dir}")
                            print(f"   ⚠️  No {version_pattern} directories found in {pn_dir}")
                        continue
                    
                    # Process each matching version directory
                    for version in matching_versions:
                        version_path = os.path.join(pn_path, version)
                        
                        if verbose:
                            print(f"\n📂 Processing: {pn_dir}/{version}")
                        
                        if not os.path.exists(version_path):
                            if verbose:
                                print(f"   ⚠️  {version} directory not found in {pn_dir}")
                            continue
                    
                        # Use fetch_set to find dataset files in the version directory
                        try:
                            result = fetch_set(version_path)
                            if result != 'not found':
                                if verbose:
                                    print(f"   ✅ Dataset file found: {result}")
                                
                                # Store result
                                dataset_key = f"{pn_dir}_{version}".replace(' ', '').replace('-', '').replace(':', '')
                                results[dataset_key] = {
                                    'path': result,
                                    'relative_path': os.path.relpath(result, base_path),
                                    'directory': pn_dir,
                                    'version': version
                                }
                                
                                # Try to read and display dataset info
                                try:
                                    with open(result, 'r', encoding='utf-8') as f:
                                        dataset_data = json.load(f)
                                    
                                    results[dataset_key]['metadata'] = dataset_data
                                    
                                    if verbose:
                                        print(f"   📋 Dataset info:")
                                        print(f"      - Type: {dataset_data.get('type', 'N/A')}")
                                        print(f"      - Name: {dataset_data.get('name', 'N/A')}")
                                        print(f"      - ID: {dataset_data.get('dataset_id', 'N/A')}")
                                        if 'dataset_version' in dataset_data:
                                            print(f"      - Version: {dataset_data.get('dataset_version', 'N/A')}")
                                        if 'authors' in dataset_data:
                                            print(f"      - Authors: {len(dataset_data['authors'])} author(s)")
                                            
                                except Exception as e:
                                    if verbose:
                                        print(f"   ⚠️  Could not read dataset details: {e}")
                            else:
                                if verbose:
                                    print(f"   ❌ No dataset file found")
                                
                        except Exception as e:
                            if verbose:
                                print(f"   ❌ Error processing {version_path}: {e}")
            
            else:
                if verbose:
                    print(f"❌ Unsupported pattern format: {pattern}")
                    print("   Supported formats: 'PN######*/V#' or 'metadata/PN######*/V#'")
            
            if verbose:
                print(f"\n📊 Summary: Found {len(results)} dataset(s)")
        
        # Ask about reordering children if not specified
        if results and reorder_children is None and verbose:
            try:
                response = input("\n🔄 Do you want to reorder dataset children? (Y/N): ").strip().upper()
                reorder_children = response == 'Y'
            except (EOFError, KeyboardInterrupt):
                reorder_children = False
                print()
        
        # Apply reordering if requested
        if results and reorder_children:
            if verbose:
                print("\n🔄 Reordering dataset children...")
                print("=" * 40)
            
            reorder_success = 0
            for key, info in results.items():
                dataset_path = info['path']
                if verbose:
                    print(f"📂 Processing: {key}")
                
                if reorder_dataset_children(dataset_path, verbose):
                    reorder_success += 1
                    
            if verbose:
                print(f"\n✅ Reordered {reorder_success}/{len(results)} dataset(s)")
            
        return results
        
    finally:
        # Restore original working directory
        os.chdir(original_cwd)


def main():
    """
    Main execution function for command line usage.
    """
    print("🔍 DataCatalogue Dataset Finder")
    print("=" * 50)
    
    results = find_catalogue_set_file()
    
    if results:
        print(f"\n🎯 Found {len(results)} dataset file(s)")
        for key, info in results.items():
            print(f"   {key}: {info['relative_path']}")
    else:
        print("\n❌ No dataset files found")


if __name__ == "__main__":
    main()
