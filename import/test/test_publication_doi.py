#!/usr/bin/env python3

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from export_xlsx import normalize_publication_doi


class TestNormalizePublicationDoi(unittest.TestCase):
    def test_adds_prefix_to_bare_doi(self):
        self.assertEqual(
            normalize_publication_doi("10.1002/mds.28216"),
            "https://doi.org/10.1002/mds.28216",
        )

    def test_preserves_canonical_url(self):
        self.assertEqual(
            normalize_publication_doi("https://doi.org/10.1002/mds.28216"),
            "https://doi.org/10.1002/mds.28216",
        )

    def test_repairs_common_spreadsheet_prefixes(self):
        cases = {
            "https:/doi.org/10.31234/osf.io/vzh4g": "https://doi.org/10.31234/osf.io/vzh4g",
            "http:/dx.doi.org/10.1016/example": "https://doi.org/10.1016/example",
            "doi: 10.1093/brain/aww043": "https://doi.org/10.1093/brain/aww043",
        }
        for value, expected in cases.items():
            with self.subTest(value=value):
                self.assertEqual(normalize_publication_doi(value), expected)

    def test_leaves_missing_doi_sentinels_unchanged(self):
        self.assertEqual(normalize_publication_doi("none"), "none")
        self.assertEqual(normalize_publication_doi(""), "")


if __name__ == "__main__":
    unittest.main()
