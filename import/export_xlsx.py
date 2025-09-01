#!/usr/bin/env python3
"""
Combined Excel to XML converter for PublicNeuro datasets.
This module combines xlsx2xml.py and xml_dict.json into a single importable function.
"""

import openpyxl
import pandas as pd
import xml.etree.ElementTree as ET
from datetime import datetime
import re
import os
import sys
import json

def extract_doi_suffix(doi_value):
    """
    Extract the suffix from a DOI, handling both full URLs and DOI format.
    Examples:
    - 'https://doi.org/10.70883/VMIF5895' -> 'VMIF5895'
    - 'http://dx.doi.org/10.70883/VMIF5895' -> 'VMIF5895'
    - '10.70883/VMIF5895' -> 'VMIF5895'
    - 'VMIF5895' -> 'VMIF5895'
    """
    if pd.isna(doi_value) or not doi_value:
        return "XXXX"
    
    doi_str = str(doi_value).strip()
    
    # If it's already just the suffix (no slash), return as is
    if '/' not in doi_str:
        return doi_str
    
    # Extract the last part after the final '/'
    parts = doi_str.split('/')
    return parts[-1] if parts[-1] else "XXXX"

def format_version(version_value):
    """
    Format version to ensure it's always V followed by a number.
    Examples:
    - 'V1' -> 'V1'
    - '1' -> 'V1'
    - 'VV1' -> 'V1'
    - 'V2.0' -> 'V2.0'
    - None -> 'VNone'
    """
    if pd.isna(version_value) or not version_value:
        return "VNone"
    
    version_str = str(version_value).strip()
    
    # If it already starts with V, check for double V and fix
    if version_str.startswith('V'):
        # Remove any extra V's at the beginning
        while version_str.startswith('VV'):
            version_str = version_str[1:]  # Remove one V
        return version_str
    
    # If it doesn't start with V, add it
    return f"V{version_str}"

def parse_keywords(keywords_value):
    """
    Parse keywords with improved robustness:
    - If commas are present, split by commas
    - Otherwise, split by spaces
    - Trim whitespace and filter empty values
    
    Examples:
    - 'word1, compound word2' -> ['word1', 'compound word2']
    - 'word1 compound word2' -> ['word1', 'compound', 'word2']
    """
    if not keywords_value or pd.isna(keywords_value):
        return []
    
    keywords_str = str(keywords_value).strip()
    if not keywords_str:
        return []
    
    # If commas are present, split by commas
    if ',' in keywords_str:
        keywords = [item.strip() for item in keywords_str.split(',') if item.strip()]
    else:
        # No commas, split by spaces
        keywords = [item.strip() for item in keywords_str.split() if item.strip()]
    
    return keywords

def parse_bids_datatypes(bids_value):
    """
    Parse BIDS data types with improved robustness:
    - If commas are present, split by commas
    - Otherwise, split by spaces
    - Trim whitespace and filter empty values
    
    Examples:
    - 'anat, func' -> ['anat', 'func']
    - 'anat func' -> ['anat', 'func']
    """
    if not bids_value or pd.isna(bids_value):
        return []
    
    bids_str = str(bids_value).strip()
    if not bids_str:
        return []
    
    # If commas are present, split by commas
    if ',' in bids_str:
        datatypes = [item.strip() for item in bids_str.split(',') if item.strip()]
    else:
        # No commas, split by spaces
        datatypes = [item.strip() for item in bids_str.split() if item.strip()]
    
    return datatypes

def parse_bids_dataset_type(dataset_type_value):
    """
    Parse BIDS Dataset type and ensure it's either 'raw' or 'derivatives'.
    
    Rules:
    - If value contains 'raw' (case insensitive), return 'raw'
    - If value contains 'deriv' (case insensitive), return 'derivatives' 
    - If both or neither, default to 'raw'
    
    Examples:
    - 'raw' -> 'raw'
    - 'Raw Data' -> 'raw'
    - 'derivatives' -> 'derivatives'
    - 'Derived/processed' -> 'derivatives'
    - 'unknown' -> 'raw'
    """
    if not dataset_type_value or pd.isna(dataset_type_value):
        return 'raw'
    
    type_str = str(dataset_type_value).lower().strip()
    
    # Check for derivatives keywords
    if 'deriv' in type_str or 'processed' in type_str or 'derived' in type_str:
        return 'derivatives'
    
    # Default to raw (including when 'raw' is present or for any other case)
    return 'raw'

