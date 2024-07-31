# -*- coding: utf-8 -*-
"""
Created on Tue Jul 30 15:02:24 2024

@author: cpernet
"""

import json
import os

def local_jsonwrite(filename, json_data):

    # Add indentation for readability (optional)
    indent = ""  # You can customize the indentation level here

    # Serialize the JSON data
    json_string = json.dumps(json_data, indent=indent, separators=(",", ": "))

    # Check if the file exists
    if not os.path.exists(filename):
        with open(filename, "w") as f:
            f.write(json_string)
    else:
        with open(filename, "a") as f:
            f.write(json_string)
            f.write("\n")  # Add a newline after each entry

def listjl2filetype(dataset_jl, list_jl, source_name, agent_name):
    """
    Reads a list.jsonl file and creates individual JSON files for each data item.

    This function mimics the behavior of the MATLAB function `listjl2filetype`.

    Args:
        dataset_jl (str): Path to the dataset.jsonl file.
        list_jl (str): Path to the list.jsonl file containing file information.
        source_name (str): Name of the data source.
        agent_name (str): Name of the agent who generated the data.
    """

    # Check if the dataset.jsonl file exists
    if not os.path.exists(dataset_jl):
        raise FileNotFoundError(f"Dataset file {dataset_jl} not found")

    # Read the dataset.jsonl file
    with open(dataset_jl, "r") as f:
        dataset_info = json.load(f)

    # Add metadata source information if it's missing
    if "metadata_sources" not in dataset_info:
        dataset_info["metadata_sources"] = {
            "sources": {"source_name": source_name, "source_version": dataset_info["dataset_version"], "agent_name": agent_name}
        }

    # Write the updated dataset information to a temporary file
    temp_dataset_file = f"{os.path.splitext(dataset_jl)[0]}.jsonl"
    local_jsonwrite(temp_dataset_file, dataset_info)

    # Read the list.jsonl file
    with open(list_jl, "r") as f:
        file_infos = [json.loads(line) for line in f]

    # Process each file information and write individual JSON files
    for file_info in file_infos:
        item = {
            "type": "file",
            "dataset_id": dataset_info["dataset_id"],
            "dataset_version": dataset_info["dataset_version"],
            "path": file_info["path"].replace("\\", "/").replace("//", "/"),  # Fix path separators
            "contentbytesize": int(file_info["contentbytesize"]),
            "metadata_sources": {
                "sources": {
                    "source_name": source_name,
                    "source_version": dataset_info["dataset_version"],
                    "agent_name": agent_name,
                }
            },
        }

        # Write the item information to a separate JSON file
        item_filename = f"{os.path.splitext(dataset_jl)[0]}.jsonl"
        local_jsonwrite(item_filename, item)