import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from export_xlsx import export_xlsx_to_both

try:
    xml_file, jsonl_file = export_xlsx_to_both('PublicnEUro_test.xlsx')
    print(f"SUCCESS: Files created:")
    print(f"  XML: {xml_file}")
    print(f"  JSONL: {jsonl_file}")
except Exception as e:
    print(f"ERROR: {e}")
