import os
import json

def find_jsonl_dataset(folder):
    """
    Finds a JSON file containing '"type": "dataset"'.
    If the folder is 'metadata', it lists all datasets and returns a dictionary.
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
