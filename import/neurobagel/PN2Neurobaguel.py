"""Create Neurobagel graph-ready JSON-LD for a PublicNeuro BIDS dataset.

This script wraps the documented Neurobagel CLI workflow:

1. Convert the BIDS dataset_description.json into Neurobagel dataset metadata.
2. Run ``bagel bids2tsv`` to summarize BIDS imaging files.
3. Run ``bagel pheno`` using a phenotypic TSV and annotated Neurobagel dictionary.
4. Run ``bagel bids`` to add imaging metadata to the JSON-LD output.

Example:
    python PN2Neurobaguel.py /dpnru002/data/raw/PN000024/PMG-BrainDrugs
        --access-type restricted 
        --access-link https://doi.org/10.70883/GBSQ9852 
        --pheno /dpnru002/data/raw/PN000024/PMG-BrainDrugs/participants.tsv
        --no-update-bagel
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path


DEFAULT_OUTPUT_FOLDER = Path("/dpnru002/shared/group/neurobagel/data")
DATASET_ID_PATTERN = re.compile(r"PN\d+", re.IGNORECASE)


def existing_file(path: Path, label: str) -> Path:
    resolved = path.expanduser().resolve()
    if not resolved.is_file():
        raise FileNotFoundError(f"{label} not found: {resolved}")
    return resolved


def existing_dir(path: Path, label: str) -> Path:
    resolved = path.expanduser().resolve()
    if not resolved.is_dir():
        raise NotADirectoryError(f"{label} not found: {resolved}")
    return resolved


def infer_dataset_id(dataset_folder: Path) -> str:
    for candidate in [dataset_folder.name, str(dataset_folder)]:
        match = DATASET_ID_PATTERN.search(candidate)
        if match:
            return match.group(0).upper()
    raise ValueError(
        "Could not infer a PublicNeuro dataset ID from the dataset folder. "
        "Pass --dataset-id, e.g. --dataset-id PN000024."
    )


def resolve_output_paths(output_folder: Path, dataset_id: str) -> tuple[Path, Path]:
    """Return the Neurobagel data root and its per-dataset work directory."""
    resolved = output_folder.expanduser().resolve()

    if resolved.name.upper() == dataset_id.upper():
        output_root = resolved.parent
        output_dir = resolved
    else:
        output_root = resolved
        output_dir = resolved / dataset_id

    if not output_dir.is_dir():
        raise NotADirectoryError(
            f"Expected existing output directory for {dataset_id}: {output_dir}"
        )

    if output_dir.name.upper() != dataset_id.upper():
        raise ValueError(
            f"Output directory name ({output_dir.name}) does not match dataset ID "
            f"({dataset_id})."
        )

    return output_root, output_dir


def run_command(command: list[str], cwd: Path | None = None) -> None:
    printable = " ".join(f'"{part}"' if " " in part else part for part in command)
    print(f"Running: {printable}")
    subprocess.run(command, cwd=cwd, check=True)


def ensure_bagel_available(update: bool) -> None:
    if update or shutil.which("bagel") is None:
        run_command([sys.executable, "-m", "pip", "install", "--upgrade", "bagel"])

    if shutil.which("bagel") is None:
        raise RuntimeError(
            "The Neurobagel CLI executable 'bagel' is still not available on PATH "
            "after attempting 'python -m pip install --upgrade bagel'. Check that "
            "the Python scripts directory for this environment is on PATH."
        )

    run_command(["bagel", "--version"])


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate Neurobagel JSON-LD for a PublicNeuro BIDS dataset."
    )
    parser.add_argument(
        "publicneuro_dataset_folder",
        type=Path,
        help="Path to the PublicNeuro BIDS dataset folder.",
    )
    parser.add_argument(
        "--pheno",
        type=Path,
        help=(
            "Phenotypic TSV file. Defaults to "
            "<output-folder>/<PN_ID>/<PN_ID>_phenotypic.tsv."
        ),
    )
    parser.add_argument(
        "--dictionary",
        type=Path,
        help=(
            "Neurobagel-annotated JSON data dictionary for --pheno. Defaults to "
            "<output-folder>/<PN_ID>/<PN_ID>_phenotypic.json."
        ),
    )
    parser.add_argument(
        "--access-type",
        required=True,
        choices=["public", "restricted"],
        help="Neurobagel dataset access type.",
    )
    parser.add_argument(
        "--access-link",
        required=True,
        help="Primary dataset access link or DOI URL.",
    )
    parser.add_argument(
        "--output-folder",
        type=Path,
        default=DEFAULT_OUTPUT_FOLDER,
        help=(
            "Existing dataset output folder, or its parent folder. If the parent "
            "is given, <PN_ID> is appended. Defaults to "
            "/dpnru002/shared/group/neurobagel/data. Intermediate files remain "
            "under <PN_ID>; the final JSON-LD is placed in this parent folder."
        ),
    )
    parser.add_argument(
        "--dataset-id",
        help="PublicNeuro dataset ID. Inferred from the dataset folder if omitted.",
    )
    parser.add_argument(
        "--skip-bids",
        action="store_true",
        help="Skip BIDS imaging table creation and only run bagel pheno.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help=(
            "Deprecated compatibility option. The final bagel bids merge now "
            "always overwrites its JSON-LD input."
        ),
    )
    parser.add_argument(
        "--no-update-bagel",
        action="store_true",
        help=(
            "Do not run 'python -m pip install --upgrade bagel' before conversion. "
            "The script still checks that bagel is available."
        ),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    dataset_folder = existing_dir(
        args.publicneuro_dataset_folder, "PublicNeuro dataset folder"
    )
    bids_description = existing_file(
        dataset_folder / "dataset_description.json", "BIDS dataset_description.json"
    )
    dataset_id = args.dataset_id or infer_dataset_id(dataset_folder)
    output_root, output_dir = resolve_output_paths(args.output_folder, dataset_id)

    default_pheno = output_dir / f"{dataset_id}_phenotypic.tsv"
    default_dictionary = output_dir / f"{dataset_id}_phenotypic.json"
    pheno_tsv = existing_file(args.pheno or default_pheno, "Phenotypic TSV")
    dictionary_json = existing_file(
        args.dictionary or default_dictionary, "Phenotypic data dictionary"
    )

    ensure_bagel_available(update=not args.no_update_bagel)

    dataset_description = output_dir / "dataset_description.json"
    bids_table = output_dir / f"{dataset_id}_bids.tsv"
    working_jsonld = output_dir / f"{dataset_id}.jsonld"
    jsonld_output = output_root / f"{dataset_id}.jsonld"

    converter = Path(__file__).resolve().with_name("BIDS2Neurobaguel.py")
    existing_file(converter, "BIDS2Neurobaguel.py")

    run_command(
        [
            sys.executable,
            str(converter),
            str(bids_description),
            args.access_type,
            args.access_link,
            str(dataset_description),
        ]
    )

    if not args.skip_bids:
        run_command(
            [
                "bagel",
                "bids2tsv",
                "--bids-dir",
                str(dataset_folder),
                "--output",
                str(bids_table),
                "--overwrite",
            ]
        )

    run_command(
        [
            "bagel",
            "pheno",
            "--pheno",
            str(pheno_tsv),
            "--dictionary",
            str(dictionary_json),
            "--dataset-description",
            str(dataset_description),
            "--output",
            str(working_jsonld),
            "--overwrite",
        ],
        cwd=output_dir,
    )

    if not args.skip_bids:
        bids_command = [
            "bagel",
            "bids",
            "--jsonld-path",
            str(working_jsonld),
            "--bids-table",
            str(bids_table),
            "--output",
            str(working_jsonld),
            "--overwrite",
        ]
        run_command(bids_command, cwd=output_dir)

    working_jsonld.replace(jsonld_output)
    print(f"Wrote Neurobagel JSON-LD to {jsonld_output}")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
