#!/usr/bin/env python3

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from status_update import ensure_default_status, update_status


class TestStatusUpdate(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.path = Path(self.directory.name) / "dataset.json"
        self.record = {
            "type": "dataset",
            "dataset_id": "PN000001 Example",
            "dataset_version": "V1",
            "description": "Original description.",
            "download_url": "/manage/request-access/PN000001",
        }
        self.path.write_text(json.dumps(self.record), encoding="utf-8")

    def tearDown(self):
        self.directory.cleanup()

    def read(self):
        return json.loads(self.path.read_text(encoding="utf-8"))

    def test_default_status_is_active_and_does_not_overwrite(self):
        self.assertTrue(ensure_default_status(self.path))
        self.assertEqual(self.read()["status"], "active")
        self.assertFalse(ensure_default_status(self.path))

    def test_archived_email_contact(self):
        update_status(self.path, "archived", contact="archive@example.org")
        record = self.read()
        self.assertEqual(record["status"], "archived")
        self.assertEqual(record["access_request_contact"]["email"], "archive@example.org")
        self.assertIn("download_url", record)

    def test_retired_url_contact(self):
        update_status(self.path, "retired", contact="https://example.org/data-access")
        record = self.read()
        self.assertEqual(record["access_request_url"], "https://example.org/data-access")
        self.assertNotIn("access_request_contact", record)

    def test_withdrawn_appends_reason_and_removes_contact(self):
        self.record["access_request_url"] = "https://example.org/old"
        self.path.write_text(json.dumps(self.record), encoding="utf-8")
        update_status(self.path, "withdrawn", reason="Controller request")
        record = self.read()
        self.assertIn("Status note (withdrawn): Controller request", record["description"])
        self.assertNotIn("access_request_url", record)

    def test_superseeded_alias_appends_new_dataset(self):
        update_status(self.path, "superseeded", new="See DOI 10.1234/current")
        record = self.read()
        self.assertEqual(record["status"], "superseded")
        self.assertIn("Status note (superseded): See DOI 10.1234/current", record["description"])
        self.assertIn("download_url", record)

    def test_jsonl_updates_only_dataset_record(self):
        path = Path(self.directory.name) / "dataset.jsonl"
        file_record = {"type": "file", "path": "participants.tsv"}
        file_line = '{  "type": "file", "path": "participants.tsv"  }\n'
        path.write_text(
            json.dumps(self.record) + "\n" + file_line,
            encoding="utf-8",
        )
        update_status(path, "archived", contact="archive@example.org")
        updated_text = path.read_text(encoding="utf-8")
        lines = [json.loads(line) for line in updated_text.splitlines()]
        self.assertEqual(lines[0]["status"], "archived")
        self.assertEqual(lines[1], file_record)
        self.assertTrue(updated_text.endswith(file_line))

    def test_required_arguments(self):
        with self.assertRaisesRegex(ValueError, "--contact"):
            update_status(self.path, "archived")
        with self.assertRaisesRegex(ValueError, "--reason"):
            update_status(self.path, "withdrawn")
        with self.assertRaisesRegex(ValueError, "--new"):
            update_status(self.path, "superseded")


if __name__ == "__main__":
    unittest.main()
