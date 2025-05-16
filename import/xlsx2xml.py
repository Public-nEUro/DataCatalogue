import openpyxl, json, re, sys, os
import pandas as pd
import xml.etree.ElementTree as ET
from datetime import datetime

def aux(input_file):

    excel_data = pd.read_excel(os.getcwd()+"/"+input_file, sheet_name=None, engine='openpyxl')

    aux_dict = dict()
    for sheet_name, df in excel_data.items():
        aux_dict[sheet_name] = df.to_dict(orient='records')
        
    # ===================================== AUTHOR =====================================      
    authors = list()
    for i in aux_dict["authors"][2:]:
        authors.append({
            'givenName': i['# Metadata record for PublicnEUro'].split(" ")[0],
            'familyName': " ".join(i['# Metadata record for PublicnEUro'].split(" ")[1:])
        })

    name = aux_dict["dataset_info"][1]['values']
    description = aux_dict["dataset_info"][2]['values']

    metadata_aux = dict()
    for info in aux_dict["dataset_info"]:
        if pd.isna(info['# Metadata record for PublicnEUro\n# BOLD field are mandatory']):
            continue
    
        key = info['# Metadata record for PublicnEUro\n# BOLD field are mandatory'].replace("\n", "")
        value = info['values'] if not pd.isna(info['values']) else None   
        metadata_aux[key] = str(value) if isinstance(value, int) else value
    subtitle = str(" ".join((metadata_aux['PN ID'], metadata_aux['title'])))
    doi = metadata_aux['DOI']
    # ===================================== DOWNLOAD URL ===================================== 
    a = "https://datacatalog.publicneuro.eu/dataset/"
    b = str(" ".join((metadata_aux['PN ID'], metadata_aux['title'])))
    c = "/"
    d = "V"+str(metadata_aux['dataset version'])
    download_url = str(a+b+c+d).replace(" ", "%20")


    return {

        "authors" : authors,
        "description": description,
        "title": metadata_aux['title'],
        "subtitle": subtitle,
        "doi": doi,
        "id": metadata_aux['PN ID'],
        "download_url": download_url,
        "name": b
    }


def xlsx2xml(metadata_path, out_file=None):

    try:
        comp = aux(metadata_path)
    except FileNotFoundError:
        print("Metadata file not found. Check the path variable and filename.")
    except Exception as e:
        print(e)
       
    try:
        with open(os.path.dirname(os.path.abspath(__file__))+"/xml_dict.json", 'r') as f:
            xml_dict = json.load(f)
    except FileNotFoundError:
        print("File not found. Check the path variable and filename.")
    except Exception as e:
        print(e) 
    
    def dict2xml_element(tag, value):
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

    root = ET.Element('doi_batch', xmlns_xsi="http://www.w3.org/2001/XMLSchema-instance", 
                      xsi_schemaLocation="http://www.crossref.org/schema/5.3.0 https://www.crossref.org/schemas/crossref5.3.0.xsd",
                      xmlns="http://www.crossref.org/schema/5.3.0", 
                      xmlns_jats="http://www.ncbi.nlm.nih.gov/JATS1", 
                      xmlns_fr="http://www.crossref.org/fundref.xsd", 
                      xmlns_ai="http://www.crossref.org/AccessIndicators.xsd", 
                      xmlns_mml="http://www.w3.org/1998/Math/MathML", 
                      version="5.3.0")

    helper_dict={"xmlns_xsi":"xmlns:xsi", 
                      "xsi_schemaLocation":"xsi:schemaLocation", 
                      "xmlns_jats":"xmlns:jats", 
                      "xmlns_fr":"xmlns:fr", 
                      "xmlns_ai":"xmlns:ai", 
                      "xmlns_mml":"xmlns:mml"}

    for element in root.iter():
        for attr, value in list(element.attrib.items()):
            for key, replacement in helper_dict.items():
                if key in attr:
                    new_attr = attr.replace(key, replacement)
                    element.set(new_attr, value)
                    del element.attrib[attr]
                    break  

    head_element = dict2xml_element('head', xml_dict['head'])
    root.append(head_element)
    body_element = dict2xml_element('body', xml_dict['body'])
    root.append(body_element)
    tree = ET.ElementTree(root)

    now = datetime.now()
    timestamp = now.strftime("%Y%m%d") + "00000000"
    
    for head in root.iter("head"):
        head.find(".//timestamp").text = timestamp
    first=True    
    for database in root.iter('database'):
        for database_metadata in database.iter('database_metadata'):
            for titles in database_metadata.iter("titles"):
                titles.find(".//subtitle").text = comp["subtitle"]
            
        for dataset in database.iter('dataset'):
            for doi_data in dataset.iter("doi_data"):
                doi_data.find(".//doi").text = comp["doi"]
            for doi_data in dataset.iter("doi_data"):
                doi_data.find(".//resource").text = comp["download_url"]
            dataset.find('.//description').text = comp['description']
            for titles in dataset.iter("titles"):
                titles.find(".//title").text = comp["title"] + " Data"
            for database_date in dataset.iter("database_date"):
                for publication_date in database_date.iter("publication_date"):
                    publication_date.find(".//month").text = now.strftime("%m")
                    publication_date.find(".//day").text = now.strftime("%d")
                    publication_date.find(".//year").text = now.strftime("%Y")
            contributors_elem = dataset.find('.//contributors')
            if contributors_elem is not None:
                for author in comp['authors']:
                    seq= "first" if first else "additional"
                    first=False
                    person_name_elem = ET.Element('person_name', sequence=seq, contributor_role="author")
                    given_name_elem = ET.SubElement(person_name_elem, 'given_name')
                    given_name_elem.text = author['givenName']
                    surname_elem = ET.SubElement(person_name_elem, 'surname')
                    surname_elem.text = author['familyName']
                    contributors_elem.append(person_name_elem)
                
    for el in root.iter():
        match = re.match("^(?:\{.*?\})?(.*)$", el.tag)
        if match:
            el.tag = match.group(1)
    
    if not out_file:
        out_file = os.getcwd()+"/"+"PublicNeuro.xml"
    else: out_file = os.getcwd()+"/"+out_file
    
    tree.write(out_file, encoding="UTF-8", xml_declaration=True)
    print(f"\n\t [X] xml file has been saved in '{out_file}'")
    
