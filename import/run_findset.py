"""
Run findset.py on metadata/PN000011*/V1
"""

import sys
import os

# Add current directory to path to import findset
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from findset import find_jsonl_dataset, fetch_set

def main():
    # Change to the script's directory first
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    print(f"📍 Working directory: {os.getcwd()}")
    
    # Change to the DataCatalogue directory (parent of import)
    base_path = os.path.dirname(script_dir)  # Go up one level from import to DataCatalogue
    os.chdir(base_path)
    print(f"📍 Changed to: {os.getcwd()}")
    
    # Target path pattern: metadata/PN000011*/V1
    metadata_path = "metadata"
    
    print("🔍 Running findset.py on metadata/PN000011*/V1")
    print("=" * 60)
    
    if not os.path.exists(metadata_path):
        print(f"❌ Metadata directory not found: {metadata_path}")
        return
    
    # Look for PN000011 directories
    pn000011_dirs = []
    for item in os.listdir(metadata_path):
        if item.startswith("PN000011"):
            pn000011_dirs.append(item)
    
    if not pn000011_dirs:
        print("❌ No PN000011 directories found")
        return
    
    print(f"📁 Found PN000011 directories: {pn000011_dirs}")
    
    # Process each PN000011 directory's V1 subdirectory
    for pn_dir in pn000011_dirs:
        pn_path = os.path.join(metadata_path, pn_dir)
        v1_path = os.path.join(pn_path, "V1")
        
        print(f"\n📂 Processing: {pn_dir}/V1")
        
        if not os.path.exists(v1_path):
            print(f"   ⚠️  V1 directory not found in {pn_dir}")
            continue
        
        # Use fetch_set to find dataset files in the V1 directory
        try:
            result = fetch_set(v1_path)
            if result != 'not found':
                print(f"   ✅ Dataset file found: {result}")
                
                # Try to read and display some info about the dataset
                try:
                    import json
                    with open(result, 'r', encoding='utf-8') as f:
                        dataset_data = json.load(f)
                    
                    print(f"   📋 Dataset info:")
                    print(f"      - Type: {dataset_data.get('type', 'N/A')}")
                    print(f"      - Name: {dataset_data.get('name', 'N/A')}")
                    print(f"      - ID: {dataset_data.get('dataset_id', 'N/A')}")
                    if 'version' in dataset_data:
                        print(f"      - Version: {dataset_data.get('version', 'N/A')}")
                except Exception as e:
                    print(f"   ⚠️  Could not read dataset details: {e}")
            else:
                print(f"   ❌ No dataset file found")
                
        except Exception as e:
            print(f"   ❌ Error processing {v1_path}: {e}")

if __name__ == "__main__":
    main()
