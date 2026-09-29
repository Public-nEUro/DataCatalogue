#!/usr/bin/env python3
"""
Compare the backup XML file with the current XML file to identify differences
"""

import os
import sys
import xml.etree.ElementTree as ET
from xml.dom import minidom

# Get the directory where this script is located
script_dir = os.path.dirname(os.path.abspath(__file__))
# Get the import directory (parent of script if in subfolder, or script_dir itself)
import_dir = script_dir if os.path.basename(script_dir) == 'import' else os.path.dirname(script_dir)

def normalize_xml(file_path):
    """Parse and normalize XML for comparison"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Parse and pretty print to normalize formatting
    root = ET.fromstring(content)
    rough_string = ET.tostring(root, encoding='unicode')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="    ")

def compare_xml_files(file1, file2):
    """Compare two XML files and identify differences"""
    print("XML FILE COMPARISON")
    print("=" * 60)
    
    if not os.path.exists(file1):
        print(f"❌ File 1 not found: {file1}")
        return
    
    if not os.path.exists(file2):
        print(f"❌ File 2 not found: {file2}")
        return
    
    print(f"Backup file:  {file1}")
    print(f"Current file: {file2}")
    print()
    
    # Parse both files
    try:
        tree1 = ET.parse(file1)
        tree2 = ET.parse(file2)
        root1 = tree1.getroot()
        root2 = tree2.getroot()
    except ET.ParseError as e:
        print(f"❌ XML parsing error: {e}")
        return
    
    # Key elements to compare
    comparisons = [
        ("DOI", ".//doi"),
        ("Timestamp", ".//timestamp"),
        ("Resource URL", ".//resource"),
        ("Publication Date", ".//publication_date"),
        ("Title", ".//titles/title"),
        ("Subtitle", ".//titles/subtitle"),
        ("Description", ".//description"),
        ("Authors", ".//contributors/person_name")
    ]
    
    differences_found = False
    
    for name, xpath in comparisons:
        if name == "Authors":
            # Special handling for multiple authors
            authors1 = root1.findall(xpath)
            authors2 = root2.findall(xpath)
            
            if len(authors1) != len(authors2):
                print(f"❌ {name}: Different number of authors")
                print(f"   Backup: {len(authors1)} authors")
                print(f"   Current: {len(authors2)} authors")
                differences_found = True
            else:
                for i, (auth1, auth2) in enumerate(zip(authors1, authors2)):
                    given1 = auth1.find('given_name').text if auth1.find('given_name') is not None else ""
                    surname1 = auth1.find('surname').text if auth1.find('surname') is not None else ""
                    given2 = auth2.find('given_name').text if auth2.find('given_name') is not None else ""
                    surname2 = auth2.find('surname').text if auth2.find('surname') is not None else ""
                    
                    if given1 != given2 or surname1 != surname2:
                        print(f"❌ Author {i+1}: Different")
                        print(f"   Backup: {given1} {surname1}")
                        print(f"   Current: {given2} {surname2}")
                        differences_found = True
                    else:
                        print(f"✓ Author {i+1}: {given1} {surname1} (same)")
        
        elif name == "Publication Date":
            # Special handling for publication date
            date1 = root1.find(xpath)
            date2 = root2.find(xpath)
            
            if date1 is not None and date2 is not None:
                month1 = date1.find('month').text if date1.find('month') is not None else ""
                day1 = date1.find('day').text if date1.find('day') is not None else ""
                year1 = date1.find('year').text if date1.find('year') is not None else ""
                
                month2 = date2.find('month').text if date2.find('month') is not None else ""
                day2 = date2.find('day').text if date2.find('day') is not None else ""
                year2 = date2.find('year').text if date2.find('year') is not None else ""
                
                date_str1 = f"{year1}-{month1}-{day1}"
                date_str2 = f"{year2}-{month2}-{day2}"
                
                if date_str1 != date_str2:
                    print(f"❌ {name}: Different")
                    print(f"   Backup: {date_str1}")
                    print(f"   Current: {date_str2}")
                    differences_found = True
                else:
                    print(f"✓ {name}: {date_str1} (same)")
        
        else:
            # Standard element comparison
            elem1 = root1.find(xpath)
            elem2 = root2.find(xpath)
            
            text1 = elem1.text.strip() if elem1 is not None and elem1.text else ""
            text2 = elem2.text.strip() if elem2 is not None and elem2.text else ""
            
            if text1 != text2:
                print(f"❌ {name}: Different")
                print(f"   Backup: '{text1}'")
                print(f"   Current: '{text2}'")
                differences_found = True
            else:
                print(f"✓ {name}: Same")
    
    print("\n" + "=" * 60)
    if not differences_found:
        print("✅ FILES ARE IDENTICAL (except for timestamp differences)")
    else:
        print("⚠️  DIFFERENCES FOUND BETWEEN FILES")
    print("=" * 60)

# Compare the files using absolute paths
backup_file = os.path.join(import_dir, "data_import", "PN000011 Clinical Pediatric MRI with and without Motion Correction", "PublicNeuro_PN000011_backup.xml")
current_file = os.path.join(import_dir, "data_import", "PN000011 Clinical Pediatric MRI with and without Motion Correction", "PublicnEUro_PN000011.xml")

print(f"Looking for files in: {import_dir}")
print(f"Backup file: {backup_file}")
print(f"Current file: {current_file}")
print()

compare_xml_files(backup_file, current_file)
