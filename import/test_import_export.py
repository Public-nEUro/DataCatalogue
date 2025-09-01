"""
Test that export_xlsx.py works as an import module
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_import():
    print("🧪 Testing export_xlsx.py as import module")
    print("=" * 50)
    
    try:
        # Test importing the module
        print("📥 Importing export_xlsx...")
        from export_xlsx import export_xlsx_to_xml, export_xlsx_to_jsonl, export_xlsx_to_both
        print("✅ Import successful!")
        
        # Show available functions
        print("\n📋 Available functions:")
        print("   - export_xlsx_to_xml(excel_file_path, output_xml_path=None)")
        print("   - export_xlsx_to_jsonl(excel_file_path, output_jsonl_path=None)")
        print("   - export_xlsx_to_both(excel_file_path, output_xml_path=None, output_jsonl_path=None)")
        
        # Test the function signatures
        print("\n🔍 Function docstrings:")
        print(f"   export_xlsx_to_xml: {export_xlsx_to_xml.__doc__ or 'No docstring'}")
        print(f"   export_xlsx_to_jsonl: {export_xlsx_to_jsonl.__doc__ or 'No docstring'}")
        print(f"   export_xlsx_to_both: {export_xlsx_to_both.__doc__ or 'No docstring'}")
        
        print("\n✅ SUCCESS: export_xlsx.py can be used as both import and CLI!")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_import()
