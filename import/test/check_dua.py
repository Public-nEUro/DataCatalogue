import json

with open('PublicnEUro_test.jsonl', 'r', encoding='utf-8') as f:
    data = json.load(f)

print("Checking additional_display sections:")
for item in data.get('additional_display', []):
    print(f"- {item['name']}")
    if 'DUA' in item['name']:
        print("  DUA content found!")
        dua_content = item.get('content', {})
        print(f"  Restrictions: {len(dua_content.get('Restrictions', []))} items")
        print(f"  Terms: {len(dua_content.get('Terms', []))} items")
        if dua_content.get('Terms'):
            terms_preview = dua_content['Terms'][0][:100] + "..." if len(dua_content['Terms'][0]) > 100 else dua_content['Terms'][0]
            print(f"  Terms preview: {terms_preview}")
