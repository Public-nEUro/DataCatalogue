#!/usr/bin/env python3

# Test script to verify that process_file_metadata processes .log files correctly
import sys
import os
import json

# Add parent directory to path to import the function
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

from file_metadata_utils import process_file_metadata, get_file_info

# Test 1: Check if get_file_info finds the .log file
print("=== Test 1: get_file_info scan ===")
fake_files_dir = "fake_files"
file_info = get_file_info(fake_files_dir)

log_files = [f for f in file_info if f['path'].endswith('.log')]
print(f"Found {len(log_files)} .log files:")
for log_file in log_files:
    print(f"  - {log_file['path']} (size: {log_file['contentbytesize']} bytes)")

# Test 2: Check specific stuff.log file
stuff_log_path = "source/sub-01/stuff.log"
# Handle Windows path separators
stuff_log_path_windows = "source\\sub-01\\stuff.log"
stuff_log_found = any(f['path'] == stuff_log_path or f['path'] == stuff_log_path_windows for f in file_info)
print(f"\nstuff.log found: {stuff_log_found}")

if stuff_log_found:
    stuff_log_info = next(f for f in file_info if f['path'] in [stuff_log_path, stuff_log_path_windows])
    print(f"stuff.log details: {stuff_log_info}")
else:
    print("stuff.log NOT found - this indicates a problem!")

# Test 3: Full process_file_metadata test
print("\n=== Test 2: process_file_metadata with stuff.log ===")
try:
    # Create a minimal dataset JSONL for testing
    test_dataset_jsonl = {
        "type": "dataset",
        "name": "Test Dataset",
        "dataset_id": "test_dataset",
        "dataset_version": "V1",
        "doi": "10.test/test",
        "description": "Test dataset for log file processing"
    }
    
    with open("test_dataset.jsonl", "w") as f:
        json.dump(test_dataset_jsonl, f)
    
    # Process file metadata
    output_file = process_file_metadata(
        dataset_jsonl="test_dataset.jsonl",
        file_list_source=fake_files_dir,
        source_name="TestSource",
        agent_name="TestAgent"
    )
    
    print(f"Output file created: {output_file}")
    
    # Check if the output contains stuff.log
    with open(output_file, 'r') as f:
        output_content = f.read()
    
    if 'stuff.log' in output_content:
        print("✅ SUCCESS: stuff.log found in processed output!")
        
        # Parse and show the specific entry for stuff.log
        with open(output_file, 'r') as f:
            for line_num, line in enumerate(f, 1):
                try:
                    entry = json.loads(line)
                    if 'path' in entry and 'stuff.log' in entry['path']:
                        print(f"stuff.log entry (line {line_num}):")
                        print(f"  Path: {entry.get('path', 'N/A')}")
                        print(f"  Size: {entry.get('contentbytesize', 'N/A')} bytes")
                        print(f"  Type: {entry.get('type', 'N/A')}")
                        break
                except json.JSONDecodeError:
                    continue
    else:
        print("❌ FAIL: stuff.log NOT found in processed output!")
    
    # Clean up test file
    os.remove("test_dataset.jsonl")
    
except Exception as e:
    print(f"❌ Error during process_file_metadata test: {e}")
    import traceback
    traceback.print_exc()

print("\n=== Test completed ===")
