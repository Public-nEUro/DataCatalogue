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

    print(f"\nDataset has been updated!")
    print(f"Created full DOI: {full_doi}")
    print(f"Updated dataset:\n")
    print(json.dumps(load_('dataset_.json'), indent=4))
    print()
    
if __name__ == '__main__':
    doi_pipeline("PN000005")
