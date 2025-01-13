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

### Creating a dataset

```bash
cd ../import/data_import/
```
```python
python3
from get_files import get_file_info as gf
from listjl2filetype import listjl2filetype as l2f
l2f('PN000002 Aggression Project.jsonl', 'file_list.jsonl', 'PublicnEuro', 'agent_name') # agent_name is the admin person dealing with the dataset
exit()
python3 -m venv my_catalog_env
source my_catalog_env/bin/activate
pip install datalad-catalog
datalad catalog-validate --metadata DataCatalogue/import/data_import/Datasetfolder/the_new_file.jsonl
datalad catalog-add --catalog DataCatalogue --metadata DataCatalogue/import/data_import/Datasetfolder/the_new_file.jsonl
```

### Re-recreating the catalogue





