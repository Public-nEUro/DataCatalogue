#!/usr/bin/env python3

# Test running process_file_metadata with the specified parameters
import sys
import os
import json

# Add parent directory to path to import the function
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

from file_metadata_utils import process_file_metadata

print("=== Running process_file_metadata with specified parameters ===")

# Parameters as requested
dataset_jsonl = r'D:\PublicnEUro\DataCatalogue\import\test\PublicnEUro_test.jsonl'
file_list_source = r'D:\PublicnEUro\DataCatalogue\import\test\fake_files'
source_name = 'test'
agent_name = 'test'

print(f"Dataset JSONL: {dataset_jsonl}")
print(f"File list source: {file_list_source}")
print(f"Source name: {source_name}")
print(f"Agent name: {agent_name}")

# Check if the dataset JSONL file exists
if os.path.exists(dataset_jsonl):
    print(f"✅ Dataset JSONL file exists")
    
    # Show its contents
    with open(dataset_jsonl, 'r', encoding='utf-8') as f:
        dataset_content = json.load(f)
    print(f"Dataset info: {dataset_content.get('name', 'N/A')} (ID: {dataset_content.get('dataset_id', 'N/A')})")
else:
    print(f"❌ Dataset JSONL file not found: {dataset_jsonl}")

# Check if the fake_files directory exists
if os.path.exists(file_list_source):
    print(f"✅ Source directory exists")
    
    # Show what files are in there
    import glob
    all_files = []
    for root, dirs, files in os.walk(file_list_source):
        for file in files:
            full_path = os.path.join(root, file)
            rel_path = os.path.relpath(full_path, file_list_source)
            all_files.append(rel_path)
    
    print(f"Files in source directory ({len(all_files)} total):")
    for file in sorted(all_files):
        print(f"  - {file}")
else:
    print(f"❌ Source directory not found: {file_list_source}")

# Run the function
print(f"\n=== Executing process_file_metadata ===")
try:
    output_file = process_file_metadata(
        dataset_jsonl=dataset_jsonl,
        file_list_source=file_list_source,
        source_name=source_name,
        agent_name=agent_name
    )
    
    print(f"✅ SUCCESS: Output file created: {output_file}")
    
    # Analyze the output
    with open(output_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    print(f"Output contains {len(lines)} entries")
    
    # Show entries that contain .log files
    log_entries = []
    for i, line in enumerate(lines, 1):
        try:
            entry = json.loads(line)
            if 'path' in entry and '.log' in entry['path']:
                log_entries.append((i, entry))
        except json.JSONDecodeError:
            continue
    
    if log_entries:
        print(f"\n.log files found in output ({len(log_entries)}):")
        for line_num, entry in log_entries:
            print(f"  Line {line_num}: {entry['path']} ({entry.get('contentbytesize', 0)} bytes)")
    else:
        print(f"\nNo .log files found in output")
    
    # Show first few entries as examples
    print(f"\nFirst 3 entries:")
    for i, line in enumerate(lines[:3], 1):
        try:
            entry = json.loads(line)
            print(f"  {i}. {entry.get('path', 'N/A')} (type: {entry.get('type', 'N/A')})")
        except json.JSONDecodeError:
            print(f"  {i}. [Invalid JSON]")
    
except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

print(f"\n=== Test completed ===")
