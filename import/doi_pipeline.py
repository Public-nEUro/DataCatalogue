# This script only makes sure that metadata has an updated doi identifier. 
# It is a part of other functions
import random, string, json, sys

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

    print(f"\t     +++ Dataset has been updated!")
    print(f"\t     +++ Created full DOI: {full_doi}")
    print(f"\t     +++ Updated dataset:\n")
    print(json.dumps(load_('dataset_.json'), indent=8))
    print()

# ===========================================================>>> step 0: specify filenames to be processed in this doi pipeline
if len(sys.argv) < 3:
    print("\n\t [X] Please make sure you have provided the NP ID and metadata.jsonl as arguments while running doi_pipeline.py.\n\t     +++ PN ID e.g. PN0000Xa, PN0000Xb, etc.\n\t     +++ metadata.jsonl e.g. PublicnEUro_record_Aggression.jsonl")
    print("\n\t [X] Usecase: python3 doi_pipeline.py PN000002 PublicnEUro_record_Aggression.jsonl")
    sys.exit(1)
project = str(sys.argv[1])

metadata_file = str(sys.argv[2]) #"PublicnEUro_record_Aggression.jsonl"
dataset_info = load_(metadata_file)

print(f"\n\t [X] PN ID: {project}")
# ===========================================================>>> step 1: update doi
# dataset_.json is simply a file with a dictionary that holds project name as keys, and project doi as values
"""
USECASE: Given a project name:
 + 1. Generate doi suffix
 + 2. Update the doi in dataset_.json
"""
if project in list(load_("dataset_.json").keys()) and load_("dataset_.json")[project].__len__() == 8:
    print(f"\n\t     +++ PN ID already exist. DOI: {load_('dataset_.json')[project]}")
    updated_doi = load_("dataset_.json")
else: 
    doi_pipeline(project) # we should call/generated doi only if it does not exist
    updated_doi = load_("dataset_.json")


# ===========================================================>>> step 2: update DOI in dataset metadata
"""
Here we make sure if the final metadata has been updated by latest generated doi. It will pass if so, otherwise it will be updated.
"""

if dataset_info['doi'].split('/')[-1].__len__() == 8:    
    if dataset_info['doi'].split('/')[-1] == updated_doi[project]:
        print(f"\t     +++ Metadata has already been updated.")
    if dataset_info['doi'].split('/')[-1] != updated_doi[project]:
        print(f"\t     [x] ===> NOTICE:")
        print(f"\t     +++ Metadata has already been updated. However DOIs are different.")
        print(f"\t     +++ Metadata DOI: {dataset_info['doi']}")
        print(f"\t     +++ dateset_.json DOI: {'10.70883/'+updated_doi[project]}")   
        print(f"\t     +++ You can either open '{metadata_file}', and edit DOI to '{'10.70883/'+updated_doi[project]}' manually, or '10.70883/XXXX' and run this file again")
if dataset_info['doi'].split('/')[-1] == "XXXX":
    dataset_info['doi'] = dataset_info['doi'][:-4]+updated_doi[project]
    print(f"\n\t [X] Updated DOI: {dataset_info['doi']} in metadata file: {metadata_file}")
with open(metadata_file, 'w') as jsonl_file:
    jsonl_file.write(json.dumps(dataset_info) + '\n')
