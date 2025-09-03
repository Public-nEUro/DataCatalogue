print("Testing export with detailed output...")

try:
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from export_xlsx import export_xlsx_to_both
    print("Function imported successfully")
    
    print("Calling export_xlsx_to_both...")
    result = export_xlsx_to_both('PublicnEUro_test.xlsx')
    print(f"Result: {result}")
    
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()

print("Script completed.")
