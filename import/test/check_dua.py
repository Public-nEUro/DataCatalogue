import json
import os
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_dua_content():
    """Test DUA content extraction with proper file cleanup"""
    
    # Clean up existing files
    output_files = ['PublicnEUro_test.xml', 'PublicnEUro_test.jsonl']
    for file in output_files:
        if os.path.exists(file):
            os.remove(file)
            print(f"Removed existing {file}")
    
    # Generate fresh output
    try:
        from export_xlsx import export_xlsx_to_both
        print("Generating fresh test output...")
        export_xlsx_to_both('PublicnEUro_test.xlsx')
        print("Export completed successfully")
    except Exception as e:
        print(f"Export failed: {e}")
        return
    
    # Check the DUA content
    if not os.path.exists('PublicnEUro_test.jsonl'):
        print("ERROR: JSONL file not found")
        return
        
    with open('PublicnEUro_test.jsonl', 'r', encoding='utf-8') as f:
        data = json.load(f)

    print("\nChecking additional_display sections:")
    for item in data.get('additional_display', []):
        print(f"- {item['name']}")
        if 'DUA' in item['name']:
            print("  DUA content found!")
            dua_content = item.get('content', {})
            print(f"  Restrictions: {len(dua_content.get('Restrictions', []))} items")
            print(f"  Terms: {len(dua_content.get('Terms', []))} items")
            
            if dua_content.get('Restrictions'):
                print(f"  Restrictions content: {dua_content['Restrictions'][0]}")
            
            if dua_content.get('Terms'):
                terms_preview = dua_content['Terms'][0][:100] + "..." if len(dua_content['Terms'][0]) > 100 else dua_content['Terms'][0]
                print(f"  Terms preview: {terms_preview}")

if __name__ == "__main__":
    test_dua_content()
