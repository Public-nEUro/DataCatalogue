"""
Combined functionality from findset.py and execute_findset.py
Finds JSON files containing '"type": "dataset"' in catalog directory structures.
"""

import os
import json


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


def find_catalogue_set_file(target_pattern="PN000011*/V1", base_path=None, verbose=True):
    """
    Main function to find dataset files in catalog directory structures.
    Combines the functionality of findset.py and execute_findset.py.
    
    Args:
        target_pattern (str): Pattern to search for (e.g., "PN000011*/V1", "metadata/PN000001*/V1")
        base_path (str): Base path to search from (default: auto-detect DataCatalogue)
        verbose (bool): Whether to print detailed output (default: True)
        
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
        # Patterns like "PN000001*/V1" or "PN000011*/V1"
        if "*/" in pattern and pattern.endswith("/V1"):
            pn_prefix = pattern.split("*/")[0]  # e.g., "PN000001"
            version = pattern.split("/")[-1]    # e.g., "V1"
            
            if verbose:
                print(f"🔍 Looking for directories starting with: {pn_prefix}")
                print(f"🔢 Target version: {version}")
            
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
            
            # Process each matching directory's version subdirectory
            for pn_dir in matching_dirs:
                pn_path = os.path.join(metadata_path, pn_dir)
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
            
        return results
        
    finally:
        # Restore original working directory
        os.chdir(original_cwd)


def main():
    """
    Main execution function for command line usage.
    """
    results = find_catalogue_set_file()
    
    if results:
        print(f"\n🎯 Found {len(results)} dataset file(s)")
        for key, info in results.items():
            print(f"   {key}: {info['relative_path']}")
    else:
        print("\n❌ No dataset files found")


if __name__ == "__main__":
    main()
