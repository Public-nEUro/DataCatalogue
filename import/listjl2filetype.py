# -*- coding: utf-8 -*-
"""
Created on Tue Jul 30 15:02:24 2024

@author: Cyril Pernet & Martin Norgaard
"""

import os
import json
import re

def listjl2filetype(datasetjl, listjl, source_name, agent_name):
    # 1 - Get datasetjl
    if not os.path.exists(datasetjl):
        raise FileNotFoundError(f'dataset.json file {datasetjl} not found')

    with open(datasetjl, 'r') as f:
        dataset_info = json.loads(f.read())

    # Add metadata sources if not already present
    if 'metadata_sources' not in dataset_info:
        dataset_info['metadata_sources'] = {
            'sources': {
                'source_name': source_name,
                'source_version': dataset_info.get('dataset_version', ''),
                'agent_name': agent_name
            }
        }

    local_jsonwrite(f"{dataset_info['name'].replace(' ', '')}.jsonl", dataset_info)

    # 2 - Get listjl
    with open(listjl, 'r') as f:
        files_info = f.readlines()

    # Edit items and append
    for file_info in files_info:
        file_info_dict = json.loads(file_info.strip())

        # Assuming file_info is a dictionary with keys 'path' and 'contentbytesize'
        if 'path' in file_info_dict and 'contentbytesize' in file_info_dict:
            item = {
                'type': 'file',
                'dataset_id': dataset_info['dataset_id'],
                'dataset_version': dataset_info['dataset_version'],
                'path': file_info_dict['path'].replace("\\", "/"),  # Replace backslashes with forward slashes
                'contentbytesize': float(file_info_dict['contentbytesize']),
                'metadata_sources': {
                    'sources': {
                        'source_name': source_name,
                        'source_version': dataset_info['dataset_version'],
                        'agent_name': agent_name
                    }
                }
            }
            local_jsonwrite(f"{dataset_info['name'].replace(' ', '')}.jsonl", item)
        else:
            print(f"Pattern not found in the following file info: {file_info}")

    # Fix known issues
    fix_metadata_sources(f"{dataset_info['name'].replace(' ', '')}.jsonl")

def fix_metadata_sources(filename):
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

    os.remove(filename)
    with open(filename, 'w') as f:
        f.writelines(updated_lines)

def local_jsonwrite(filename, json_obj):
    json_str = json.dumps(json_obj, ensure_ascii=False)
    # Fix double slashes and other unwanted stuff
    json_str = re.sub(r'\\\\', '/', json_str)  # Ensure forward slashes
    json_str = re.sub(r'//', '/', json_str)    # Ensure forward slashes

    mode = 'a' if os.path.exists(filename) else 'w'
    with open(filename, mode) as f:
        f.write(json_str + '\n')

# Example usage:
# listjl2filetype('OpenNeuroPETPhantoms_datasetonly.jsonl', 'file_list.jsonl', 'OpenNeuro_PET', 'Cyril Pernet')