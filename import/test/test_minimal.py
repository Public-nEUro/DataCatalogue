import pandas as pd

# Simple test to see if the cleanup function logic is working
test_data = {
    "funding": [
        {"name": "Elsass foundation", "identifier": "18-3-0147"}, 
        {"name": "Novo Nordisk and Novozymes Talent Program", "identifier": pd.NA}
    ]
}

def remove_nan_and_na_values(data):
    if isinstance(data, dict):
        cleaned = {}
        for key, value in data.items():
            if pd.isna(value):
                continue
            elif isinstance(value, str) and value.strip().lower() in ['n.a.', 'na', 'n/a', '']:
                continue
            elif isinstance(value, (dict, list)):
                cleaned_value = remove_nan_and_na_values(value)
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
                if cleaned_item is not None and cleaned_item != {} and cleaned_item != []:
                    cleaned.append(cleaned_item)
        return cleaned
    else:
        return data

print("Before cleanup:")
print(test_data)

cleaned = remove_nan_and_na_values(test_data)
print("\nAfter cleanup:")
print(cleaned)

# Test JSON serialization
import json
print("\nJSON serializable:")
print(json.dumps(cleaned, indent=2))
