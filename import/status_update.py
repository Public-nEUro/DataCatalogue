#!/usr/bin/env python3
"""Update the user-facing availability status of a catalogue dataset record."""

import argparse
import json
import os
import re
import tempfile
from pathlib import Path
from urllib.parse import urlparse


STATUSES = ("active", "archived", "retired", "withdrawn", "superseded")
STATUS_ALIASES = {"superseeded": "superseded"}


def _read_records(path):
    """Return (records, is_jsonl, original_lines) for a JSON or JSONL file."""
    path = Path(path)
    if path.suffix.lower() == ".jsonl":
        lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
        datasets = []
        for index, line in enumerate(lines):
            if not line.strip():
                continue
            if not datasets or ('"type"' in line and '"dataset"' in line):
                record = json.loads(line)
                if record.get("type") == "dataset":
                    datasets.append((index, record))
                    if len(datasets) > 1:
                        break
        return datasets, True, lines

    with path.open("r", encoding="utf-8") as stream:
        return [(0, json.load(stream))], False, None


def _write_records(path, records, is_jsonl, original_lines, changed_indices=None):
    """Atomically write updated JSON or JSONL records."""
    path = Path(path)
    if is_jsonl:
        changed_indices = set(changed_indices or ())
        for index, record in records:
            if index in changed_indices:
                original_lines[index] = json.dumps(record, ensure_ascii=False) + "\n"
        content = "".join(original_lines)
    else:
        content = json.dumps(records[0][1], indent=2, ensure_ascii=False) + "\n"

    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            stream.write(content)
        os.replace(temporary_name, path)
    except Exception:
        try:
            os.unlink(temporary_name)
        except FileNotFoundError:
            pass
        raise


def _dataset_records(records):
    datasets = [(index, record) for index, record in records if record.get("type") == "dataset"]
    if not datasets:
        raise ValueError("No record with type='dataset' was found")
    if len(datasets) > 1:
        raise ValueError("More than one dataset record was found; update one dataset file at a time")
    return datasets


def _normalise_status(status):
    status = STATUS_ALIASES.get(status.lower(), status.lower())
    if status not in STATUSES:
        raise ValueError(f"Status must be one of: {', '.join(STATUSES)}")
    return status


def _contact_fields(contact):
    if re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", contact):
        return "access_request_contact", {
            "givenName": "Data",
            "familyName": "Controller",
            "email": contact,
        }

    parsed = urlparse(contact)
    if parsed.scheme in {"http", "https"} and parsed.netloc:
        return "access_request_url", contact
    raise ValueError("Contact must be an email address or an http(s) URL")


def _append_description(record, status, detail):
    note = f"Status note ({status}): {detail.strip()}"
    description = record.get("description")
    if isinstance(description, list):
        if note not in description:
            description.append(note)
    elif isinstance(description, str) and description.strip():
        if note not in description:
            record["description"] = description.rstrip() + "\n\n" + note
    else:
        record["description"] = note


def ensure_default_status(path):
    """Set missing dataset status values to active; return whether the file changed."""
    records, is_jsonl, original_lines = _read_records(path)
    datasets = _dataset_records(records)
    changed = False
    for _, record in datasets:
        if not record.get("status"):
            record["status"] = "active"
            changed = True
    if changed:
        _write_records(
            path,
            records,
            is_jsonl,
            original_lines,
            changed_indices={index for index, _ in datasets},
        )
    return changed


def update_status(path, status, contact=None, reason=None, new=None):
    """Update one dataset record and return the updated record."""
    status = _normalise_status(status)

    if status in {"archived", "retired"} and not contact:
        raise ValueError(f"--contact is required for status '{status}'")
    if status == "withdrawn" and not reason:
        raise ValueError("--reason is required for status 'withdrawn'")
    if status == "superseded" and not new:
        raise ValueError("--new is required for status 'superseded'")
    if contact and status not in {"archived", "retired"}:
        raise ValueError("--contact is only valid for archived or retired datasets")
    if reason and status != "withdrawn":
        raise ValueError("--reason is only valid for withdrawn datasets")
    if new and status != "superseded":
        raise ValueError("--new is only valid for superseded datasets")

    records, is_jsonl, original_lines = _read_records(path)
    dataset_index, record = _dataset_records(records)[0]
    record["status"] = status

    # A transition replaces the previous alternative retrieval route. The
    # download URL is retained so a later reactivation does not lose it; the
    # catalogue renderer decides whether it is visible for the current status.
    record.pop("access_request_url", None)
    record.pop("access_request_contact", None)
    if contact:
        field, value = _contact_fields(contact)
        record[field] = value

    if reason:
        _append_description(record, status, reason)
    if new:
        _append_description(record, status, new)

    _write_records(
        path,
        records,
        is_jsonl,
        original_lines,
        changed_indices={dataset_index},
    )
    return record


def main():
    parser = argparse.ArgumentParser(
        description="Update a PublicnEUro dataset availability status"
    )
    parser.add_argument("json_file", help="Dataset .json or .jsonl file to update")
    parser.add_argument(
        "status",
        choices=STATUSES + tuple(STATUS_ALIASES),
        help="New dataset status (the common 'superseeded' spelling is accepted as an alias)",
    )
    parser.add_argument("--contact", help="Retrieval/controller email address or URL")
    parser.add_argument("--reason", help="Reason appended to description for withdrawn data")
    parser.add_argument("--new", help="Replacement information appended for superseded data")
    args = parser.parse_args()

    try:
        record = update_status(
            args.json_file,
            args.status,
            contact=args.contact,
            reason=args.reason,
            new=args.new,
        )
    except (OSError, ValueError, json.JSONDecodeError) as error:
        parser.error(str(error))

    print(
        f"Updated {record.get('dataset_id', args.json_file)} "
        f"({record.get('dataset_version', 'unknown version')}): {record['status']}"
    )


if __name__ == "__main__":
    main()
