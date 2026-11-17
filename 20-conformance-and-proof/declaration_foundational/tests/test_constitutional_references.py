"""Verify independent constitutional evidence and crosswalk provenance."""

import csv
import hashlib
import html
import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / "00-constitutional-source" / "declaration-of-independence"
EVIDENCE = BASE / "evidence"

EXPECTED = {
    "DECL-CW-001": (
        "national-archives-constitution-transcript.html",
        373,
        "We the People",
        "US-CONST:PREAMBLE",
    ),
    "DECL-CW-002": (
        "national-archives-constitution-transcript.html",
        543,
        "during good Behaviour",
        "US-CONST:ARTICLE-III-SECTION-1",
    ),
    "DECL-CW-003": (
        "national-archives-bill-of-rights-transcript.html",
        447,
        "right of trial by jury",
        "US-CONST:AMENDMENT-VII",
    ),
}


class ConstitutionalReferenceTests(unittest.TestCase):

    def test_independent_source_hashes(self):
        metadata = json.loads(
            (EVIDENCE / "constitutional-reference-acquisitions.json")
            .read_text(encoding="utf-8-sig")
        )

        self.assertEqual(len(metadata), 2)

        expected_files = {
            "national-archives-constitution-transcript.html",
            "national-archives-bill-of-rights-transcript.html",
        }

        self.assertEqual(
            {item["file"] for item in metadata},
            expected_files,
        )

        for item in metadata:
            with self.subTest(file=item["file"]):
                path = EVIDENCE / item["file"]

                self.assertTrue(path.is_file())
                self.assertEqual(
                    hashlib.sha256(path.read_bytes()).hexdigest().lower(),
                    item["sha256"].lower(),
                )
                self.assertEqual(
                    item["acquisition_status"],
                    "ACQUIRED",
                )
                self.assertEqual(
                    item["verification_status"],
                    "HASH_RECORDED",
                )

    def test_crosswalk_source_spans(self):
        with (
            BASE / "DECLARATION_CONSTITUTION_CROSSWALK.csv"
        ).open(encoding="utf-8-sig", newline="") as f:
            records = list(csv.DictReader(f))

        self.assertEqual(
            {r["crosswalk_id"] for r in records},
            set(EXPECTED),
        )

        for record in records:
            with self.subTest(crosswalk=record["crosswalk_id"]):
                filename, line, phrase, provision = EXPECTED[
                    record["crosswalk_id"]
                ]

                self.assertEqual(
                    record["constitutional_provision"],
                    provision,
                )
                self.assertEqual(
                    record["independent_authority_source"],
                    f"{filename}#HTML:L{line}",
                )
                self.assertEqual(
                    record["legal_effect"],
                    "NONE_INFERRED",
                )
                self.assertEqual(
                    record["review_status"],
                    "SOURCE_ANCHORED_PENDING_REVIEW",
                )

                lines = (EVIDENCE / filename).read_text(
                    encoding="utf-8"
                ).splitlines()

                self.assertGreaterEqual(len(lines), line)

                passage = html.unescape(
                    re.sub(r"<[^>]+>", "", lines[line - 1])
                )

                self.assertIn(phrase, passage)


if __name__ == "__main__":
    unittest.main()
