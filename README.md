# This branch

The goal of this branch is to learn how our catalogue is set-up and allow some testing.

## DataLad Catalog

We rely on [datalad-catalog](https://github.com/datalad/datalad-catalog/) to populate the metatada and render them on the web. The `index.html` is a self-contained and static [VueJS](https://vuejs.org/)-based site that pulls to datasets from the json files located under `/metadata`.

### Content

The content of this root directory includes everything necessary to serve the static site:

```
.
├── artwork
├── assets
├── config.json
├── index.html
├── metadata
└── README.md
```

The `artwork` and `assets` directories contain images and web assets (such as JavaScript and CSS files) respectively that support the rendering of the HTML components in `index.html`. The `config.json` file contains customizable configuration options supplied to `datalad-catalog`.

## Testing ground

This branch has been stripped from all but the Aggression data in the import folder: `import/data_import/Aggression`. The PublicnEUro ID is PN000002. The folder has the excel file from the user to create the parent (dataset) metadata information, and the `file_list.jsonl` file, that lists all the files present on the server.

### Creating a study information (metadata from user)

```bash
cd ../import
```

*Create the Aggression.jsonl*
The file `import/study_template.jsonl` shows the key-values used to create this information. Here, create the new jsonl from `import/data_import/Aggression/PublicnEUro_record_Aggression.xlsx` using `xlsx2json.py`.

```python
python3
from xlsx2json import xlsx2json as x2j
import os
os.chdir('data_import/Aggression')
x2j("PublicnEUro_record_Aggression.xlsx")
```
An important key-value in the created jsonl is `"type": "dataset"`, which informs datalad that this is the metadata level. It then possible to check that the new file is valid:  

```bash
cd ../root_folder
```
```python
python3 -m venv my_catalog_env
source my_catalog_env/bin/activate
pip install datalad-catalog
datalad catalog-validate --metadata DataCatalogue/import/data_import/Aggression/Aggression.jsonl
deactivate
```
*Add file information (childrens)*

In the repository, the file `import/data_import/Aggression/file_list.jsonl` lists all the file existing on drive. We now merge that information with the study metdata. All those files will have key-value `"type": "file"` which informs datalad this is a child of the dataset.

```python
cd DataCatalogue/import/
from listjl2filetype import listjl2filetype as l2f
import os
os.chdir('data_import/Aggression')
l2f('Aggression.jsonl', 'file_list.jsonl', 'PublicnEuro', 'test_agent') 
exit()
```
A new file based on the datset name value has been created - which should be `AggressionProject.jsonl`. Again this can be tested, and if valid, imported.

```bash
cd ../root_folder
```
```python
python3 -m venv my_catalog_env
source my_catalog_env/bin/activate
datalad catalog-validate --metadata DataCatalogue/import/data_import/Aggression/AggressionProject.jsonl
datalad catalog-add --catalog DataCatalogue --metadata DataCatalogue/import/data_import/Aggression/AggressionProject.jsonl
```
Assuming all went well, the `metadata/PN000002 Aggression` folder has been created. 


### Creating the catalogue

One can check the render of our data in a browser doing:  

```python
datalad catalog-serve --catalog DataCatalogue/
```
and check the adress http://localhost:8000/

Oops, it's all empty -- that because everything is a dataset! so we need to update the superdataset, that is the one that includes them all.  

Edit the file `/import/data_import/catalogue_info.jsonl` adding under `metadata_sources` the following:  
`"subdatasets": [{"dataset_id": "PN000002 Aggression Project", "dataset_version": "V1", "dataset_path": "PN000002 Aggression Project"}]`.  

Then, as before, add it to the data catalogue (datalad catalog-add --catalog DataCatalogue  ... ). Now try again to visualize, it's all there in the browser.