def parse_excel_metadata(input_file):
    """
    Parse Excel file to extract metadata for both XML and JSONL generation.
    Returns comprehensive metadata dictionary.
    """
    excel_data = pd.read_excel(input_file, sheet_name=None, engine='openpyxl')
    
    aux_dict = dict()
    for sheet_name, df in excel_data.items():
        aux_dict[sheet_name] = df.to_dict(orient='records')
    
    # Extract authors
    authors = list()
    if "authors" in aux_dict:
        for i in aux_dict["authors"][2:]:
            if pd.isna(i.get('# Metadata record for PublicnEUro')):
                continue
            full_name = str(i['# Metadata record for PublicnEUro']).strip()
            if full_name and full_name != 'nan':
                name_parts = full_name.split(" ")
                authors.append({
                    'givenName': name_parts[0] if len(name_parts) > 0 else '',
                    'familyName': " ".join(name_parts[1:]) if len(name_parts) > 1 else ''
                })

    # Extract funding information
    funding = list()
    if "funding" in aux_dict:
        for i in aux_dict["funding"][2:]:
            if not pd.isna(i.get('# Metadata record for PublicnEUro')):
                funding.append({
                    'name': i['# Metadata record for PublicnEUro'],
                    'identifier': i.get('Unnamed: 1', '')
                })

    # Extract publications
    publication = list()
    if "publications" in aux_dict:
        for i in aux_dict["publications"][2:]:
            if not pd.isna(i.get('# Metadata record for PublicnEUro')):
                author_name = str(i.get('Unnamed: 2', ''))
                name_parts = author_name.split(" ")
                
                publication.append({
                    "type": "academic publication",
                    "title": i['# Metadata record for PublicnEUro'], 
                    "datePublished": str(i.get('Unnamed: 1', '')),
                    "doi": i.get('Unnamed: 3', ''),
                    "authors": [{
                        "givenName": name_parts[0] if len(name_parts) > 0 else '',
                        "familyName": (" ".join(name_parts[1:-2]) if "et al." in author_name 
                                     else " ".join(name_parts[1:])) if len(name_parts) > 1 else ''
                    }]
                })

    # Extract participants information
    participants_aux = dict()
    if "participants_info" in aux_dict:
        for info in aux_dict["participants_info"]:
            if not pd.isna(info.get('Group level information')):
                key = info['Group level information']
                value = info.get('Unnamed: 1')
                if not pd.isna(value):
                    participants_aux[key] = str(value) if isinstance(value, int) else value

    participants = {
        "name": "Participants",
        "content": {
            "total_number": [participants_aux.get('Number of subjects', '')], 
            "age_range": [participants_aux.get('Age range [min max]', '').replace(" ", ", ")], 
            "number_of_healthy": [participants_aux.get('Number of Healthy Controls', '')], 
            "number_of_patients": [participants_aux.get('Number of Patients', '')], 
            "number_of_biological_males": [participants_aux.get('Number of biological males', '')], 
            "number_of_biological_females": [participants_aux.get('Number of biological females', '')]
        }
    } if participants_aux else {"name": "Participants", "content": {}}

    # Extract dataset info
    metadata_aux = dict()
    if "dataset_info" in aux_dict:
        for info in aux_dict["dataset_info"]:
            key_field = info.get('# Metadata record for PublicnEUro\n# BOLD field are mandatory')
            if pd.isna(key_field):
                continue
        
            key = str(key_field).replace("\n", "").strip()
            value = info.get('values')
            if not pd.isna(value):
                metadata_aux[key] = str(value) if isinstance(value, int) else value

    # Helper function for handling comma-separated values
    def handle_values(value):
        if pd.isna(value) or value is None:
            return None
        try:
            import math
            if isinstance(value, float) and math.isnan(value):
                return None
        except (TypeError, ValueError):
            pass
        
        if isinstance(value, str):
            return [str(item.strip()) for item in value.split(',')]
        return [str(value)]

    # Create detailed metadata for JSONL with improved BIDS parsing
    detailed_metadata = {
        "name": "Dataset Metadata",
        "content": {
            "bids_version": handle_values(metadata_aux.get('BIDS version')),
            "bids_datasettype": parse_bids_dataset_type(metadata_aux.get('BIDS Dataset type')), 
            "bids_datatypes": parse_bids_datatypes(metadata_aux.get('BIDS data type')),
            "NCBI Species Taxonomy": handle_values(metadata_aux.get('NCBI Species Taxonomy')),
            "Disease Ontology Name": handle_values(metadata_aux.get('Disease Ontology Name')),
            "Disease Ontology ID": handle_values(metadata_aux.get('Disease Ontology ID ')),
            "SNOMED ID": handle_values(metadata_aux.get("SNOMED ID")),
            "SNOMED label": handle_values(metadata_aux.get("SNOMED label")),
            "Cognitive Atlas concept": handle_values(metadata_aux.get('Cognitive Atlas concept(s)')),
            "Cognitive Atlas task": handle_values(metadata_aux.get('Cognitive Atlas task(s)'))
        }
    }

    # Extract metadata sources
    metadata_sources = {"sources": []}
    if "dataset curators" in aux_dict:
        for info in aux_dict["dataset curators"][2:]:
            if not pd.isna(info.get('# Metadata record for PublicnEUro')):
                metadata_sources["sources"].append({
                    'source_name': info.get('Unnamed: 1', ''),
                    'source_version': format_version(metadata_aux.get('dataset version', 'None')),
                    'agent_name': info['# Metadata record for PublicnEUro']
                })

    # Extract required fields
    name = metadata_aux.get('title', 'Unknown Dataset')
    description = metadata_aux.get('description', 'No description available')
    subtitle = f"{metadata_aux.get('PN ID', 'PN000000')} {metadata_aux.get('title', 'Unknown Dataset')}"
    
    # Handle DOI extraction
    doi_raw = metadata_aux.get('DOI', 'XXXX')
    doi_suffix = extract_doi_suffix(doi_raw)
    doi = f"10.70883/{doi_suffix}"
    
    # Build download URL
    pn_id = metadata_aux.get('PN ID', 'PN000000')
    title = metadata_aux.get('title', 'Unknown Dataset')
    version_raw = metadata_aux.get('dataset version', 'None')
    
    url_base = "https://datacatalog.publicneuro.eu/dataset/"
    url_dataset = f"{pn_id} {title}"
    url_version = format_version(version_raw)
    download_url = f"{url_base}{url_dataset}/{url_version}".replace(" ", "%20")

    # Extract keywords with improved parsing
    keywords_raw = metadata_aux.get('dataset_info', {})
    if isinstance(keywords_raw, dict):
        keywords_value = keywords_raw.get('values', '')
    else:
        # Try to get keywords from the dataset_info sheet
        keywords_value = ''
        if "dataset_info" in aux_dict and len(aux_dict["dataset_info"]) > 3:
            keywords_entry = aux_dict["dataset_info"][3].get('values', '')
            keywords_value = keywords_entry if not pd.isna(keywords_entry) else ''
    
    keywords = parse_keywords(keywords_value)

    return {
        # Basic info (used by XML)
        "authors": authors,
        "description": description,
        "title": title,
        "subtitle": subtitle,
        "doi": doi,
        "id": pn_id,
        "download_url": download_url,
        "name": f"{pn_id} {title}",
        
        # Extended info (used by JSONL)
        "funding": funding,
        "publications": publication,
        "participants": participants,
        "detailed_metadata": detailed_metadata,
        "metadata_sources": metadata_sources,
        "keywords": keywords,
        "dataset_version": format_version(version_raw),
        "license": {"name": "Data User Agreement"},
        "type": "dataset"
    }

