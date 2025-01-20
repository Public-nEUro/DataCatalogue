import subprocess
import sys

def install_openpyxl():
    subprocess.check_call([sys.executable, "-m", "pip", "install", "openpyxl", "--quiet"])

# Install openpyxl
install_openpyxl()

# Now you can import and use openpyxl
import openpyxl
import pandas as pd
import json, re

def xlsx2jsonl(input_file):

    #input_file = 'PublicnEUro_record_Aggression.xlsx'
    excel_data = pd.read_excel(input_file, sheet_name=None, engine='openpyxl')
    
    key_var=["type","name","description","dataset_id","dataset_version","keywords","license","authors","funding","publications","metadata_sources","additional_display"]
    aux_dict = dict()
    for sheet_name, df in excel_data.items():
        aux_dict[sheet_name] = df.to_dict(orient='records')
        
    
    authors = list()
    for i in aux_dict["authors"][2:]:
        authors.append({
            'givenName': i['# Metadata record for PublicnEUro'].split(" ")[0],
            'familyName': " ".join(i['# Metadata record for PublicnEUro'].split(" ")[1:])
        })
    
    funding = list()
    for i in aux_dict["funding"][2:]:
        funding.append({
            'name' : i['# Metadata record for PublicnEUro'],
            'identifier' : i['Unnamed: 1']
        })
    
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
    
    participants = dict()
    for i in aux_dict["participants_info"]:
        participants["name"] = "Participants"
        participants["content"] = {
            "total_number": [str([i['Unnamed: 1'] for i in aux_dict["participants_info"]][0])], 
            "age_range": [[i['Unnamed: 1'] for i in aux_dict["participants_info"]][6].replace(" ", ",")], 
            "number_of_healthy": [str([i['Unnamed: 1'] for i in aux_dict["participants_info"]][4])], 
            "number_of_patients": [str([i['Unnamed: 1'] for i in aux_dict["participants_info"]][5])], 
            "number_of_biological_males": [str([i['Unnamed: 1'] for i in aux_dict["participants_info"]][1])], 
            "number_of_biological_females": [str([i['Unnamed: 1'] for i in aux_dict["participants_info"]][2])]
        }
    
    metadata = dict()
    for i in aux_dict["dataset_info"]:
        metadata["name"] = "Dataset Metadata"
        metadata["content"] = {
            "bids_version" : [str(item.strip()) for item in aux_dict["dataset_info"][5]['values'].split(',')],
            "bids_datasettype" : [str(item.strip()) for item in aux_dict["dataset_info"][4]['values'].split(',')],
            "bids_datatypes" : [str(item.strip()) for item in aux_dict["dataset_info"][6]['values'].split(',')],
            "NCBI Species Taxonomy": [str(item.strip()) for item in aux_dict["dataset_info"][7]['values'].split(',')],
            "Disease Ontology Name": [str(item.strip()) for item in aux_dict["dataset_info"][9]['values'].split(',')],
            "Disease Ontology ID " : str(aux_dict["dataset_info"][8]['values']),
            "SNOMED ID": [str(item.strip()) for item in aux_dict["dataset_info"][10]['values'].split(',')],
            "SNOMED label": [str(item.strip()) for item in aux_dict["dataset_info"][11]['values'].split(',')],
            "Cognitive Atlas concept": [str(item.strip()) for item in aux_dict["dataset_info"][12]['values'].split(',')],
            "Cognitive Atlas task": [str(item.strip()) for item in aux_dict["dataset_info"][13]['values'].split(',')]
        }
    
    type_ = {"type": "dataset"}
    name = {"name" : aux_dict["dataset_info"][1]['values']}
    description = {"description": aux_dict["dataset_info"][2]['values']}
    dataset_id = {"dataset_id": "PN000002 Aggression Project"}
    dataset_version = {"dataset_version": "V1"}
    keywords = {"keywords": [str(item.strip()) for item in aux_dict["dataset_info"][3]['values'].split(',')]}
    license = {"license": {"name": "Data User Agreement"}}
    authors_ = authors
    funding_ = funding
    publication_ = publication
    metadata_sources = {"metadata_sources": {"sources": [ {"source_name": "Neurobiology Research Unit", "source_version": "1", "agent_name": "Cyril Pernet"}, {"source_name": "Neurobiology Research Unit", "source_version": "1", "agent_name": "Cheng-Teng Ip"}, {"source_name": "Neurobiology Research Unit", "source_version": "1", "agent_name": "Patrick Fisher"}]}}
    additional_display = [participants, metadata]
    
    key_list=["type","name","description","dataset_id","dataset_version","keywords","license","authors","funding","publications","metadata_sources","additional_display"]
    val_list=[type_, name  , description , dataset_id , dataset_version , keywords , license , authors_, funding_, publication_ , metadata_sources , additional_display ]
    final_dict = dict()
    
    for k, v in zip(key_list, val_list):
        if isinstance(v, dict):
            final_dict.update(v)
        else:
            final_dict[k] = v

    match = re.search(r'[^/\\]+(?=\.[^/\\]+$)', input_file)  
    if match:
        filename = match.group(0) 
    with open(filename+".jsonl", 'w') as jsonl_file:
        jsonl_file.write(json.dumps(final_dict) + '\n')
        
if __name__ == '__main__':

    xlsx2jsonl(input_file)


