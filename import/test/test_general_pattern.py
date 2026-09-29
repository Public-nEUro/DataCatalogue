"""
Test the find_catalogue_set_file.py with both generic PN*/V* and specific PN000011*/V1 patterns
"""

import sys
import os

# Add parent directory to path for imports
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)
sys.path.insert(0, parent_dir)

def test_patterns():
    print("🧪 Testing find_catalogue_set_file.py with different patterns")
    print("=" * 60)
    
    try:
        from find_catalogue_set_file import find_catalogue_set_file
        
        # Test 1: Generic pattern PN*/V* (finds all datasets)
        print("🚀 Test 1: Generic pattern PN*/V*")
        results_all = find_catalogue_set_file('PN*/V*', verbose=False)
        print(f"✅ Found {len(results_all)} datasets total")
        
        # Test 2: Specific pattern PN000011*/V1 (finds specific dataset)
        print("\n🚀 Test 2: Specific pattern PN000011*/V1")
        results_specific = find_catalogue_set_file('PN000011*/V1', verbose=False)
        
        if results_specific:
            print(f"✅ Found {len(results_specific)} PN000011 dataset(s)")
            for key, info in results_specific.items():
                print(f"   📁 {key}")
                print(f"      Directory: {info['directory']}")
                print(f"      Version: {info['version']}")
                print(f"      Path: {info['relative_path']}")
                if 'metadata' in info:
                    metadata = info['metadata']
                    print(f"      Name: {metadata.get('name', 'N/A')}")
                    print(f"      Dataset ID: {metadata.get('dataset_id', 'N/A')}")
        else:
            print("❌ PN000011 dataset not found")
        
        # Test 3: Show that the function works generically
        print(f"\n📊 Summary:")
        print(f"   - Generic PN*/V* found: {len(results_all)} datasets")
        print(f"   - Specific PN000011*/V1 found: {len(results_specific)} datasets")
        
        # Verify PN000011 is in the generic results
        pn000011_in_all = any('PN000011' in info['directory'] for info in results_all.values())
        print(f"   - PN000011 included in generic search: {'✅ YES' if pn000011_in_all else '❌ NO'}")
        
        return results_all, results_specific
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None, None

if __name__ == "__main__":
    test_patterns()
