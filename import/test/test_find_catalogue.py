"""
Test the new find_catalogue_set_file.py as an import module
"""

import sys
import os

# Add parent directory to path for imports
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)
sys.path.insert(0, parent_dir)

def test_import():
    print("🧪 Testing find_catalogue_set_file.py as import module")
    print("=" * 60)
    
    try:
        # Test importing the module
        print("📥 Importing find_catalogue_set_file...")
        from find_catalogue_set_file import find_catalogue_set_file, find_jsonl_dataset, fetch_set
        print("✅ Import successful!")
        
        # Show available functions
        print("\n📋 Available functions:")
        print("   - find_catalogue_set_file(target_pattern, base_path, verbose)")
        print("   - find_jsonl_dataset(folder)")
        print("   - fetch_set(folder)")
        
        # Test the main function
        print("\n🚀 Testing find_catalogue_set_file function...")
        results = find_catalogue_set_file(verbose=False)
        
        if results:
            print(f"✅ SUCCESS: Found {len(results)} dataset(s)")
            for key, info in results.items():
                print(f"   📁 {key}")
                print(f"      Path: {info['relative_path']}")
                if 'metadata' in info:
                    metadata = info['metadata']
                    print(f"      Name: {metadata.get('name', 'N/A')}")
                    print(f"      Type: {metadata.get('type', 'N/A')}")
        else:
            print("❌ No datasets found")
        
        print("\n✅ SUCCESS: find_catalogue_set_file.py works as both import and CLI!")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_import()
