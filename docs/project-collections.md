# Project collection pages

A project page groups published datasets under a public description of their shared research question. The [fictional Your Project page](https://datacatalog.publicneuro.eu/dataset/super/yourproject) demonstrates the layout with two sample records. Its `is_example: true` flag makes the fictional nature visible and disables citation, metadata export, and data access actions. No example is added to the main catalogue.

The main collection at `/dataset/super/V1` remains the complete repository listing. Real dataset versions have one authoritative metadata record each, with a PN identifier and their own DOI. A project page points to those records; it does not copy them or mint a project-wide dataset DOI.

## Make a real collection

1. Choose a short URL slug, such as `yourproject`, and write a description explaining the scientific aims, related studies, participating groups, data types, shared governance, and how to use the collection.
2. Identify the exact `dataset_id` and `dataset_version` of every published PN record. Use the same strings as the main `/dataset/super/V1` collection. A version change should be a deliberate update to the project collection.
3. Create a JSON record with `dataset_id: "super"`, `dataset_version: "yourproject"`, a name, description, keywords, `metadata_sources`, and the `children` and `subdatasets` shown below. Do **not** set `is_example` for a real project. The `children` list is used by the Content tree; `subdatasets` drives the searchable Datasets tab.
4. Place the record at the hashed path generated from `super-yourproject` (see below). Optionally set `metadata/super/yourproject/config.json` to `{ "dataset_options": { "default_tab": "datasets" } }`.
5. Check the project page and each child link. The version-specific PN page remains the point of citation and access; retain the PN record in the main collection. Do not duplicate or edit the PN metadata just to give it a project-specific presentation.

Minimal layout (replace the illustrative PN name with an existing exact ID):

```json
{
  "type": "dataset",
  "dataset_id": "super",
  "dataset_version": "yourproject",
  "name": "Your project title",
  "description": "Project aims, datasets, governance and how to reuse the collection.",
  "metadata_sources": {
    "sources": [{
      "source_name": "Project team",
      "source_version": "1",
      "agent_name": "Project team",
      "source_time": 1791504000
    }]
  },
  "children": [{
    "type": "dataset",
    "name": "Published dataset name",
    "dataset_id": "PN000001 OpenNeuroPET Phantoms",
    "dataset_version": "V2"
  }],
  "subdatasets": [{
    "dataset_id": "PN000001 OpenNeuroPET Phantoms",
    "dataset_version": "V2",
    "dataset_path": "PN000001 OpenNeuroPET Phantoms",
    "dirs_from_path": ["PN000001 OpenNeuroPET Phantoms"]
  }]
}
```

The catalog resolves a record from the MD5 of `dataset_id + "-" + dataset_version`. For example:

```python
import hashlib

dataset_id, version = "super", "yourproject"
digest = hashlib.md5(f"{dataset_id}-{version}".encode("utf-8")).hexdigest()
path = f"metadata/{dataset_id}/{version}/{digest[:3]}/{digest[3:]}.json"
print(path)
```

The two fictional records in this example live at `example-yourproject-mri/V1` and `example-yourproject-eeg/V1`. They have no PN identifiers, DOI, download URL, or access request route and are not listed in `/dataset/super/V1`. Replace their entries in `children` and `subdatasets` with real PN records when adapting the template; remove the fictional metadata files from the adapted collection.
