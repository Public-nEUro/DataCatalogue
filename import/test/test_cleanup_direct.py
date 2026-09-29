#!/usr/bin/env python3

# Test the cleanup function directly on sample data
import pandas as pd
import json

# Sample data that mimics what we expect from the funding parsing
sample_funding = [
    {"name": "Elsass foundation", "identifier": "18-3-0147"}, 
    {"name": "Novo Nordisk and Novozymes Talent Program", "identifier": pd.NA}
]

sample_dataset_info = {
    "field1": "value1",
    "field2": "n.a.",
    "field3": pd.NA,
    "field4": "normal value"
}

# The cleanup function from the export_xlsx.py
def remove_nan_and_na_values(data):
    """
    Recursively remove key-value pairs where the value is NaN, 'n.a.', or other meaningless values.
    """
    if isinstance(data, dict):
        cleaned = {}
        for key, value in data.items():
            # Skip keys with NaN values
            if pd.isna(value):
                print(f"Removing key '{key}' with NaN value")
                continue
            # Skip keys with string values that are meaningless
            elif isinstance(value, str) and value.strip().lower() in ['n.a.', 'na', 'n/a', '']:
                print(f"Removing key '{key}' with value '{value}'")
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
                print(f"Removing list item with NaN value")
                continue
            elif isinstance(item, str) and item.strip().lower() in ['n.a.', 'na', 'n/a', '']:
                print(f"Removing list item with value '{item}'")
                continue
            else:
                cleaned_item = remove_nan_and_na_values(item)
                # Only include non-empty items
                if cleaned_item is not None and cleaned_item != {} and cleaned_item != []:
                    cleaned.append(cleaned_item)
        return cleaned
    else:
        return data

print("Testing cleanup function...")
print("\n1. Original funding data:")
print(json.dumps(sample_funding, indent=2, default=str))

print("\n2. Cleaned funding data:")
cleaned_funding = remove_nan_and_na_values(sample_funding)
print(json.dumps(cleaned_funding, indent=2))

print("\n3. Original dataset info:")
print(json.dumps(sample_dataset_info, indent=2, default=str))

print("\n4. Cleaned dataset info:")
cleaned_dataset_info = remove_nan_and_na_values(sample_dataset_info)
print(json.dumps(cleaned_dataset_info, indent=2))

print("\n✅ Cleanup function test completed successfully!")
