#!/usr/bin/env python3

# Final test: export test files and validate results including date handling
import os
import json
import sys
import datetime

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))  # Add parent directory

print("Starting export test with cleanup function and date handling...")

# Import the updated export function
try:
    from export_xlsx import export_xlsx_to_jsonl
    print("Successfully imported export function")
    
    # Test with the test file that we know has date information
    test_file = "PublicnEUro_test.xlsx"
    if os.path.exists(test_file):
        print(f"📄 Testing date functionality with: {test_file}")
        
        try:
            test_output = export_xlsx_to_jsonl(test_file, 'date_test_output.jsonl', skip_validation=True)
            print(f"✅ Test export completed: {test_output}")
            
            # Validate results
            with open('date_test_output.jsonl', 'r', encoding='utf-8') as f:
                content = f.read()
                
            print("\n" + "="*60)
            print("VALIDATION RESULTS")
            print("="*60)
            
            # Check for NaN
            if "NaN" in content:
                print("❌ FAIL: Still contains NaN")
            else:
                print("✅ PASS: No NaN found")
                
            # Check for n.a.
            na_count = content.count('"n.a."')
            if na_count > 0:
                print(f"ℹ️  INFO: Found {na_count} 'n.a.' entries (may be in nested content)")
            else:
                print("✅ PASS: No 'n.a.' entries found")
                
            # Parse JSON
            try:
                data = json.loads(content)
                print("✅ PASS: Valid JSON structure")
                
                print("\n" + "-"*40)
                print("DATE HANDLING VALIDATION")
                print("-"*40)
                
                # Check date fields
                date_created = data.get('dateCreated')
                date_modified = data.get('dateModified')
                
                print(f"📅 dateCreated: {date_created}")
                print(f"📅 dateModified: {date_modified}")
                
                if date_modified:
                    print("✅ PASS: dateModified field found")
                else:
                    print("⚠️  WARN: No dateModified field (check if 'last-updated' exists in Excel)")
                
                # Check metadata_sources for source_time
                metadata_sources = data.get('metadata_sources', {})
                sources = metadata_sources.get('sources', [])
                
                print(f"\n📊 Metadata sources: {len(sources)} found")
                
                has_source_time = False
                for i, source in enumerate(sources):
                    source_name = source.get('source_name', 'Unknown')
                    agent_name = source.get('agent_name', 'Unknown')
                    source_time = source.get('source_time')
                    
                    print(f"  Source {i+1}:")
                    print(f"    📛 source_name: {source_name}")
                    print(f"    👤 agent_name: {agent_name}")
                    
                    if source_time:
                        has_source_time = True
                        try:
                            dt = datetime.datetime.fromtimestamp(source_time)
                            human_date = dt.strftime("%Y-%m-%d %H:%M:%S")
                            print(f"    ⏰ source_time: {source_time} ({human_date})")
                            print("    ✅ Will display 'Last updated' in catalog")
                        except (ValueError, TypeError) as e:
                            print(f"    ❌ Invalid timestamp: {source_time} - {e}")
                    else:
                        print(f"    ⚠️  source_time: Missing - will show 'Last updated: unknown'")
                
                if has_source_time:
                    print("\n✅ PASS: At least one source has source_time for date display")
                else:
                    print("\n❌ FAIL: No source_time found - dates will show as 'unknown' in catalog")
                    print("   💡 TIP: Add 'last-updated' field to Excel dataset_info sheet")
                
                print("\n" + "-"*40)
                print("CONTENT VALIDATION")
                print("-"*40)
                
                # Check funding specifically
                if 'funding' in data:
                    funding_count = len(data['funding'])
                    print(f"💰 Funding entries: {funding_count}")
                    for i, fund in enumerate(data['funding']):
                        name = fund.get('name', 'Unknown')
                        identifier = fund.get('identifier', 'No identifier')
                        print(f"  {i+1}. {name} - {identifier}")
                else:
                    print("💰 No funding section found")
                    
                # Check essential fields
                essential_fields = ['name', 'description', 'dataset_id', 'dataset_version', 'type']
                missing_fields = [field for field in essential_fields if not data.get(field)]
                
                if missing_fields:
                    print(f"⚠️  Missing essential fields: {', '.join(missing_fields)}")
                else:
                    print("✅ All essential fields present")
                    
                print("\n📊 Final Date Test Results:")
                print(f"  Dataset: {data.get('name', 'Unknown')}")
                print(f"  dateModified: {data.get('dateModified')}")
                
                test_sources = data.get('metadata_sources', {}).get('sources', [])
                for source in test_sources:
                    if source.get('source_time'):
                        dt = datetime.datetime.fromtimestamp(source['source_time'])
                        print(f"  source_time: {dt.strftime('%Y-%m-%d %H:%M:%S')}")
                        print("  ✅ Date handling working correctly!")
                        break
                    
            except json.JSONDecodeError as e:
                print(f"❌ FAIL: JSON parsing error: {e}")
                
        except Exception as e:
            print(f"❌ Test export failed: {e}")
            import traceback
            traceback.print_exc()
            
    else:
        print(f"❌ Test file not found: {test_file}")
        print("💡 Make sure PublicnEUro_test.xlsx exists in the test directory")
        
except Exception as e:
    print(f"❌ Error during export: {e}")
    import traceback
    traceback.print_exc()
    
print("\n" + "="*60)
print("TEST COMPLETED")
print("="*60)