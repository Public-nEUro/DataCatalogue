#!C:\Users\cpernet\AppData\Local\Programs\Python\Python312\python.exe
# -*- coding: utf-8 -*-
"""
@author: martin norgaard and cyril pernet
"""

import os
import json  # Import the json module

def get_file_info(path, savelist):
  """
  This function walks through a directory structure and returns a list of dictionaries containing full path, file name, and size.

  Args:
      path: The path to the directory to start searching from.

  Returns:
      A list of dictionaries, where each dictionary contains "full_path", "name", and "size" keys for each file and directory, excluding all files and directories within the 'source' and 'code' subdirectories.
  """
  file_info = []
  for root, dirs, files in os.walk(path):
    # Exclude 'code' directory completely
    if "code" in dirs:
      dirs.remove("code")

    # Process directories
    for directory in dirs:
      full_path = os.path.join(root, directory)
      # Only include directories within 'source'
      if root.endswith("sourcedata"):
        size = sum(os.path.getsize(os.path.join(dirpath, filename)) 
          for dirpath, _, filenames in os.walk(full_path) for filename in filenames)
        dirname = os.path.join("sourcedata", directory)
        file_info.append({"path": dirname, "contentbytesize": size})
        
    # Process files
    for file in files:
      full_path = os.path.join(root, file)
      # Include files with ".json" or ".nii[.gz]" extensions
      if file.endswith(('.json', '.nii', '.nii.gz')):
        size = os.path.getsize(full_path)
        filename = os.path.join(os.path.relpath(full_path, path), file)
        file_info.append({"path": filename, "contentbytesize": size})
    
  if savelist == 1:
    destination_path = os.path.join(path, "file_list.jsonl")
    with open(destination_path, "w") as f:
      for item in file_info:
        json.dump(item, f)
        f.write("\n")  # Add newline after each JSON object


  return file_info

