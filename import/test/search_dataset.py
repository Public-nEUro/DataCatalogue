#!/usr/bin/env python3
"""
Search for dataset files in PN000011/V1 directory
"""

import os
import json

def search_dataset_files():
    base_path = r"d:\PublicnEUro\DataCatalogue\metadata\PN000011 A dataset of clinical pediatric brain MRI with and without motion correction\V1"
    
    print(f"🔍 Searching for dataset files in:")
    print(f"   {base_path}")
    print("=" * 80)
    
    dataset_files = []
    total_files = 0
    
    # Walk through all subdirectories
    for root, dirs, files in os.walk(base_path):
        for file in files:
            if file.endswith('.json'):
                total_files += 1
                file_path = os.path.join(root, file)
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    # Check if this is a dataset file
                    if isinstance(data, dict) and data.get('type', '').lower() == 'dataset':
                        dataset_files.append(file_path)
                        print(f"✅ DATASET FOUND: {file_path}")
                        
                        # Print some details
                        print(f"   📋 Dataset ID: {data.get('dataset_id', 'N/A')}")
                        print(f"   📋 Name: {data.get('name', 'N/A')}")
                        print(f"   📋 Version: {data.get('dataset_version', 'N/A')}")
                        
                        if 'authors' in data:
                            print(f"   👥 Authors: {len(data['authors'])} author(s)")
                        
                        print()
                        
                except (json.JSONDecodeError, UnicodeDecodeError, Exception) as e:
                    # Skip files that can't be read or parsed
                    continue
    
    print(f"📊 Summary:")
    print(f"   Total JSON files examined: {total_files}")
    print(f"   Dataset files found: {len(dataset_files)}")
    
    if dataset_files:
        print(f"\n📁 Dataset files:")
        for df in dataset_files:
            rel_path = os.path.relpath(df, base_path)
            print(f"   {rel_path}")
    else:
        print("   ❌ No dataset files found")

if __name__ == "__main__":
    search_dataset_files()
