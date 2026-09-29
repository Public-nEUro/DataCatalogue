#!/usr/bin/env python3
"""
Test the integrated reorder functionality in find_catalogue_set_file.py
"""

import sys
import os

# Add parent directory to path for imports
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)
sys.path.insert(0, parent_dir)

from find_catalogue_set_file import find_catalogue_set_file

def test_reorder_integration():
    print("🧪 Testing integrated reorder functionality")
    print("=" * 60)
    
    # Test 1: Explicit reorder_children=False
    print("📋 Test 1: reorder_children=False")
    results = find_catalogue_set_file('PN000001*/V1', verbose=True, reorder_children=False)
    print(f"Result: Found {len(results)} dataset(s), no reordering")
    
    print("\n" + "="*60)
    
    # Test 2: Explicit reorder_children=True  
    print("📋 Test 2: reorder_children=True")
    results = find_catalogue_set_file('PN000001*/V1', verbose=True, reorder_children=True)
    print(f"Result: Found {len(results)} dataset(s), with reordering")
    
    print("\n✅ Integration tests completed!")

if __name__ == "__main__":
    test_reorder_integration()
