#!/usr/bin/env python3
"""
Fix UCB dataset JSONL by adding hasPart and isPartOf fields
"""
import json

def fix_ucb_dataset():
    input_file = "/openneuropet/DataCatalogue/import/data_import/PNC00001 UCB-J_consortium/PN000005 UCBJ-Leuven1/LeuvenPETUCB-Jdataset1incontrolparticipants.jsonl"
    
    # Read all lines
    with open(input_file, 'r') as f:
        lines = [line.strip() for line in f.readlines() if line.strip()]
    
    # Parse first line (dataset entry)
    dataset_entry = json.loads(lines[0])
    
    # Extract all file paths from remaining lines
    file_paths = []
    file_entries = []
    
    for line in lines[1:]:
        file_entry = json.loads(line)
        if file_entry.get('type') == 'file' and 'path' in file_entry:
            file_paths.append(file_entry['path'])
            file_entries.append(file_entry)
    
    # Add hasPart to dataset entry
    dataset_entry['hasPart'] = sorted(file_paths)
    
    # Add isPartOf to all file entries
    clean_dataset_id = dataset_entry['dataset_id']
    for file_entry in file_entries:
        file_entry['isPartOf'] = clean_dataset_id
    
    # Write back to file
    with open(input_file, 'w') as f:
        # Write dataset entry first
        f.write(json.dumps(dataset_entry, ensure_ascii=False) + '\n')
        
        # Write all file entries
        for file_entry in file_entries:
            f.write(json.dumps(file_entry, ensure_ascii=False) + '\n')
    
    print(f"Fixed dataset with {len(file_paths)} files")
    print(f"Added hasPart to dataset: {dataset_entry['name']}")
    print(f"Added isPartOf to {len(file_entries)} file entries")

if __name__ == "__main__":
    fix_ucb_dataset()