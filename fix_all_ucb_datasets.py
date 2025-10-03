#!/usr/bin/env python3
"""
Fix all UCB-J dataset JSONL files by adding hasPart and isPartOf fields
"""
import json
import os

def fix_ucb_dataset(input_file):
    """Fix a single UCB dataset JSONL file"""
    print(f"Processing: {input_file}")
    
    # Read all lines
    with open(input_file, 'r') as f:
        lines = [line.strip() for line in f.readlines() if line.strip()]
    
    if not lines:
        print(f"  Empty file, skipping")
        return
    
    # Parse first line (dataset entry)
    try:
        dataset_entry = json.loads(lines[0])
    except json.JSONDecodeError:
        print(f"  Error parsing dataset entry, skipping")
        return
    
    # Check if it's a dataset entry
    if dataset_entry.get('type') != 'dataset':
        print(f"  First entry is not a dataset, skipping")
        return
    
    # Extract all file paths from remaining lines
    file_paths = []
    file_entries = []
    
    for line in lines[1:]:
        try:
            file_entry = json.loads(line)
            if file_entry.get('type') == 'file' and 'path' in file_entry:
                file_paths.append(file_entry['path'])
                file_entries.append(file_entry)
        except json.JSONDecodeError:
            continue
    
    if not file_paths:
        print(f"  No files found, skipping")
        return
    
    # Clean up dataset_id (remove trailing spaces)
    if 'dataset_id' in dataset_entry:
        dataset_entry['dataset_id'] = dataset_entry['dataset_id'].strip()
    
    # Add hasPart to dataset entry (only if not already present)
    if 'hasPart' not in dataset_entry:
        dataset_entry['hasPart'] = sorted(file_paths)
        print(f"  Added hasPart with {len(file_paths)} files")
    
    # Add isPartOf to all file entries
    clean_dataset_id = dataset_entry['dataset_id']
    updated_files = 0
    
    for file_entry in file_entries:
        # Clean dataset_id in file entries
        if 'dataset_id' in file_entry:
            file_entry['dataset_id'] = file_entry['dataset_id'].strip()
        
        # Add isPartOf if not already present
        if 'isPartOf' not in file_entry:
            file_entry['isPartOf'] = clean_dataset_id
            updated_files += 1
    
    print(f"  Added isPartOf to {updated_files} file entries")
    
    # Write back to file
    with open(input_file, 'w') as f:
        # Write dataset entry first
        f.write(json.dumps(dataset_entry, ensure_ascii=False) + '\n')
        
        # Write all file entries
        for file_entry in file_entries:
            f.write(json.dumps(file_entry, ensure_ascii=False) + '\n')
    
    print(f"  ✅ Fixed: {os.path.basename(input_file)}")

def main():
    """Fix all UCB-J datasets"""
    ucb_files = [
        "/openneuropet/DataCatalogue/import/data_import/PNC00001 UCB-J_consortium/PN000006_UCBJ-Leuven2/LeuvenPETUCB-Jdataset2incontrolparticipants.jsonl",
        "/openneuropet/DataCatalogue/import/data_import/PNC00001 UCB-J_consortium/PN000007_UCBJ-Leuven3/LeuvenPETUCB-Jdataset3incontrolparticipants.jsonl",
        "/openneuropet/DataCatalogue/import/data_import/PNC00001 UCB-J_consortium/PN000008_UCBJ-Leuven4/LeuvenPETUCB-Jdataset4incontrolparticipants.jsonl",
        "/openneuropet/DataCatalogue/import/data_import/PNC00001 UCB-J_consortium/PN000010_UCBJ-Leuven5/LeuvenPETUCB-Jdataset5incontrolparticipants.jsonl"
    ]
    
    print(f"🔧 Fixing {len(ucb_files)} UCB-J datasets...")
    
    for file_path in ucb_files:
        if os.path.exists(file_path):
            fix_ucb_dataset(file_path)
        else:
            print(f"❌ File not found: {file_path}")
    
    print("\n🎉 All UCB-J datasets have been fixed!")

if __name__ == "__main__":
    main()