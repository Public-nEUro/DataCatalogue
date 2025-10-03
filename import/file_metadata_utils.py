#!/usr/bin/env python3
"""
File listing and metadata processing utilities for PublicnEUro datasets.

This module combines the functionality of get_files.py and listjl2filetype.py
into importable functions that can process dataset files and generate comprehensive
metadata catalogs.

Usage Examples:
    # Process complete dataset metadata with directory scanning
    from file_metadata_utils import process_file_metadata
    output_file = process_file_metadata(
        dataset_jsonl='dataset.jsonl',
        file_list_source='/path/to/data/directory',  # Directory to scan
        source_name='PublicnEUro',
        agent_name='Cyril Pernet'
    )
    
    # Process with existing file list JSONL
    output_file = process_file_metadata(
        dataset_jsonl='dataset.jsonl',
        file_list_source='file_list.jsonl',  # Pre-generated file list
        source_name='PublicnEUro',
        agent_name='Cyril Pernet'
    )
        
    # Scan directory and get file information
    from file_metadata_utils import get_file_info
    file_list = get_file_info('/path/to/dataset/directory')
    # Returns: [{'path': 'sub-01/anat/sub-01_T1w.nii.gz', 'contentbytesize': 12345}, ...]
    
    # Scan directory and save to JSONL file
    get_file_info('/path/to/dataset/directory', save_to_file=True, output_file='my_files.jsonl')
    
Key Functions:
    - get_file_info(directory_path, save_to_file=False, output_file="file_list.jsonl"): 
        Scan directory recursively for BIDS-compliant files and return file information
        Supports .nii, .json, .tsv, .log, neuroimaging formats, and BIDS standard files
        
    - process_file_metadata(dataset_jsonl, file_list_source, source_name, agent_name):
        Generate comprehensive metadata catalog combining dataset info with file listings
        file_list_source can be: directory path, JSONL file path, or list of file dictionaries
"""

import os
import json
import re
from typing import List, Dict, Union


def get_file_info(directory_path: str, save_to_file: bool = False, output_file: str = "file_list.jsonl") -> List[Dict]:
    """
    Walk through a directory structure and return BIDS-compliant file information.
    
    This function recursively scans a directory for files that comply with BIDS
    (Brain Imaging Data Structure) standards and neuroimaging formats commonly
    used in neuroscience datasets.
    
    Args:
        directory_path (str): The path to the directory to scan recursively
        save_to_file (bool): Whether to save the results to a JSONL file (default: False)
        output_file (str): Name of the output file if save_to_file is True (default: "file_list.jsonl")
        
    Returns:
        List[Dict]: List of dictionaries with file information, each containing:
            - 'path': Relative path from directory_path
            - 'contentbytesize': File size in bytes
            
    Included File Types:
        - BIDS standard: .json, .tsv, .tsv.gz, .nii, .nii.gz
        - Neuroimaging: .edf, .vhdr, .vmrk, .eeg, .set, .fdt, .bdf
        - Additional: .zip, .log, .pcd, .tsa, .tst, .tsm, .tsp, .wfb
        - BIDS text files: README, CHANGES, LICENSE, CITATION (no extension)
        
    Excluded:
        - 'code' directories (completely skipped)
        - Non-BIDS files: .txt, .md, .yml, .py, etc.
        
    Special Handling:
        - Directories within 'sourcedata' are included with total size
        - Path separators normalized to forward slashes for cross-platform compatibility
        
    Example:
        >>> files = get_file_info('/data/study01')
        >>> print(files[0])
        {'path': 'sub-01/anat/sub-01_T1w.nii.gz', 'contentbytesize': 8234567}
        
        >>> get_file_info('/data/study01', save_to_file=True, output_file='study_files.jsonl')
        # Creates study_files.jsonl with one JSON object per line
        
    Note:
        This function is designed for BIDS-compliant datasets and may not be
        suitable for general file system scanning due to its specific filtering rules.
    """
    file_info = []
    
    for root, dirs, files in os.walk(directory_path):
        # Exclude 'code' directory completely
        if "code" in dirs:
            dirs.remove("code")

        # Process directories
        for directory in dirs:
            full_path = os.path.join(root, os.path.normpath(directory))
            # Only include directories within 'sourcedata'
            if root.endswith("sourcedata"):
                size = sum(os.path.getsize(os.path.join(dirpath, filename)) 
                          for dirpath, _, filenames in os.walk(full_path) for filename in filenames)
                # Use sourcedata as the parent directory name
                dirname = os.path.join("sourcedata", os.path.normpath(directory)).replace("\\", "/")
                file_info.append({"path": dirname, "contentbytesize": size})
                
        # Process files
        for file in files:
            full_path = os.path.join(root, file)
            
            # Check if file should be included
            should_include = False
            
            # Include files with BIDS-standard extensions + neuroimaging formats
            if file.endswith(('.json', '.edf', '.vhdr', '.vmrk', '.eeg', '.set', '.fdt', '.bdf', 
                             '.nii', '.nii.gz', '.zip', '.tsv', '.tsv.gz', '.pcd', '.tsa', 
                             '.tst', '.tsm', '.tsp', '.wfb', '.log','.h5')):
                should_include = True
            
            # Include BIDS-standard plain text files (no extension) 
            # as per BIDS specification: https://bids-specification.readthedocs.io/
            elif file in ('README', 'CHANGES', 'LICENSE', 'CITATION'):
                should_include = True
            
            if should_include:
                size = os.path.getsize(full_path)
                filename = os.path.relpath(full_path, directory_path).replace("\\", "/")  # Normalize to forward slashes
                file_info.append({"path": filename, "contentbytesize": size})
    
    if save_to_file:
        # Use the output_file parameter as-is if it's an absolute path, otherwise join with cwd
        if os.path.isabs(output_file):
            output_path = output_file
        else:
            output_path = os.path.join(os.getcwd(), output_file)
        with open(output_path, "w") as f:
            for item in file_info:
                json.dump(item, f)
                f.write("\n")  # Add newline after each JSON object
    
    return file_info


