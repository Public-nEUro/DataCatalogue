import random, string, json

def load_(filename):
    with open(filename, 'r') as f:
        data = json.load(f)
    return data

def save_(data, filename):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)

def generate_doi():
    doi_resolver = "https://doi.org"
    nru_prefix = "10.70883"
    suffix = ''.join(random.choices(string.ascii_uppercase, k=4)) + str(random.randint(1000, 9999))
    return f"{doi_resolver}/{nru_prefix}/{suffix}"

def doi_pipeline(project):
    full_doi = generate_doi()
    suffix_doi = full_doi.split('/')[-1]
    datasets = load_('dataset_.json')

    while suffix_doi in datasets.values():
        full_doi = generate_doi()
        suffix_doi = full_doi.split('/')[-1]

    datasets[project] = suffix_doi
    save_(datasets, 'dataset_.json')

    print(f"\n - Dataset has been updated!")
    print(f" - Created full DOI: {full_doi}")
    print(f" - Updated dataset:\n")
    print(json.dumps(load_('dataset_.json'), indent=4))
    print()

# ===========================================================>>> step 0: specify filenames to be processed in this doi pipeline
project = "PN000002"

xml_file = "xml_dict.json"
xml_dict = load_(xml_file)

metadata_file = "/data_import/Aggression/PublicnEUro_record_Aggression.jsonl"
dataset_info = load_(metadata_file)

print(f" - Project identifier: {project}")
# ===========================================================>>> step 1: update doi
# dataset_.json is simply a file with a dictionary that holds project name as keys, and project doi as values
"""
USECASE: Given a project name:
 + 1. Generate doi suffix
 + 2. Update the doi in dataset_.json
"""
if project in list(load_("dataset_.json").keys()) and load_("dataset_.json")[project].__len__() == 8:
    print(f" - Project already exist. DOI: {load_('dataset_.json')[project]}")
    updated_doi = load_("dataset_.json")
else: 
    doi_pipeline(project) # we should call/generated doi only if it does not exist
    updated_doi = load_("dataset_.json")

# ===========================================================>>> step 2: update xml_dict.json
# There is xml_dict.json file created by default input. here we only update the doi
# This file will later be used to create xml file

if xml_dict['body']['database']['database_metadata']['doi_data']['doi'].split("/")[1].__len__() == 8:
    if xml_dict['body']['database']['database_metadata']['doi_data']['doi'].split("/")[1] == load_("dataset_.json")[project]:
        print()
        print(f" + \t ===> NOTE! <===")
        print(f" - xml_dict.json has already been updated.")
    if xml_dict['body']['database']['database_metadata']['doi_data']['doi'].split("/")[1] != load_("dataset_.json")[project]:
        print()
        print(f" + \t ===> NOTE! <===")
        print(f" - xml_dict.json has already been updated. However DOIs are different.")
        print(f" - xml_dict.json DOI: {xml_dict['body']['database']['database_metadata']['doi_data']['doi']}")
        print(f" - dateset_.json DOI: {'10.70883/'+updated_doi[project]}")   
if xml_dict['body']['database']['database_metadata']['doi_data']['doi'].split("/")[1] == "XXXX":
    xml_dict['body']['database']['database_metadata']['doi_data']['doi'] = "10.70883/"+updated_doi[project]
    print(f"\n - Updated DOI: {xml_dict['body']['database']['database_metadata']['doi_data']['doi']} in xml file: {xml_file}")
save_(xml_dict, xml_file)

# ===========================================================>>> step 3: update DOI in dataset metadata
"""
Here we make sure if the final metadata has been updated by latest generated doi. It will pass if so, otherwise it will be updated.
"""

if dataset_info['doi'].split('/')[-1].__len__() == 8:    
    if dataset_info['doi'].split('/')[-1] == updated_doi[project]:
        print()
        print(f" + \t ===> NOTE! <===")
        print(f" - Metadata has already been updated.")
    if dataset_info['doi'].split('/')[-1] != updated_doi[project]:
        print()
        print(f" + \t ===> NOTE! <===")
        print(f" - Metadata has already been updated. However DOIs are different.")
        print(f" - Metadata DOI: {dataset_info['doi']}")
        print(f" - dateset_.json DOI: {'10.70883/'+updated_doi[project]}")   

if dataset_info['doi'].split('/')[-1] == "XXXX":
    dataset_info['doi'] = dataset_info['doi'][:-4]+updated_doi[project]
    print(f"\n - Updated DOI: {dataset_info['doi']} in metadata file: {metadata_file}\n")
with open(metadata_file, 'w') as jsonl_file:
    jsonl_file.write(json.dumps(dataset_info) + '\n')
