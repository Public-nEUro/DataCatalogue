"""Convert a BIDS dataset_description.json file to Neurobaguel metadata.

Usage:
    python BIDS2Neurobaguel.py C:\bids\dataset_description.json public https://example.org/dataset C:\neurobaguel\output
    access type is public or restricted
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


OUTPUT_FILENAME = "dataset_description.json"
ACCESS_INSTRUCTIONS = {
    "public": "click download and get the data",
    "restricted": "register and request access",
}


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8-sig") as f:
        data = json.load(f)

    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a JSON object")

    return data


def as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def convert_dataset_description(
    bids_description: dict[str, Any],
    access_type: str,
    repository_url: str,
) -> dict[str, Any]:
    references_and_links = as_list(bids_description.get("ReferencesAndLinks"))
    if not references_and_links:
        references_and_links.extend(as_list(bids_description.get("DatasetDOI")))
        references_and_links.extend(as_list(bids_description.get("HowToAcknowledge")))

    return {
        "Name": bids_description.get("Name", ""),
        "Authors": as_list(bids_description.get("Authors")),
        "ReferencesAndLinks": references_and_links,
        "Keywords": as_list(bids_description.get("Keywords")),
        "RepositoryURL": "https://datacatalog.publicneuro.eu/dataset/super/V1",
        "AccessInstructions": ACCESS_INSTRUCTIONS[access_type],
        "AccessType": access_type,
        "AccessEmail": "publicneuro@nru.dk",
        "AccessLink": repository_url,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Create a Neurobaguel dataset_description.json file from a BIDS "
            "dataset_description.json file."
        )
    )
    parser.add_argument(
        "bids_dataset_description",
        type=Path,
        help="Full path to the input BIDS dataset_description.json file.",
    )
    parser.add_argument(
        "access_type",
        choices=sorted(ACCESS_INSTRUCTIONS),
        help="Dataset access type. Must be public or restricted.",
    )
    parser.add_argument(
        "repository_url",
        help="Dataset URL to write to the Neurobaguel AccessLink field.",
    )
    parser.add_argument(
        "output",
        type=Path,
        help=(
            "Output directory for the Neurobaguel dataset_description.json file. "
            "If a JSON file path is given, that exact file path is used."
        ),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    bids_path = args.bids_dataset_description.expanduser().resolve()
    requested_output_path = args.output.expanduser().resolve()
    output_path = (
        requested_output_path
        if requested_output_path.suffix.lower() == ".json"
        else requested_output_path / OUTPUT_FILENAME
    )

    bids_description = load_json(bids_path)
    neurobaguel_description = convert_dataset_description(
        bids_description,
        args.access_type,
        args.repository_url,
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(neurobaguel_description, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print(f"Wrote Neurobaguel dataset description to {output_path}")


if __name__ == "__main__":
    main()
