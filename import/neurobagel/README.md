# PublicNeuro to Neurobagel conversion

`PN2Neurobaguel.py` creates graph-ready Neurobagel JSON-LD for a
PublicNeuro BIDS dataset. It coordinates `BIDS2Neurobaguel.py` and the
Neurobagel `bagel` command-line interface.

## Prerequisites

- Python 3
- A local PublicNeuro dataset organized as BIDS and containing
  `dataset_description.json`
- A phenotypic TSV file, usually the BIDS `participants.tsv` or a derived TSV
- A Neurobagel-annotated JSON data dictionary describing that TSV
- The Neurobagel `bagel` CLI

By default, `PN2Neurobaguel.py` upgrades or installs `bagel` with `pip` before
running. Use `--no-update-bagel` to use the version already available on
`PATH` without attempting an installation or upgrade.

## Required directory layout

The output directory must already exist and located inside the node target (here the target is /dpnru002/shared/group/neurobagel/data so the output directory is /dpnru002/shared/group/neurobagel/data/PN.... and of course the PublicNeuro ID must already exist. The ID is inferred from a name (it can be supplied with `--dataset-id`). 

Unless `--pheno` and `--dictionary` are supplied, the script expects the phenotypic TSV and annotated dictionary to already be in that directory with these exact names:
```text
/path/to/output/
└── PN000024/
    ├── PN000024_phenotypic.tsv
    └── PN000024_phenotypic.json
```

The JSON file is the annotated Neurobagel data dictionary; annotating only the
TSV is not sufficient. These inputs are not created by this script. Existing files may have different names or live elsewhere when their paths are given explicitly:

```bash
--pheno /path/to/participants.tsv \
--dictionary /path/to/participants_annotated.json
```

## Usage

From the repository root:

```bash
python data/PN2Neurobaguel.py /dpnru002/data/raw/PN0000XX/folder_name
  --access-type restricted 
  --access-link https://doi.org/10.70883/XXXXXXXX
  --pheno /dpnru002/data/raw/PN0000XX/folder_name/participants.tsv
  --no-update-bagel
```

The output root defaults to `/dpnru002/shared/group/neurobagel/data`. The
script infers `PN0000XX` from the input path and finds the annotated dictionary
at `/dpnru002/shared/group/neurobagel/data/PN0000XX/PN0000XX_phenotypic.json`.
`--output-folder` remains available as an override.

For the filenames currently used in the local `PN0000XX` directory, an
explicit invocation would look like:

```bash
python PN2Neurobaguel.py /dpnru002/data/raw/PN0000XX/folder_name
  --access-type restricted 
  --access-link https://doi.org/10.70883/XXXXXXXX
  --output-folder /dpnru002/shared/group/neurobagel/data/PN0000XX
  --pheno /dpnru002/data/raw/PN0000XX/folder_nameparticipants.tsv 
  --dictionary /dpnru002/shared/group/neurobagel/data/PN0000XX/participants_annotated.json \
  --no-update-bagel
```

Replace the dataset path, access link, and phenotypic TSV path with the real
values.

Run the built-in help for all options:

```bash
python data/PN2Neurobaguel.py --help
```

## Workflow

1. `PN2Neurobaguel.py` validates the BIDS dataset, output directory,
   phenotypic TSV, and annotated dictionary.
2. It launches `BIDS2Neurobaguel.py` as a separate Python process. That script
   converts the BIDS `dataset_description.json` into the Neurobagel dataset
   metadata file `<output>/dataset_description.json`.
3. `bagel bids2tsv` scans the BIDS dataset and creates
   `<output>/<PN_ID>_bids.tsv` containing its imaging metadata.
4. `bagel pheno` combines the phenotypic TSV, annotated dictionary, and
   converted dataset description into a working
   `<output>/<PN_ID>/<PN_ID>.jsonld`.
5. `bagel bids` adds the imaging metadata to that JSON-LD file.
6. The completed JSON-LD is moved to `<output>/<PN_ID>.jsonld`, where the
   Neurobagel client can find it.

In short:

```text
BIDS dataset_description.json
        │
        ▼
BIDS2Neurobaguel.py ──► output/dataset_description.json
                                  │
phenotypic TSV + annotated JSON ──┼──► bagel pheno ──► <PN_ID>.jsonld
                                  │                         ▲
BIDS dataset ──► bagel bids2tsv ──┴──► <PN_ID>_bids.tsv ───┘
                                                    bagel bids
```

`BIDS2Neurobaguel.py` is therefore used indirectly: it is not imported, but
is located beside `PN2Neurobaguel.py` and executed with the active Python
interpreter.

## Useful options

- `--dataset-id PN000024`: override dataset-ID inference.
- `--pheno PATH`: use a phenotypic TSV other than the default.
- `--dictionary PATH`: use an annotated dictionary other than the default.
- `--skip-bids`: skip `bagel bids2tsv` and `bagel bids`; produce phenotypic
  JSON-LD only.
- `--overwrite`: pass `--overwrite` to `bagel bids` when updating the JSON-LD.
- `--no-update-bagel`: do not install or upgrade `bagel`.

## Outputs

After a complete run, the output root contains:

```text
/dpnru002/shared/group/neurobagel/data/
├── PN000024.jsonld               # final graph-ready output for the client
└── PN000024/
    ├── PN000024_phenotypic.tsv   # optional pre-existing phenotype input
    ├── PN000024_phenotypic.json  # pre-existing annotated dictionary
    ├── dataset_description.json  # created by BIDS2Neurobaguel.py
    └── PN000024_bids.tsv         # created by bagel bids2tsv
```

With `--skip-bids`, the BIDS TSV is not created and imaging metadata is not
added to the final JSON-LD.

The minimal invocation, using the built-in output root and inferred PN name,
is:

```bash
python PN2Neurobaguel.py /dpnru002/data/raw/PN000024/PMG-BrainDrugs --access-type restricted --access-link https://doi.org/10.70883/GBSQ9852 --pheno /dpnru002/data/raw/PN000024/PMG-BrainDrugs/participants.tsv --no-update-bagel
```
