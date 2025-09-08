#!/usr/bin/env python3

# Test the refactored clean_data_structure function
import sys
import os
import json

# Add parent directory to path to import the refactored functions
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    from export_xlsx import clean_data_structure, filter_empty_values, clean_metadata_content
    import pandas as pd
    
    print("=== Testing Refactored Cleaning Functions ===")
    
    # Test data with various problematic values
    test_data = {
        "funding": [
            {"name": "Good Foundation", "identifier": "12345"},
            {"name": "Bad Foundation", "identifier": pd.NA},  # Should be removed
            {"name": "Another Foundation", "identifier": "n.a."}  # Should be removed
        ],
        "dataset_info": {
            "title": "Good Title",
            "description": "",  # Should be removed
            "keywords": ["keyword1", "keyword2"],
            "bad_field": "n.a.",  # Should be removed
            "empty_field": None,  # Should be removed
            "array_field": []  # Should be removed
        },
        "authors": [
            {"givenName": "John", "familyName": "Doe"},
            {"givenName": "", "familyName": ""},  # Should be removed
            {"givenName": "Jane", "familyName": "Smith"}
        ]
    }
    
    print("1. Original test data:")
    print(json.dumps(test_data, indent=2, default=str))
    
    # Test comprehensive mode (should remove NaN and n.a. values)
    print("\n2. Testing comprehensive mode:")
    cleaned_comprehensive = clean_data_structure(test_data, mode='comprehensive')
    print(json.dumps(cleaned_comprehensive, indent=2))
    
    # Test basic mode (should only remove basic empty values)
    print("\n3. Testing basic mode:")
    cleaned_basic = clean_data_structure(test_data, mode='basic')
    print(json.dumps(cleaned_basic, indent=2, default=str))
    
    # Test JSONL mode (should apply domain-specific rules)
    print("\n4. Testing JSONL mode:")
    cleaned_jsonl = clean_data_structure(test_data, mode='jsonl')
    print(json.dumps(cleaned_jsonl, indent=2))
    
    # Test legacy functions (backward compatibility)
    print("\n5. Testing legacy functions:")
    legacy_filter = filter_empty_values({"empty": "", "good": "value", "null": None})
    legacy_metadata = clean_metadata_content({"title": "Good", "bad": "n.a.", "empty": ""})
    
    print(f"Legacy filter_empty_values: {legacy_filter}")
    print(f"Legacy clean_metadata_content: {legacy_metadata}")
    
    print("\n✅ All tests completed successfully!")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
except Exception as e:
    print(f"❌ Error during testing: {e}")
    import traceback
    traceback.print_exc()