def get_xml_template():
    """
    Return the embedded XML template dictionary.
    """
    return {
        "head": {
            "doi_batch_id": "Neurobiology Research Unit",
            "timestamp": "2024121700000000",
            "depositor": {
                "depositor_name": "PublicNeuro",
                "email_address": "publicneuro@nru.dk"
            },
            "registrant": "Neurobiology Research Unit, Rigshospitalet, Denmark"
        },
        "body": {
            "database": {
                "database_metadata": {
                    "@attributes": {
                        "language": "en"
                    },
                    "titles": {
                        "title": "PublicNeuro Datasets",
                        "subtitle": ""
                    }
                },
                "dataset": {
                    "@attributes": {
                        "dataset_type": "record"
                    },
                    "contributors": {},
                    "titles": {
                        "title": "something"
                    },
                    "database_date": {
                        "publication_date": {
                            "month": "MONTH",
                            "day": "DAY",
                            "year": "YEAR"
                        }
                    },
                    "description": {
                        "@attributes": {
                            "language": "en"
                        },
                        "#text": "something"
                    },
                    "doi_data": {
                        "doi": "10.32013/XXXX",
                        "resource": "https://www.crossref.org/xml-samples"
                    }
                }
            }
        }
    }

def dict2xml_element(tag, value):
    """
    Convert dictionary to XML element recursively.
    """
    element = ET.Element(tag)
    if isinstance(value, dict):
        for key, val in value.items():
            if key == "#text":
                element.text = str(val)
            elif key.startswith('@'):
                for i in list(val.keys()):
                    element.set(i, val[i])
            else:
                child_element = dict2xml_element(key, val)
                element.append(child_element)
    elif isinstance(value, list):
        for item in value:
            element.append(dict2xml_element(tag, item))
    else:
        element.text = str(value)
    return element

