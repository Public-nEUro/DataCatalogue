# Context

The static website is generated thanks to https://docs.datalad.org/projects/catalog/en/latest/.

Our /import folder contains the metadata from users and file listing from the servers ; those get imported to /metadata and displayed via index.html

## Test

outside the catalogue folder validate and import a dataset

```
datalad catalog-validate --metadata 'DataCatalogue/import/somedataset'
datalad catalog-add --catalog DataCatalogue --metadata 'DataCatalogue/import/somedataset'
```

then add it to the PublicnEUro_superdataset.jsonl and again validate and import

```
datalad catalog-validate --metadata 'DataCatalogue/import/PublicnEUro_superdataset.jsonl'
datalad catalog-add --catalog DataCatalogue --metadata 'DataCatalogue/import/PublicnEUro_superdataset.jsonl'
```

Finally, check the webpage is as wanted

```
datalad catalog-serve --catalog DataCatalogue/
```
