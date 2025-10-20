# Testing PNC00001 as a File/Directory Container Instead of Dataset

## Goal
Make PNC00001 UCB-J consortium appear as a container/collection with children datasets, 
but NOT count as a dataset itself in the catalog count.

## What Was Changed

Created `UCBJ_consortium_test.jsonl` with these key changes:

1. **Type changed**: `"type": "dataset"` → `"type": "file"`
2. **Added required file fields**:
   - `"path": "PNC00001 UCB-J consortium"`
   - `"contentbytesize": 0` (indicates it's a directory)
3. **Parent dataset**: `"dataset_id": "super"` (makes it part of superdataset)
4. **Changed subdatasets format**: 
   - Removed `subdatasets` array
   - Changed to `children` array with dataset type references
5. **Moved metadata**: Description, keywords, etc. moved to `additional_display`

## Commands to Run on Server

### Step 1: Navigate to the directory
```bash
cd /path/to/PublicnEUro/DataCatalogue/import/data_import/PNC00001\ UCB-J_consortium
```

### Step 2: Validate the test file
```bash
datalad catalog-validate --metadata UCBJ_consortium_test.jsonl
```

**Expected outcome**: Should validate successfully (exit code 0)

### Step 3: If validation passes, add to catalog
```bash
cd /path/to/PublicnEUro/DataCatalogue
datalad catalog-add --catalog . --metadata 'import/data_import/PNC00001 UCB-J_consortium/UCBJ_consortium_test.jsonl'
```

### Step 4: Check the result in the catalog
```bash
datalad catalog-serve --catalog .
```

Then browse to the catalog and check:
- Does PNC00001 appear in the file tree of the superdataset?
- Does it show its children datasets when clicked?
- Does the dataset count exclude PNC00001 (showing only the 8 actual datasets)?

## Troubleshooting

### If validation fails:
The error message will indicate what's wrong. Common issues:
- Missing required fields for file type
- Invalid children structure
- Schema mismatch

### If it works but doesn't display correctly:
We may need to adjust:
- The `children` structure
- The `path` field
- The `additional_display` content

### Alternative approach if file type doesn't work:
Keep it as `"type": "dataset"` but investigate catalog configuration to:
- Exclude certain dataset_id patterns from the count
- Mark it as a "collection" type in metadata
- Use catalog filtering features

## Rollback
If the test doesn't work, the original file is still intact:
```bash
# Original is in UCBJ_consortium.jsonl
# Can re-import that if needed
```

## Next Steps After Testing

1. If successful: Replace `UCBJ_consortium.jsonl` with the new version
2. Update the superdataset to reference PNC00001 as a file in its hasPart
3. Remove old PNC00001 metadata if needed
4. Re-generate catalog

## Notes

- The file type with contentbytesize=0 is how datalad-catalog represents directories
- Children can be datasets (as shown in the example you referenced)
- This should make PNC00001 browsable but not counted as a dataset itself
