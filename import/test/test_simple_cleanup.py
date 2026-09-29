#!/usr/bin/env python3

# Simple test of the cleanup function
import pandas as pd
import json

# Test data with NaN values
test_data = {
    "funding": [
        {"name": "Elsass foundation", "identifier": "18-3-0147"}, 
        {"name": "Novo Nordisk and Novozymes Talent Program", "identifier": pd.NA}
    ],
    "dataset_info": {
        "field1": "value1",
        "field2": "n.a.",
        "field3": pd.NA,
        "field4": "N/A"
    }
}

def remove_nan_and_na_values(data):
    """
    Recursively remove key-value pairs where the value is NaN, 'n.a.', or other meaningless values.
    """
    if isinstance(data, dict):
        cleaned = {}
        for key, value in data.items():
            # Skip keys with NaN values
            if pd.isna(value):
                continue
            # Skip keys with string values that are meaningless
            elif isinstance(value, str) and value.strip().lower() in ['n.a.', 'na', 'n/a', '']:
                continue
            # Recursively clean nested structures
            elif isinstance(value, (dict, list)):
                cleaned_value = remove_nan_and_na_values(value)
                # Only include if the cleaned structure is not empty
                if cleaned_value:
                    cleaned[key] = cleaned_value
            else:
                cleaned[key] = value
        return cleaned
    elif isinstance(data, list):
        cleaned = []
        for item in data:
            if pd.isna(item):
                continue
            elif isinstance(item, str) and item.strip().lower() in ['n.a.', 'na', 'n/a', '']:
                continue
            else:
                cleaned_item = remove_nan_and_na_values(item)
                # Only include non-empty items
                if cleaned_item is not None and cleaned_item != {} and cleaned_item != []:
                    cleaned.append(cleaned_item)
        return cleaned
    else:
        return data

# Test the function
print("Original data:")
print(json.dumps(test_data, indent=2, default=str))

print("\nCleaned data:")
cleaned_data = remove_nan_and_na_values(test_data)
print(json.dumps(cleaned_data, indent=2, default=str))
