"""
Test the updated find_catalogue_set_file function with different PN numbers
"""

import sys
import os

# Add parent directory to path for imports
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)
sys.path.insert(0, parent_dir)

from find_catalogue_set_file import find_catalogue_set_file as fs

def test_patterns():
    print("🧪 Testing Different PN Patterns")
    print("=" * 50)
    
    # Test patterns
    patterns = [
        "PN000001*/V1",
        "metadata/PN000001*/V1", 
        "PN000011*/V1",
        "metadata/PN000011*/V1"
    ]
    
    for pattern in patterns:
        print(f"\n🎯 Testing pattern: {pattern}")
        print("-" * 40)
        
        try:
            results = fs(pattern, verbose=False)
            
            if results:
                print(f"✅ Found {len(results)} dataset(s):")
                for key, info in results.items():
                    print(f"   📁 {key}")
                    print(f"      Directory: {info.get('directory', 'N/A')}")
                    print(f"      Version: {info.get('version', 'N/A')}")
                    print(f"      Path: {info['relative_path']}")
                    if 'metadata' in info:
                        metadata = info['metadata']
                        print(f"      Name: {metadata.get('name', 'N/A')}")
            else:
                print("❌ No datasets found")
                
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_patterns()