def process_file_metadata(dataset_jsonl: str, 
                         file_list_source: Union[str, List[Dict]], 
                         source_name: str, 
                         agent_name: str,
                         output_file: str = None) -> str:
    """
    Process dataset metadata and file listings into a comprehensive catalog.
    
    Args:
        dataset_jsonl: Path to the dataset JSONL file (from export_xlsx.py)
        file_list_source: Either:
            - Path to a directory to scan for files
            - Path to a file_list.jsonl file
            - List of file info dictionaries
        source_name: Name of the data source
        agent_name: Name of the processing agent
        output_file: Optional custom output filename
        
    Returns:
        Path to the generated output file
        
    Raises:
        FileNotFoundError: If dataset_jsonl file doesn't exist
        ValueError: If file_list_source is invalid
    """
    # 1 - Get dataset info
    if not os.path.exists(dataset_jsonl):
        raise FileNotFoundError(f'Dataset JSONL file {dataset_jsonl} not found')

    with open(dataset_jsonl, 'r') as f:
        dataset_info = json.loads(f.read())

    # Clean up dataset_id and dataset_version (remove trailing spaces)
    if 'dataset_id' in dataset_info:
        dataset_info['dataset_id'] = dataset_info['dataset_id'].strip()
    if 'dataset_version' in dataset_info:
        dataset_info['dataset_version'] = dataset_info['dataset_version'].strip()

    # Add metadata sources if not already present
    if 'metadata_sources' not in dataset_info:
        dataset_info['metadata_sources'] = {
            'sources': {
                'source_name': source_name,
                'source_version': dataset_info.get('dataset_version', ''),
                'agent_name': agent_name
            }
        }

    # 2 - Get file list first (we need it to build hasPart)
    file_info_list = []
    
    if isinstance(file_list_source, list):
        # Direct list of file info dictionaries
        file_info_list = file_list_source
    elif isinstance(file_list_source, str):
        if os.path.isdir(file_list_source):
            # Directory path - scan it
            file_info_list = get_file_info(file_list_source, save_to_file=False)
        elif os.path.isfile(file_list_source):
            # File path - read the JSONL file
            with open(file_list_source, 'r') as f:
                file_info_list = [json.loads(line.strip()) for line in f.readlines() if line.strip()]
        else:
            raise ValueError(f"File list source not found: {file_list_source}")
    else:
        raise ValueError(f"Invalid file_list_source type: {type(file_list_source)}")

    # Add hasPart to dataset_info with all file paths
    file_paths = []
    for file_info_dict in file_info_list:
        if 'path' in file_info_dict:
            file_paths.append(file_info_dict['path'].replace("\\", "/"))
    
    # Add hasPart field to dataset
    dataset_info['hasPart'] = sorted(file_paths)

    # Determine output filename
    if output_file is None:
        output_file = f"{dataset_info['name'].replace(' ', '')}.jsonl"
    
    # Write dataset info with hasPart
    _write_jsonl_line(output_file, dataset_info, mode='w')

    # 3 - Process each file and append to output
    clean_dataset_id = dataset_info.get('dataset_id', dataset_info.get('id', '')).strip()
    clean_dataset_version = dataset_info.get('dataset_version', '').strip()
    
    for file_info_dict in file_info_list:
        if 'path' in file_info_dict and 'contentbytesize' in file_info_dict:
            item = {
                'type': 'file',
                'dataset_id': clean_dataset_id,
                'dataset_version': clean_dataset_version,
                'path': file_info_dict['path'].replace("\\", "/"),  # Normalize path separators
                'contentbytesize': float(file_info_dict['contentbytesize']),
                'isPartOf': clean_dataset_id,  # Add isPartOf relationship
                'metadata_sources': {
                    'sources': {
                        'source_name': source_name,
                        'source_version': clean_dataset_version,
                        'agent_name': agent_name
                    }
                }
            }
            
            # Fix metadata sources structure (recent addition)
            for k, v in item['metadata_sources'].items():
                item['metadata_sources'][k] = [v]
            
            _write_jsonl_line(output_file, item, mode='a')
        else:
            print(f"Warning: Invalid file info format: {file_info_dict}")

    # 4 - Fix known metadata sources issues
    _fix_metadata_sources(output_file)
    
    return output_file