def export_xlsx_to_xml(excel_file_path, output_xml_path=None):
    """
    Convert Excel metadata file to XML format for CrossRef submission.
    
    Args:
        excel_file_path (str): Path to the Excel file containing metadata
        output_xml_path (str): Optional output path for XML file. If not provided,
                              will use the same name as Excel file with .xml extension
    
    Returns:
        str: Path to the generated XML file
    """
    # Parse Excel metadata
    metadata = parse_excel_metadata(excel_file_path)
    
    # Get XML template
    xml_dict = get_xml_template()
    
    # Determine output file path
    if output_xml_path is None:
        base_name = os.path.splitext(excel_file_path)[0]
        output_xml_path = f"{base_name}.xml"
    
    # Create XML structure
    root = ET.Element('doi_batch', 
                      **{
                          'xmlns:xsi': "http://www.w3.org/2001/XMLSchema-instance",
                          'xsi:schemaLocation': "http://www.crossref.org/schema/5.3.0 https://www.crossref.org/schemas/crossref5.3.0.xsd",
                          'xmlns': "http://www.crossref.org/schema/5.3.0",
                          'xmlns:jats': "http://www.ncbi.nlm.nih.gov/JATS1",
                          'xmlns:fr': "http://www.crossref.org/fundref.xsd",
                          'xmlns:ai': "http://www.crossref.org/AccessIndicators.xsd",
                          'xmlns:mml': "http://www.w3.org/1998/Math/MathML",
                          'version': "5.3.0"
                      })
    
    # Add head element
    head_element = dict2xml_element('head', xml_dict['head'])
    root.append(head_element)
    
    # Add body element
    body_element = dict2xml_element('body', xml_dict['body'])
    root.append(body_element)
    
    # Update timestamp
    now = datetime.now()
    timestamp = now.strftime("%Y%m%d") + "00000000"
    
    for head in root.iter("head"):
        timestamp_elem = head.find(".//timestamp")
        if timestamp_elem is not None:
            timestamp_elem.text = timestamp
    
    # Update database metadata
    for database in root.iter('database'):
        for database_metadata in database.iter('database_metadata'):
            for titles in database_metadata.iter("titles"):
                subtitle_elem = titles.find(".//subtitle")
                if subtitle_elem is not None:
                    subtitle_elem.text = metadata["subtitle"]
        
        # Update dataset information
        for dataset in database.iter('dataset'):
            # Update DOI
            for doi_data in dataset.iter("doi_data"):
                doi_elem = doi_data.find(".//doi")
                if doi_elem is not None:
                    doi_elem.text = metadata["doi"]
                
                resource_elem = doi_data.find(".//resource")
                if resource_elem is not None:
                    resource_elem.text = metadata["download_url"]
            
            # Update description
            desc_elem = dataset.find('.//description')
            if desc_elem is not None:
                desc_elem.text = metadata['description']
            
            # Update title
            for titles in dataset.iter("titles"):
                title_elem = titles.find(".//title")
                if title_elem is not None:
                    title_elem.text = metadata["title"] + " Data"
            
            # Update publication date
            for database_date in dataset.iter("database_date"):
                for publication_date in database_date.iter("publication_date"):
                    month_elem = publication_date.find(".//month")
                    day_elem = publication_date.find(".//day")
                    year_elem = publication_date.find(".//year")
                    
                    if month_elem is not None:
                        month_elem.text = now.strftime("%m")
                    if day_elem is not None:
                        day_elem.text = now.strftime("%d")
                    if year_elem is not None:
                        year_elem.text = now.strftime("%Y")
            
            # Add contributors/authors
            contributors_elem = dataset.find('.//contributors')
            if contributors_elem is not None:
                # Clear existing contributors
                contributors_elem.clear()
                
                first = True
                for author in metadata['authors']:
                    seq = "first" if first else "additional"
                    first = False
                    
                    person_name_elem = ET.Element('person_name', 
                                                sequence=seq, 
                                                contributor_role="author")
                    
                    given_name_elem = ET.SubElement(person_name_elem, 'given_name')
                    given_name_elem.text = author['givenName']
                    
                    surname_elem = ET.SubElement(person_name_elem, 'surname')
                    surname_elem.text = author['familyName']
                    
                    contributors_elem.append(person_name_elem)
    
    # Clean up namespace prefixes in element tags
    for el in root.iter():
        match = re.match(r"^(?:\{.*?\})?(.*)$", el.tag)
        if match:
            el.tag = match.group(1)
    
    # Create ElementTree and write with pretty printing
    tree = ET.ElementTree(root)
    
    # Pretty print using minidom
    from xml.dom import minidom
    rough_string = ET.tostring(root, encoding='unicode')
    reparsed = minidom.parseString(rough_string)
    pretty_xml = reparsed.toprettyxml(indent="    ")
    
    # Remove extra blank lines
    pretty_lines = [line for line in pretty_xml.split('\n') if line.strip()]
    pretty_xml = '\n'.join(pretty_lines)
    
    # Write to file
    with open(output_xml_path, 'w', encoding='utf-8') as f:
        f.write(pretty_xml)
    
    print(f"\n\t [X] XML file has been saved in '{output_xml_path}'")
    return output_xml_path

