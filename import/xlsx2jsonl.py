import subprocess
import sys

def install_openpyxl():
    subprocess.check_call([sys.executable, "-m", "pip", "install", "openpyxl", "--quiet"])

# Install openpyxl
install_openpyxl()

# Now you can import and use openpyxl
import openpyxl
import pandas as pd
import json, re, math

def xlsx2jsonl(input_file):

    #input_file = 'PublicnEUro_record_Aggression.xlsx'
    excel_data = pd.read_excel(input_file, sheet_name=None, engine='openpyxl')
    
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
    # ===================================== FUNDING =====================================
    funding = list()
    for i in aux_dict["funding"][2:]:
        funding.append({
            'name' : i['# Metadata record for PublicnEUro'],
            'identifier' : i['Unnamed: 1']
        })
    # ===================================== PUBLICATION =====================================      
    publication=list()
    for i in aux_dict["publications"][2:]:
         publication.append({
            "type":"academic publication",
            "title": i['# Metadata record for PublicnEUro'], 
            "datePublished":str(i['Unnamed: 1']),
            "doi":i['Unnamed: 3'],
            "authors":[{
                "givenName": i['Unnamed: 2'].split(" ")[0],
                "familyName": " ".join(i['Unnamed: 2'].split(" ")[1:-2]) if "et al." in i['Unnamed: 2'] else " ".join(i['Unnamed: 2'].split(" ")[1:])
            }]
        })
    # ===================================== PARTICIPANTS =====================================  
    participants_aux, participants = dict(), dict()
    for info in aux_dict["participants_info"]:
        if pd.isna(info['Group level information']):
            continue
        key = info['Group level information']
        value = info['Unnamed: 1'] if not pd.isna(info['Unnamed: 1']) else None   
        participants_aux[key] = str(value) if isinstance(value, int) else value
    
    for info in aux_dict["participants_info"]:
        participants["name"] = "Participants"
        participants["content"] = {
            "total_number": [participants_aux['Number of subjects']], 
            "age_range": [participants_aux['Age range [min max]'].replace(" ", ", ")], 
            "number_of_healthy": [participants_aux['Number of Healthy Controls']], 
            "number_of_patients": [participants_aux['Number of Patients']], 
            "number_of_biological_males": [participants_aux['Number of biological males']], 
            "number_of_biological_females": [participants_aux['Number of biological females']]
        }
    # ===================================== METADATA =====================================  
    metadata_aux, metadata = dict(), dict()
    for info in aux_dict["dataset_info"]:
        if pd.isna(info['# Metadata record for PublicnEUro\n# BOLD field are mandatory']):
            continue
    
        key = info['# Metadata record for PublicnEUro\n# BOLD field are mandatory'].replace("\n", "")
        value = info['values'] if not pd.isna(info['values']) else None   
        metadata_aux[key] = str(value) if isinstance(value, int) else value
    def handle_values(dataset_info, index):
        try:
            if math.isnan(dataset_info[index]):
                return None  
        except TypeError:  # in case the field is provided with a value
            return [str(item.strip()) for item in dataset_info[index].split(',')]
        except AttributeError:  # in case the field is empty
            value = dataset_info[index]
            return [str(item.strip()) for item in value.split(',')] if not math.isnan(value) else str(value)
    for i in aux_dict["dataset_info"]:
        metadata["name"] = "Dataset Metadata"
        metadata["content"] = {
            "bids_version" : None if metadata_aux['BIDS version'] == None else [metadata_aux['BIDS version']],
            "bids_datasettype" : None if metadata_aux['BIDS Dataset type'] == None else [str(item.strip()) for item in metadata_aux['BIDS Dataset type'].split(',')], 
            "bids_datatypes" : None if metadata_aux['BIDS data type'] == None else [str(item.strip()) for item in metadata_aux['BIDS data type'].split(',')],
            "NCBI Species Taxonomy": None if metadata_aux['NCBI Species Taxonomy'] == None else [str(item.strip()) for item in metadata_aux['NCBI Species Taxonomy'].split(',')],
            "Disease Ontology Name": None if metadata_aux['Disease Ontology Name'] == None else [str(item.strip()) for item in metadata_aux['Disease Ontology Name'].split(',')],
            "Disease Ontology ID " : None if metadata_aux['Disease Ontology ID '] == None else [str(item.strip()) for item in metadata_aux['Disease Ontology ID '].split(',')],
            "SNOMED ID":  None if metadata_aux["SNOMED ID"] == None else handle_values(metadata_aux, "SNOMED ID"),
            "SNOMED label": None if metadata_aux["SNOMED label"] == None else handle_values(metadata_aux, "SNOMED label"),
            "Cognitive Atlas concept": None if metadata_aux['Cognitive Atlas concept(s)'] == None else handle_values(metadata_aux, 'Cognitive Atlas concept(s)'),
            "Cognitive Atlas task": None if metadata_aux['Cognitive Atlas task(s)'] == None else handle_values(metadata_aux, 'Cognitive Atlas task(s)')
        }
    # ====================================================================================================
    type_ = {"type": "dataset"}
    name = {"name" : aux_dict["dataset_info"][1]['values']}
    description = {"description": aux_dict["dataset_info"][2]['values']}

    # ===================================== Join Dataset ID and Name =====================================  
    try:
        pn_id_xlsx = aux_dict["dataset_info"][19]['internet link/desription']
    except (IndexError, TypeError): # in case the given xlsx file has emtpy field for PN ID
        pn_id_xlsx = metadata_aux['PN ID']
        #print(f">>> PN ID field in the given xlsx file is empty! It is now set to 'PN00000X'.")
        pass
    dataset_id = {"dataset_id": str(" ".join((metadata_aux['PN ID'], metadata_aux['title'])))}
    # ====================================================================================================
    dataset_version = {"dataset_version": None if metadata_aux['dataset version'] == None else "V"+str(metadata_aux['dataset version'])} 
    doi = {"doi" : metadata_aux['DOI']}
    # ===================================== DOWNLOAD URL ===================================== 
    a = "https://datacatalog.publicneuro.eu/dataset/"
    b = str(" ".join((metadata_aux['PN ID'], metadata_aux['title'])))
    c = "/"
    d = "V"+str(metadata_aux['dataset version'])
    download_url = {"download_url": str(a+b+c+d).replace(" ", "%20")}
    # ====================================================================================================
    keywords = {"keywords": [str(item.strip()) for item in aux_dict["dataset_info"][3]['values'].split(',')]}
    license = {"license": {"name": "Data User Agreement"}}
    authors_ = authors
    funding_ = funding
    publication_ = publication
    # ===================================== METADATA SOURCES =====================================
    metadata_sources = {
    'metadata_sources': {
        'sources': [
            {'source_name': info['Unnamed: 1'], 
             'source_version': "V"+str(metadata_aux['dataset version']), 
             'agent_name': info['# Metadata record for PublicnEUro']}
            for info in aux_dict["dataset curators"][2:]]}}
    #metadata_sources = {"metadata_sources": {"sources": [ {"source_name": "Neurobiology Research Unit", "source_version": "1", "agent_name": "Cyril Pernet"}, {"source_name": "Neurobiology Research Unit", "source_version": "1", "agent_name": "Cheng-Teng Ip"}, {"source_name": "Neurobiology Research Unit", "source_version": "1", "agent_name": "Patrick Fisher"}]}}
    # =============================================================================================
    additional_display = [metadata, participants]
    
    key_list=["type","name","description","dataset_id","dataset_version","doi", "download_url","keywords","license","authors","funding","publications","metadata_sources","additional_display"]
    val_list=[type_, name  , description , dataset_id , dataset_version , doi , download_url  , keywords , license , authors_, funding_, publication_ , metadata_sources , additional_display ]
    final_dict = dict()
    
    for k, v in zip(key_list, val_list):
        if isinstance(v, dict):
            final_dict.update(v)
        else:
            final_dict[k] = v


    #match = re.search(r'[^/\\]+(?=\.[^/\\]+$)', input_file)  
    #if match:
    #    filename = match.group(0) 
    with open(input_file.split(".")[0]+".jsonl", 'w') as jsonl_file:
        jsonl_file.write(json.dumps(final_dict) + '\n')

if __name__ == '__main__':

    #input_file = 'PublicnEUro_record.xlsx'
    input_file = "data_import/Aggression/PublicnEUro_record_Aggression.xlsx"
    xlsx2jsonl(input_file)


