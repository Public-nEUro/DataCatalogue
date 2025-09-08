#!/usr/bin/env python3
"""
Excel to XML/JSONL Converter for PublicNeuro Datasets
=====================================================

This module converts Excel metadata files to XML and JSONL formats for dataset publication. It extracts comprehensive metadata including authors, funding, publications, participants, DUA (Data User Agreement) terms, and BIDS information with intelligent filtering of empty/meaningless values.

MAIN FUNCTIONS:
==============

Core Export Functions:
- export_xlsx_to_xml(excel_file, output_xml=None, skip_validation=False)
  Converts Excel file to CrossRef XML format for DOI registration
  
- export_xlsx_to_jsonl(excel_file, output_jsonl=None, skip_validation=False) 
  Converts Excel file to JSONL format for web catalog display
  
- export_xlsx_to_both(excel_file, output_xml=None, output_jsonl=None)
  Converts Excel file to both XML and JSONL formats (shows warnings but exports anyway)

Metadata Processing:
- parse_excel_metadata(input_file)
  Main parser that extracts all metadata from Excel sheets into structured dict
  
- validate_metadata(metadata)
  Validates that all mandatory fields are present and have values
  Returns validation errors dictionary by category (dataset_info, participants, dua, authors, data_curators)

Data Parsing Utilities:
- extract_doi_suffix(doi_value)
  Extracts DOI suffix from various DOI formats
  
- format_version(version_value)
  Ensures version numbers are properly formatted with 'V' prefix
  
- parse_keywords(keywords_value)
  Intelligently parses keywords by commas or spaces, handles compound terms
  
- parse_bids_datatypes(bids_value)
  Parses BIDS data types by commas or spaces
  
- parse_bids_dataset_type(dataset_type_value)
  Ensures BIDS dataset type is 'raw' or 'derivatives'

Text Processing & Filtering:
- clean_text_for_jsonl(text, preserve_line_breaks=False)
  Cleans text for JSONL output, optionally preserving line breaks for web rendering

- filter_empty_values(data_dict)
  Removes keys with empty, None, or meaningless placeholder values from dictionaries

- clean_metadata_content(content_dict) 
  Cleans metadata content by removing null, empty, and meaningless values

- remove_nan_and_na_values(data)
  Recursively removes key-value pairs with NaN, 'n.a.', or other meaningless values from nested structures

- clean_jsonl_structure(data)
  Comprehensively cleans entire JSONL structure removing empty arrays, null values, and meaningless entries

Template Management:
- get_xml_template()
  Returns embedded CrossRef XML template structure

Command Line Interface:
- main()
  CLI entry point, processes command line arguments and runs export

EXCEL SHEET STRUCTURE EXPECTED:
==============================
- dataset_info: Basic dataset information (title, description, keywords, BIDS info)
- participants_info: Number of subjects and participant details  
- DUA: Data User Agreement restrictions (cell D3) and terms (cell B1)
- authors: Author names and affiliations
- dataset curators: Data curator names and institutions
- funding: Funding sources and grant identifiers
- publications: Related publications with DOIs

DUA EXTRACTION:
==============
- Restrictions: Extracted from cell B1 of DUA sheet (dropdown selection)
- Terms: Extracted from cell B2 of DUA sheet with line break preservation (\n)
- Only processes columns A and B (ignores columns C, D, etc.)
- Structure: {"name": "DUA terms", "content": {"Restrictions": [...], "Terms": [...]}}

OUTPUT FORMATS:
==============
- XML: CrossRef format for DOI registration with database metadata
- JSONL: Web catalog format with additional_display fields for rich rendering
- Empty Value Filtering: Automatically removes null, empty arrays, meaningless placeholders

VALIDATION:
===========
Comprehensive validation across 5 categories:
1. Dataset info: title, description, keywords, BIDS version/type/datatypes
2. Participants: total number of subjects
3. DUA: restrictions selection and terms (unless restriction is 'None (CCBY)')
4. Authors: at least one author with name
5. Data curators: at least one curator with name and institution

EXPORT BEHAVIOR:
===============
- Individual functions (export_xlsx_to_xml, export_xlsx_to_jsonl): Strict validation, fails on errors
- Combined function (export_xlsx_to_both): Shows warnings but exports anyway
- All functions support skip_validation parameter for testing

FEATURES:
=========
- Intelligent keyword parsing (space or comma separated)
- Line break preservation in DUA terms for web rendering
- Comprehensive empty value filtering (null, [], "", meaningless placeholders)
- Author filtering (keeps authors with either given name or family name)
- BIDS compliance validation and parsing
- Flexible DOI format handling
- Version number normalization (V1, not VV1)

Usage:
======
# Command line (both formats with warnings)
python export_xlsx.py input_file.xlsx

# Python API (strict validation)
from export_xlsx import export_xlsx_to_xml, export_xlsx_to_jsonl
xml_file = export_xlsx_to_xml('file.xlsx')
jsonl_file = export_xlsx_to_jsonl('file.xlsx')

# Python API (warnings but exports)
from export_xlsx import export_xlsx_to_both
xml_file, jsonl_file = export_xlsx_to_both('file.xlsx')
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

def validate_metadata(metadata):
    """
    Validate that all mandatory fields are present and have values.
    Returns dictionary with validation errors by category.
    """
    validation_errors = {
        'dataset_info': [],
        'participants': [],
        'dua': [],
        'authors': [],
        'data_curators': []
    }
    
    # (1) Dataset info mandatory fields
    if not metadata.get('title') or str(metadata['title']).strip() == 'Unknown Dataset':
        validation_errors['dataset_info'].append("title")
    if not metadata.get('description') or str(metadata['description']).strip() == 'No description available':
        validation_errors['dataset_info'].append("description")
    if not metadata.get('keywords') or len(metadata['keywords']) == 0:
        validation_errors['dataset_info'].append("Keywords")
    if not metadata.get('dataset_version') or str(metadata['dataset_version']).strip() in ['VNone', 'V']:
        validation_errors['dataset_info'].append("dataset version")
    
    # Check BIDS fields from detailed_metadata
    detailed_metadata = metadata.get('detailed_metadata', {}).get('content', {})
    bids_datasettype = detailed_metadata.get('bids_datasettype')
    if not bids_datasettype or (isinstance(bids_datasettype, list) and len(bids_datasettype) == 0):
        validation_errors['dataset_info'].append("BIDS Dataset type")
    
    bids_version = detailed_metadata.get('bids_version')
    if not bids_version or (isinstance(bids_version, list) and (len(bids_version) == 0 or not bids_version[0] or bids_version[0] == 'BIDS version')):
        validation_errors['dataset_info'].append("BIDS version")
    
    bids_datatypes = detailed_metadata.get('bids_datatypes')
    if not bids_datatypes or (isinstance(bids_datatypes, list) and len(bids_datatypes) == 0):
        validation_errors['dataset_info'].append("BIDS data type")
    
    # (2) Participant info mandatory fields
    participants = metadata.get('participants', {}).get('content', {})
    total_subjects = participants.get('total_number', [''])
    if not total_subjects or not total_subjects[0] or str(total_subjects[0]).strip() == '':
        validation_errors['participants'].append("Number of subjects")
    
    # (3) DUA mandatory fields
    dua_content = metadata.get('dua_content', {}).get('content', {})
    
    if not dua_content:
        validation_errors['dua'].append("DUA content not found")
    else:
        restrictions = dua_content.get('Restrictions', [])
        terms = dua_content.get('Terms', [])
        
        if not restrictions or len(restrictions) == 0:
            validation_errors['dua'].append("Restrictions must be selected")
        else:
            # Check if restriction is 'None (CCBY)' - if so, terms are optional
            restriction_value = restrictions[0] if restrictions else ""
            if restriction_value != 'None (CCBY)':
                if not terms or len(terms) == 0 or not terms[0].strip():
                    validation_errors['dua'].append("Terms must have a value (unless restriction is 'None (CCBY)')")
    
    # (4) Authors mandatory fields
    authors = metadata.get('authors', [])
    if not authors or len(authors) == 0:
        validation_errors['authors'].append("At least 1 author name is required")
    else:
        # Check if at least one author has a name
        has_valid_author = False
        for author in authors:
            given_name = author.get('givenName', '').strip()
            family_name = author.get('familyName', '').strip()
            if given_name or family_name:
                has_valid_author = True
                break
        if not has_valid_author:
            validation_errors['authors'].append("At least 1 author must have a name")
    
    # (5) Data curator mandatory fields
    metadata_sources = metadata.get('metadata_sources', {}).get('sources', [])
    if not metadata_sources or len(metadata_sources) == 0:
        validation_errors['data_curators'].append("At least 1 curator name and 1 institution is required")
    else:
        # Check if at least one curator has both name and institution
        has_valid_curator = False
        for source in metadata_sources:
            agent_name = source.get('agent_name', '').strip()
            source_name = source.get('source_name', '').strip()
            if agent_name and source_name:
                has_valid_curator = True
                break
        if not has_valid_curator:
            validation_errors['data_curators'].append("At least 1 curator must have both name and institution")
    
    return validation_errors

def filter_empty_values(data_dict):
    """Remove keys with empty, None, or meaningless values from a dictionary"""
    filtered = {}
    for key, value in data_dict.items():
        if isinstance(value, list):
            # Filter out empty strings, None, meaningless placeholders, and whitespace-only strings from lists
            filtered_list = [v for v in value if v is not None and str(v).strip() != '' and str(v).strip() != '[]']
            if filtered_list:  # Only include the key if there are non-empty values
                filtered[key] = filtered_list
        elif value is not None and value != [] and str(value).strip() != '' and str(value).strip() != '[]':
            filtered[key] = value
    return filtered

def clean_metadata_content(content_dict):
    """Clean metadata content by removing null, empty, and meaningless values"""
    cleaned = {}
    for key, value in content_dict.items():
        if value is None:
            continue  # Skip null values
        elif isinstance(value, list):
            # Filter out None, empty strings, and meaningless values from lists
            cleaned_list = [v for v in value if v is not None and str(v).strip() != '' and str(v).strip() not in ['[]', 'BIDS version']]
            if cleaned_list:  # Only include if there are meaningful values
                cleaned[key] = cleaned_list
        elif isinstance(value, str) and value.strip() in ['', '[]', 'BIDS version']:
            continue  # Skip empty or meaningless string values
        else:
            cleaned[key] = value
    return cleaned

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

    # Helper function to filter out empty values
    def filter_empty_values(data_dict):
        """Remove keys with empty, None, or meaningless values from a dictionary"""
        filtered = {}
        for key, value in data_dict.items():
            if isinstance(value, list):
                # Filter out empty strings, None, meaningless placeholders, and whitespace-only strings from lists
                filtered_list = [v for v in value if v is not None and str(v).strip() != '' and str(v).strip() != '[]']
                if filtered_list:  # Only include the key if there are non-empty values
                    filtered[key] = filtered_list
            elif value is not None and value != [] and str(value).strip() != '' and str(value).strip() != '[]':
                filtered[key] = value
        return filtered

    # Helper function to clean metadata content
    def clean_metadata_content(content_dict):
        """Clean metadata content by removing null, empty, and meaningless values"""
        cleaned = {}
        for key, value in content_dict.items():
            if value is None:
                continue  # Skip null values
            elif isinstance(value, list):
                # Filter out None, empty strings, and meaningless values from lists
                cleaned_list = [v for v in value if v is not None and str(v).strip() != '' and str(v).strip() not in ['[]', 'BIDS version']]
                if cleaned_list:  # Only include if there are meaningful values
                    cleaned[key] = cleaned_list
            elif isinstance(value, str) and value.strip() in ['', '[]', 'BIDS version']:
                continue  # Skip empty or meaningless string values
            else:
                cleaned[key] = value
        return cleaned

    participants = {
        "name": "Participants",
        "content": filter_empty_values({
            "total_number": [participants_aux.get('Number of subjects', '')], 
            "age_range": [participants_aux.get('Age range [min max]', '').replace(" ", ", ")], 
            "number_of_healthy": [participants_aux.get('Number of Healthy Controls', '')], 
            "number_of_patients": [participants_aux.get('Number of Patients', '')], 
            "number_of_biological_males": [participants_aux.get('Number of biological males', '')], 
            "number_of_biological_females": [participants_aux.get('Number of biological females', '')]
        })
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
        "content": clean_metadata_content({
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
        })
    }

    # Extract DUA (Data User Agreement) information
    def clean_text_for_jsonl(text, preserve_line_breaks=False):
        """Clean text for JSONL compatibility"""
        if pd.isna(text) or not text:
            return ""
        
        text_str = str(text).strip()
        
        if preserve_line_breaks:
            # Preserve line breaks as \n for web rendering
            text_str = text_str.replace('\r\n', '\n').replace('\r', '\n')
            # Clean problematic characters but keep line breaks
            text_str = text_str.replace('"', "'").replace('\t', ' ')
        else:
            # Convert line breaks to periods (original behavior)
            text_str = text_str.replace('\r\n', '. ').replace('\n', '. ').replace('\r', '. ')
            text_str = text_str.replace('"', "'").replace('\t', ' ')
            # Normalize multiple periods
            import re
            text_str = re.sub(r'\.+', '.', text_str)
        
        # Normalize multiple spaces to single space
        import re
        text_str = re.sub(r' +', ' ', text_str)
        return text_str.strip()
    
    dua_content = {"name": "DUA terms", "content": {"Restrictions": [], "Terms": []}}
    if "DUA" in aux_dict and len(aux_dict["DUA"]) >= 2:  # Need at least 2 data rows
        dua_df = pd.DataFrame(aux_dict["DUA"])
        
        # With headers: pandas treats headers automatically, so data starts at row 0
        # Row 0: "Restrictions" content, Row 1: "Terms" content
        
        # Get Restrictions from first data row (row 0, column 1)
        if dua_df.shape[0] > 0 and dua_df.shape[1] > 1:
            restrictions_value = dua_df.iloc[0, 1]  # First data row, column "Content"
            if not pd.isna(restrictions_value) and str(restrictions_value).strip():
                clean_restriction = clean_text_for_jsonl(restrictions_value, preserve_line_breaks=False)
                if clean_restriction:
                    dua_content["content"]["Restrictions"] = [clean_restriction]
        
        # Get Terms from second data row (row 1, column 1) 
        if dua_df.shape[0] > 1 and dua_df.shape[1] > 1:
            terms_value = dua_df.iloc[1, 1]  # Second data row, column "Content"
            if not pd.isna(terms_value) and str(terms_value).strip():
                clean_terms = clean_text_for_jsonl(terms_value, preserve_line_breaks=True)
                if clean_terms:
                    dua_content["content"]["Terms"] = [clean_terms]

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
    # Extract keywords using the same pattern as other metadata fields
    keywords_value = metadata_aux.get('Keywords', '')
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
        "dua_content": dua_content,
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

def export_xlsx_to_xml(excel_file_path, output_xml_path=None, skip_validation=False):
    """
    Convert Excel metadata file to XML format for CrossRef submission.
    
    Args:
        excel_file_path (str): Path to the Excel file containing metadata
        output_xml_path (str): Optional output path for XML file. If not provided,
                              will use the same name as Excel file with .xml extension
    
    Returns:
        str: Path to the generated XML file
    
    Raises:
        ValueError: If mandatory fields are missing
    """
    # Parse Excel metadata
    metadata = parse_excel_metadata(excel_file_path)
    
    # Validate metadata (if not skipped)
    if not skip_validation:
        validation_errors = validate_metadata(metadata)
        total_errors = sum(len(errors) for errors in validation_errors.values())
        if total_errors > 0:
            error_msg = f"❌ VALIDATION FAILED - Cannot proceed with conversion:\n\n"
            error_count = 1
            for category, issues in validation_errors.items():
                if issues:
                    for issue in issues:
                        error_msg += f"   {error_count}. {category}: {issue}\n"
                        error_count += 1
            error_msg += f"\nPlease fix these issues in '{excel_file_path}' and try again."
            raise ValueError(error_msg)
    
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

def export_xlsx_to_jsonl(excel_file_path, output_jsonl_path=None, skip_validation=False):
    """
    Convert Excel metadata file to JSONL format for data catalog.
    
    Args:
        excel_file_path (str): Path to the Excel file containing metadata
        output_jsonl_path (str): Optional output path for JSONL file. If not provided,
                                will use the same name as Excel file with .jsonl extension
    
    Returns:
        str: Path to the generated JSONL file
    
    Raises:
        ValueError: If mandatory fields are missing
    """
    # Parse Excel metadata
    metadata = parse_excel_metadata(excel_file_path)
    
    # Validate metadata (if not skipped)
    if not skip_validation:
        validation_errors = validate_metadata(metadata)
        total_errors = sum(len(errors) for errors in validation_errors.values())
        if total_errors > 0:
            error_msg = f"❌ VALIDATION FAILED - Cannot proceed with conversion:\n\n"
            error_count = 1
            for category, issues in validation_errors.items():
                if issues:
                    for issue in issues:
                        error_msg += f"   {error_count}. {category}: {issue}\n"
                        error_count += 1
            error_msg += f"\nPlease fix these issues in '{excel_file_path}' and try again."
            raise ValueError(error_msg)
    
    # Determine output file path
    if output_jsonl_path is None:
        base_name = os.path.splitext(excel_file_path)[0]
        output_jsonl_path = f"{base_name}.jsonl"
    
    # Helper function to remove NaN and n.a. values from nested structures
    def remove_nan_and_na_values(data):
        """
        Recursively remove key-value pairs where the value is NaN, 'n.a.', or other meaningless values.
        
        Args:
            data: Dictionary, list, or other data structure to clean
            
        Returns:
            Cleaned data structure with NaN and n.a. values removed
        """
        if isinstance(data, dict):
            cleaned = {}
            for key, value in data.items():
                # Skip keys with NaN values (handle scalars only)
                try:
                    if pd.isna(value):
                        continue
                except (ValueError, TypeError):
                    # pd.isna() failed, probably because value is an array/list - continue processing
                    pass
                    
                # Skip keys with string values that are meaningless
                if isinstance(value, str) and value.strip().lower() in ['n.a.', 'na', 'n/a', '']:
                    continue
                # Recursively clean nested structures
                elif isinstance(value, (dict, list)):
                    cleaned_value = remove_nan_and_na_values(value)
                    # Only include if the cleaned structure is not empty
                    if cleaned_value:
                        cleaned[key] = cleaned_value
                else:
                    cleaned[key] = value
            return cleaned
        elif isinstance(data, list):
            cleaned = []
            for item in data:
                # Skip NaN items (handle scalars only)
                try:
                    if pd.isna(item):
                        continue
                except (ValueError, TypeError):
                    # pd.isna() failed, continue processing
                    pass
                    
                if isinstance(item, str) and item.strip().lower() in ['n.a.', 'na', 'n/a', '']:
                    continue
                else:
                    cleaned_item = remove_nan_and_na_values(item)
                    # Only include non-empty items
                    if cleaned_item is not None and cleaned_item != {} and cleaned_item != []:
                        cleaned.append(cleaned_item)
            return cleaned
        else:
            return data

    # Helper function to clean entire JSONL structure
    def clean_jsonl_structure(data):
        """Clean the entire JSONL structure by removing empty/meaningless values"""
        cleaned = {}
        for key, value in data.items():
            if value is None:
                continue  # Skip null values
            elif isinstance(value, list):
                if key == "keywords" and len(value) == 0:
                    continue  # Skip empty keywords array
                elif key == "funding" and len(value) == 0:
                    continue  # Skip empty funding array  
                elif key == "publications" and len(value) == 0:
                    continue  # Skip empty publications array
                elif key == "authors":
                    # Clean authors - remove those with empty names
                    cleaned_authors = []
                    for author in value:
                        if isinstance(author, dict):
                            # Keep author if they have either given name or family name
                            given = author.get('givenName', '').strip()
                            family = author.get('familyName', '').strip()
                            if given or family:
                                cleaned_authors.append(author)
                    if cleaned_authors:
                        cleaned[key] = cleaned_authors
                elif key == "additional_display":
                    # Clean additional_display sections
                    cleaned_sections = []
                    for section in value:
                        if isinstance(section, dict) and section.get('content'):
                            # Only include sections that have meaningful content after cleaning
                            if len(section['content']) > 0:
                                cleaned_sections.append(section)
                    if cleaned_sections:
                        cleaned[key] = cleaned_sections
                else:
                    cleaned[key] = value
            elif isinstance(value, str) and value.strip() == '':
                continue  # Skip empty strings
            else:
                cleaned[key] = value
        return cleaned
    
    # First apply NaN and n.a. cleanup to the metadata structure
    cleaned_metadata = remove_nan_and_na_values(metadata)
    
    # Build JSONL structure with cleaned metadata (with fallbacks for safety)
    jsonl_data = clean_jsonl_structure({
        "type": cleaned_metadata.get("type", "dataset"),
        "name": cleaned_metadata.get("title", ""),
        "description": cleaned_metadata.get("description", ""),
        "dataset_id": cleaned_metadata.get("name", ""),
        "dataset_version": cleaned_metadata.get("dataset_version", ""),
        "doi": cleaned_metadata.get("doi", ""),
        "download_url": cleaned_metadata.get("download_url", ""),
        "keywords": cleaned_metadata.get("keywords", []),
        "license": cleaned_metadata.get("license", {}),
        "authors": cleaned_metadata.get("authors", []),
        "funding": cleaned_metadata.get("funding", []),
        "publications": cleaned_metadata.get("publications", []),
        "metadata_sources": cleaned_metadata.get("metadata_sources", {}),
        "additional_display": [
            cleaned_metadata.get("detailed_metadata", {}), 
            cleaned_metadata.get("dua_content", {}), 
            cleaned_metadata.get("participants", {})
        ]
    })
    
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
    
    Raises:
        ValueError: If mandatory fields are missing
    """
    # Parse and validate metadata once
    metadata = parse_excel_metadata(excel_file_path)
    validation_errors = validate_metadata(metadata)
    
    # Check if there are any validation errors
    total_errors = sum(len(issues) for issues in validation_errors.values())
    if total_errors > 0:
        print(f"⚠️  VALIDATION WARNINGS - Found {total_errors} issues but proceeding with conversion:")
        error_count = 1
        for category, issues in validation_errors.items():
            if issues:
                for issue in issues:
                    print(f"   {error_count}. {category}: {issue}")
                    error_count += 1
        print(f"Converting '{excel_file_path}' anyway...\n")
    
    # If validation passes, proceed with both exports
    xml_file = export_xlsx_to_xml(excel_file_path, output_xml_path, skip_validation=True)
    jsonl_file = export_xlsx_to_jsonl(excel_file_path, output_jsonl_path, skip_validation=True)
    
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
    except ValueError as e:
        # Handle validation errors specifically
        print(f"\n{str(e)}")
        sys.exit(1)
    except Exception as e:
        print(f"\n\t [X] Error during conversion: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()
