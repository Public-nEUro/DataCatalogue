#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: martin norgaard and cyril pernet
"""

import os
import json

def get_file_info(path, savelist):
    """
    This function walks through a directory structure and returns a list of dictionaries 
    containing BIDS-compliant file information with cross-platform path support.

    Args:
        path: The path to the directory to start searching from.
        savelist: If 1, saves output to 'file_list.jsonl'; if 0, returns list only.

    Returns:
        A list of dictionaries, where each dictionary contains "path" and "contentbytesize" 
        keys for each file and directory. Includes directories within 'sourcedata' and 
        excludes 'code' directories. Paths are normalized to forward slashes for 
        cross-platform compatibility.
        
        Supported file types:
        - BIDS standard: .json, .tsv, .tsv.gz, .nii, .nii.gz
        - Neuroimaging: .edf, .vhdr, .vmrk, .eeg, .set, .fdt, .bdf
        - Additional: .zip, .log, .pcd, .tsa, .tst, .tsm, .tsp, .wfb, .yml
        - BIDS text files: README, CHANGES, LICENSE, CITATION (no extension)
    """
    file_info = []
    
    for root, dirs, files in os.walk(path):
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
                dirname = os.path.join("sourcedata", os.path.normpath(directory)).replace("\\", "/")
                file_info.append({"path": dirname, "contentbytesize": size})
        
        # Process files
        for file in files:
            full_path = os.path.join(root, file)
            
            # Include files with BIDS-standard extensions + neuroimaging formats
            if file.endswith(('.json', '.edf', '.vhdr', '.vmrk', '.eeg', '.set', '.fdt', '.bdf', 
                             '.nii', '.nii.gz', '.zip', '.tsv', '.tsv.gz', '.pcd', '.tsa', 
                             '.tst', '.tsm', '.tsp', '.wfb', '.yml', '.log')):
                size = os.path.getsize(full_path)
                filename = os.path.relpath(full_path, path).replace("\\", "/")
                file_info.append({"path": filename, "contentbytesize": size})
            
            # Include BIDS-standard plain text files (no extension)
            elif file in ('README', 'CHANGES', 'LICENSE', 'CITATION'):
                size = os.path.getsize(full_path)
                filename = os.path.relpath(full_path, path).replace("\\", "/")
                file_info.append({"path": filename, "contentbytesize": size})
    
    if savelist == 1:
        destination_path = os.path.join(os.getcwd(), "file_list.jsonl")
        with open(destination_path, "w") as f:
            for item in file_info:
                json.dump(item, f)
                f.write("\n")  # Add newline after each JSON object
    
    return file_info