def export_xlsx_to_jsonl(excel_file_path, output_jsonl_path=None):
    """
    Convert Excel metadata file to JSONL format for data catalog.
    
    Args:
        excel_file_path (str): Path to the Excel file containing metadata
        output_jsonl_path (str): Optional output path for JSONL file. If not provided,
                                will use the same name as Excel file with .jsonl extension
    
    Returns:
        str: Path to the generated JSONL file
    """
    # Parse Excel metadata
    metadata = parse_excel_metadata(excel_file_path)
    
    # Determine output file path
    if output_jsonl_path is None:
        base_name = os.path.splitext(excel_file_path)[0]
        output_jsonl_path = f"{base_name}.jsonl"
    
    # Build JSONL structure
    jsonl_data = {
        "type": metadata["type"],
        "name": metadata["title"],
        "description": metadata["description"],
        "dataset_id": metadata["name"],
        "dataset_version": metadata["dataset_version"],
        "doi": metadata["doi"],
        "download_url": metadata["download_url"],
        "keywords": metadata["keywords"],
        "license": metadata["license"],
        "authors": metadata["authors"],
        "funding": metadata["funding"],
        "publications": metadata["publications"],
        "metadata_sources": metadata["metadata_sources"],
        "additional_display": [metadata["detailed_metadata"], metadata["participants"]]
    }
    
    # Write JSONL file
    with open(output_jsonl_path, 'w', encoding='utf-8') as f:
        f.write(json.dumps(jsonl_data) + '\n')
    
    print(f"\n\t [X] JSONL file has been saved in '{output_jsonl_path}'")
    return output_jsonl_path

