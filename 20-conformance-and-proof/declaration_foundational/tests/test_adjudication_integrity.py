import csv
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / "00-constitutional-source/declaration-of-independence"


def load(name):
    with (BASE / name).open(newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def validate_record(row, proposal, passage):
    if row["constitutional_reference"] != proposal["proposed_constitutional_provision"]:
        raise ValueError("Constitutional reference mismatch")

    if row["proposed_relationship_class"] != proposal["proposed_relationship_class"]:
        raise ValueError("Proposed classification mismatch")

    if row["constitutional_source_span"] != passage["source_span"]:
        raise ValueError("Constitutional source span mismatch")

    if row["constitutional_source_sha256"] != passage["extracted_html_sha256"]:
        raise ValueError("Constitutional passage hash mismatch")

    if row["source_verification"] != passage["extraction_status"]:
        raise ValueError("Source verification status mismatch")

    if row["legal_effect"] != "NONE_INFERRED":
        raise ValueError("Unauthorized legal effect")

    if row["disposition"] != "PENDING":
        raise ValueError("Premature disposition")

    if row["review_status"] != "NOT_REVIEWED":
        raise ValueError("Premature review status")

    if row["adjudicated_relationship_class"]:
        raise ValueError("Premature adjudicated classification")

    for field in (
        "textual_correspondence",
        "structural_correspondence",
        "historical_support",
        "chronology_assessment",
    ):
        if row[field] != "NOT_ASSESSED":
            raise ValueError(f"Premature assessment: {field}")

    for field in (
        "scope_limitations",
        "evidence_rationale",
        "independent_historical_sources",
    ):
        if row[field]:
            raise ValueError(f"Unsupported assessment: {field}")


class AdjudicationIntegrityTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.proposals = load("DECLARATION_RELATIONSHIP_PROPOSALS.csv")
        cls.passages = load("CONSTITUTIONAL_PROVISION_PASSAGES.csv")
        cls.records = load("DECLARATION_RELATIONSHIP_ADJUDICATION.csv")

        cls.proposal_map = {
            p["foundational_id"]: p for p in cls.proposals
        }

        cls.passage_map = {
            p["constitutional_reference"]: p for p in cls.passages
        }

    def test_complete_proposal_coverage(self):
        self.assertEqual(len(self.proposals), 27)
        self.assertEqual(len(self.records), 27)
        self.assertEqual(len(self.proposal_map), 27)
        self.assertEqual(len(self.passage_map), 17)

        identifiers = [r["foundational_id"] for r in self.records]

        self.assertEqual(len(set(identifiers)), 27)
        self.assertEqual(set(identifiers), set(self.proposal_map))

    def test_all_records_match_verified_baseline(self):
        for row in self.records:
            with self.subTest(foundational_id=row["foundational_id"]):
                proposal = self.proposal_map[row["foundational_id"]]
                passage = self.passage_map[row["constitutional_reference"]]
                validate_record(row, proposal, passage)

    def test_unauthorized_legal_effect_rejected(self):
        row = dict(self.records[0])
        row["legal_effect"] = "BINDING"

        proposal = self.proposal_map[row["foundational_id"]]
        passage = self.passage_map[row["constitutional_reference"]]

        with self.assertRaises(ValueError):
            validate_record(row, proposal, passage)

    def test_premature_disposition_rejected(self):
        row = dict(self.records[0])
        row["disposition"] = "RETAIN"

        proposal = self.proposal_map[row["foundational_id"]]
        passage = self.passage_map[row["constitutional_reference"]]

        with self.assertRaises(ValueError):
            validate_record(row, proposal, passage)


if __name__ == "__main__":
    unittest.main()