def _write_jsonl_line(filename: str, json_obj: Dict, mode: str = 'a'):
    """
    Write a JSON object as a line to a JSONL file.
    
    Args:
        filename: Output filename
        json_obj: Dictionary to write as JSON
        mode: File mode ('w' for write, 'a' for append)
    """
    json_str = json.dumps(json_obj, ensure_ascii=False)
    # Fix double slashes and other unwanted stuff
    json_str = re.sub(r'\\\\', '/', json_str)  # Ensure forward slashes
    json_str = re.sub(r'//', '/', json_str)    # Ensure forward slashes

    with open(filename, mode) as f:
        f.write(json_str + '\n')


def _fix_metadata_sources(filename: str):
    """
    Fix known issues with metadata_sources formatting in JSONL files.
    
    Args:
        filename: Path to the JSONL file to fix
    """
    lines = []
    with open(filename, 'r') as f:
        lines = f.readlines()

    updated_lines = []
    for line in lines:
        if line.strip() == "":
            continue
        
        if '"metadata_sources":{"sources":' not in line:
            updated_lines.append(line)
            continue

        parts = re.split(r'"metadata_sources":\{"sources":', line)
        if len(parts) < 2:
            updated_lines.append(line)
            continue
        
        part1 = parts[0]
        part2 = '"metadata_sources":{"sources":['  # Add the square bracket
        part3 = parts[1]
        part3 = part3.rstrip('}').rstrip() + '}]}}'  # Rebuild ending adding square bracket
        updated_lines.append(part1 + part2 + part3)

    # Rewrite the file
    with open(filename, 'w') as f:
        f.writelines(updated_lines)


# Convenience aliases for backward compatibility
def listjl2filetype(dataset_jsonl: str, list_jsonl: str, source_name: str, agent_name: str) -> str:
    """
    Legacy function name - calls process_file_metadata with file list JSONL.
    
    Args:
        dataset_jsonl: Path to dataset JSONL file
        list_jsonl: Path to file list JSONL file  
        source_name: Name of the data source
        agent_name: Name of the processing agent
        
    Returns:
        Path to the generated output file
    """
    return process_file_metadata(dataset_jsonl, list_jsonl, source_name, agent_name)


if __name__ == "__main__":
    # Example usage
    print("File metadata processing utilities")
    print("Import this module to use get_file_info() and process_file_metadata()")
