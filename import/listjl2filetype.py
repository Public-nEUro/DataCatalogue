import json
import os

def listjl2filetype(datasetjl, listjl, source_name, agent_name):
    # 1 - get datasetjl
    if not os.path.exists(datasetjl):
        raise FileNotFoundError(f'dataset.json file {datasetjl} not found')
    
    with open(datasetjl, 'r') as file:
        dataset_info = json.load(file)
    
    local_jsonwrite(f"{dataset_info['name'].replace(' ', '')}.jsonl", dataset_info)

    # 2 - get listjl
    with open(listjl, 'r') as file:
        files_info = file.readlines()
    
    # edit items and append
    for file_info in files_info:
        file_info_json = json.loads(file_info)
        item = {
            "type": "file",
            "dataset_id": dataset_info["dataset_id"],
            "dataset_version": dataset_info["dataset_version"],
            "path": file_info_json["path"],
            "contentbytesize": int(file_info_json["contentbytesize"]),
            "metadata_sources": {
                "sources": {
                    "source_name": source_name,
                    "source_version": dataset_info["dataset_version"],
                    "agent_name": agent_name
                }
            }
        }
        local_jsonwrite(f"{dataset_info['name'].replace(' ', '')}.jsonl", item)

def local_jsonwrite(filename, json_obj):
    # Serialize a JSON (JavaScript Object Notation) structure
    
    json_str = json.dumps(json_obj, indent=4)
    
    mode = 'a' if os.path.exists(filename) else 'w'
    
    with open(filename, mode) as file:
        file.write(json_str)
        file.write('\n')

# Example usage
# listjl2filetype('dataset.jsonl', 'file_list.jsonl', 'OpenNeuro_PET', 'Cyril Pernet')
