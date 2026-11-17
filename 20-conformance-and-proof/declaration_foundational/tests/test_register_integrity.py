"""Source-anchored Declaration register conformance tests."""

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
SOURCE = EVIDENCE / "national-archives-declaration-transcript.html"


def read_csv(name):
    with (BASE / name).open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def source_lines():
    return SOURCE.read_text(encoding="utf-8").splitlines()


def extract_line(lines, span):
    match = re.fullmatch(r"HTML:L([1-9][0-9]*)", span)
    if not match:
        raise ValueError("Invalid source span")

    index = int(match.group(1)) - 1

    if index >= len(lines):
        raise ValueError("Source span out of bounds")

    raw = lines[index].strip()

    if not re.fullmatch(r"<p>.*</p>", raw):
        raise ValueError("Source span is not a paragraph")

    return html.unescape(re.sub(r"<[^>]+>", "", raw)).strip()


class RegisterIntegrityTests(unittest.TestCase):

    def test_preserved_source_hash(self):
        metadata = json.loads(
            (EVIDENCE / "acquisition-metadata.json").read_text(
                encoding="utf-8-sig"
            )
        )

        actual = hashlib.sha256(SOURCE.read_bytes()).hexdigest()

        self.assertEqual(actual.lower(), metadata["SHA256"].lower())

        sources = read_csv("DECLARATION_SOURCE_REGISTER.csv")

        self.assertEqual(len(sources), 1)
        self.assertEqual(sources[0]["source_id"], "DECL-1776-NA")
        self.assertEqual(sources[0]["sha256"].lower(), actual.lower())
        self.assertEqual(sources[0]["acquisition_status"], "ACQUIRED")
        self.assertEqual(sources[0]["verification_status"], "HASH_VERIFIED")
        self.assertEqual(
            sources[0]["representation_path"],
            metadata["File"],
        )
        self.assertEqual(
            sources[0]["retrieved_at_utc"],
            metadata["RetrievedUTC"],
        )

    def test_grievances_match_source(self):
        records = read_csv("DECLARATION_GRIEVANCE_REGISTER.csv")
        lines = source_lines()

        self.assertEqual(len(records), 27)

        expected_spans = [
            f"HTML:L{line}" for line in range(380, 433, 2)
        ]

        self.assertEqual(
            [r["source_span"] for r in records],
            expected_spans,
        )

        for index, record in enumerate(records, 1):
            with self.subTest(grievance=index):
                self.assertEqual(
                    record["grievance_id"],
                    f"DECL-GR-{index:03d}",
                )
                self.assertEqual(record["source_id"], "DECL-1776-NA")
                self.assertEqual(
                    record["exact_quote"],
                    extract_line(lines, record["source_span"]),
                )
                self.assertEqual(
                    record["review_status"],
                    "EXTRACTED_PENDING_REVIEW",
                )

    def test_principles_match_source(self):
        records = read_csv("DECLARATION_PRINCIPLE_REGISTER.csv")
        lines = source_lines()

        self.assertEqual(len(records), 3)

        paragraph = extract_line(lines, "HTML:L377")

        for index, record in enumerate(records, 1):
            with self.subTest(principle=index):
                self.assertEqual(
                    record["principle_id"],
                    f"DECL-PR-{index:03d}",
                )
                self.assertEqual(record["source_id"], "DECL-1776-NA")
                self.assertEqual(record["source_span"], "HTML:L377")
                self.assertIn(record["exact_quote"], paragraph)
                self.assertTrue(record["exact_quote"])
                self.assertEqual(
                    record["authority_class"],
                    "FOUNDATIONAL",
                )
                self.assertEqual(
                    record["review_status"],
                    "EXTRACTED_PENDING_REVIEW",
                )

    def test_crosswalk_has_no_inferred_legal_effect(self):
        records = read_csv(
            "DECLARATION_CONSTITUTION_CROSSWALK.csv"
        )

        principles = read_csv("DECLARATION_PRINCIPLE_REGISTER.csv")
        grievances = read_csv("DECLARATION_GRIEVANCE_REGISTER.csv")

        valid_ids = {
            r["principle_id"] for r in principles
        } | {
            r["grievance_id"] for r in grievances
        }

        self.assertEqual(len(records), 3)
        self.assertEqual(
            len({r["crosswalk_id"] for r in records}),
            len(records),
        )

        for record in records:
            with self.subTest(crosswalk=record["crosswalk_id"]):
                self.assertIn(
                    record["principle_or_grievance_id"],
                    valid_ids,
                )
                self.assertEqual(
                    record["legal_effect"],
                    "NONE_INFERRED",
                )
                self.assertEqual(
                    record["review_status"],
                    "SOURCE_ANCHORED_PENDING_REVIEW",
                )
                self.assertTrue(
                    record["independent_authority_source"]
                )
                self.assertTrue(record["constitutional_provision"])
                self.assertTrue(record["relationship"])


if __name__ == "__main__":
    unittest.main()
