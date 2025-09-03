import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from export_xlsx import parse_excel_metadata, validate_metadata

# Parse test file
metadata = parse_excel_metadata('PublicnEUro_test.xlsx')

# Check validation
validation_errors = validate_metadata(metadata)

print("Validation Results:")
print("=" * 40)
for category, issues in validation_errors.items():
    if issues:
        print(f"{category}: {len(issues)} issues")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print(f"{category}: OK")

print("\nKeywords:", metadata.get('keywords', 'MISSING'))
print("BIDS version:", metadata.get('detailed_metadata', {}).get('content', {}).get('bids_version', 'MISSING'))