def export_xlsx_to_both(excel_file_path, output_xml_path=None, output_jsonl_path=None):
    """
    Convert Excel metadata file to both XML and JSONL formats.
    
    Args:
        excel_file_path (str): Path to the Excel file containing metadata
        output_xml_path (str): Optional output path for XML file
        output_jsonl_path (str): Optional output path for JSONL file
    
    Returns:
        tuple: (xml_file_path, jsonl_file_path)
    """
    xml_file = export_xlsx_to_xml(excel_file_path, output_xml_path)
    jsonl_file = export_xlsx_to_jsonl(excel_file_path, output_jsonl_path)
    
    print(f"\n\t [X] Both files generated successfully:")
    print(f"\t     XML:   {xml_file}")
    print(f"\t     JSONL: {jsonl_file}")
    
    return xml_file, jsonl_file

def main():
    """
    Command line interface for the function.
    Default behavior: outputs both XML and JSONL files
    """
    if len(sys.argv) < 2:
        print("\n\t [X] Please provide the Excel file path as an argument")
        print("\n\t [X] Usage: python export_xlsx.py <excel_file_path> [xml|jsonl] [output_path]")
        print("\n\t [X] Examples:")
        print("\t     python export_xlsx.py PublicnEUro_PN000011.xlsx          # Both XML and JSONL (default)")
        print("\t     python export_xlsx.py PublicnEUro_PN000011.xlsx xml      # XML only")
        print("\t     python export_xlsx.py PublicnEUro_PN000011.xlsx jsonl    # JSONL only")
        print("\t     python export_xlsx.py PublicnEUro_PN000011.xlsx xml output.xml")
        print("\t     python export_xlsx.py PublicnEUro_PN000011.xlsx jsonl output.jsonl")
        sys.exit(1)
    
    excel_file = sys.argv[1]
    
    # Parse arguments
    format_type = "both"  # default to both formats
    output_file = None
    
    if len(sys.argv) > 2:
        # Check if second argument is a format specifier
        if sys.argv[2].lower() in ['xml', 'jsonl']:
            format_type = sys.argv[2].lower()
            if len(sys.argv) > 3:
                output_file = sys.argv[3]
        else:
            # Second argument is not a format, treat as output file for both formats
            output_file = sys.argv[2]
    
    if not os.path.exists(excel_file):
        print(f"\n\t [X] Error: File '{excel_file}' not found")
        sys.exit(1)
    
    try:
        if format_type == "xml":
            result_file = export_xlsx_to_xml(excel_file, output_file)
            print(f"\n\t [X] Successfully converted '{excel_file}' to XML: '{result_file}'")
        elif format_type == "jsonl":
            result_file = export_xlsx_to_jsonl(excel_file, output_file)
            print(f"\n\t [X] Successfully converted '{excel_file}' to JSONL: '{result_file}'")
        else:  # format_type == "both" (default)
            xml_file, jsonl_file = export_xlsx_to_both(excel_file)
            print(f"\n\t [X] Successfully converted '{excel_file}' to both formats:")
            print(f"\t     XML:   {xml_file}")
            print(f"\t     JSONL: {jsonl_file}")
    except Exception as e:
        print(f"\n\t [X] Error during conversion: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()
