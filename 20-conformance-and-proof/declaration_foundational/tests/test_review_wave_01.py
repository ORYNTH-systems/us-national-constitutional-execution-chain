import csv
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / "00-constitutional-source/declaration-of-independence"


def load(name):
    with (BASE / name).open(newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


EXPECTED = {
    "DECL-PR-001": "NARROW",
    "DECL-PR-003": "RETAIN",
    "DECL-GR-001": "RETAIN",
    "DECL-GR-002": "REJECT",
    "DECL-GR-003": "NARROW",
    "DECL-GR-004": "NARROW",
    "DECL-GR-005": "NARROW",
}


def validate_review(row, canonical):
    fid = row["foundational_id"]

    if fid not in EXPECTED:
        raise ValueError("Unexpected foundational identifier")

    if row["recommended_disposition"] != EXPECTED[fid]:
        raise ValueError("Unexpected recommended disposition")

    if row["constitutional_reference"] != canonical["constitutional_reference"]:
        raise ValueError("Constitutional reference mismatch")

    if row["existing_relationship_class"] != canonical["proposed_relationship_class"]:
        raise ValueError("Relationship classification mismatch")

    if row["source_span"] != canonical["constitutional_source_span"]:
        raise ValueError("Source span mismatch")

    if row["source_sha256"] != canonical["constitutional_source_sha256"]:
        raise ValueError("Source digest mismatch")

    if not row["review_rationale"].strip():
        raise ValueError("Missing review rationale")

    if row["historical_causation"] != "NOT_ESTABLISHED":
        raise ValueError("Unsupported historical causation")

    if row["legal_effect"] != "NONE_INFERRED":
        raise ValueError("Unauthorized legal effect")

    if row["review_state"] != "ANALYTICAL_RECOMMENDATION":
        raise ValueError("Premature approval")

    if canonical["disposition"] != "PENDING":
        raise ValueError("Canonical disposition changed")

    if canonical["review_status"] != "NOT_REVIEWED":
        raise ValueError("Canonical review status changed")


class ReviewWave01Tests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.reviews = load("DECLARATION_RELATIONSHIP_REVIEW_WAVE_01.csv")
        cls.canonical = {
            row["foundational_id"]: row
            for row in load("DECLARATION_RELATIONSHIP_ADJUDICATION.csv")
        }

    def test_complete_review_wave(self):
        self.assertEqual(len(self.reviews), 7)

        identifiers = [r["foundational_id"] for r in self.reviews]

        self.assertEqual(len(set(identifiers)), 7)
        self.assertEqual(set(identifiers), set(EXPECTED))

    def test_all_recommendations_preserve_boundaries(self):
        for row in self.reviews:
            with self.subTest(foundational_id=row["foundational_id"]):
                validate_review(
                    row,
                    self.canonical[row["foundational_id"]],
                )

    def test_unauthorized_authority_rejected(self):
        row = dict(self.reviews[0])
        row["legal_effect"] = "BINDING"

        with self.assertRaises(ValueError):
            validate_review(
                row,
                self.canonical[row["foundational_id"]],
            )

    def test_premature_approval_rejected(self):
        row = dict(self.reviews[0])
        row["review_state"] = "APPROVED"

        with self.assertRaises(ValueError):
            validate_review(
                row,
                self.canonical[row["foundational_id"]],
            )

    def test_source_substitution_rejected(self):
        row = dict(self.reviews[0])
        row["source_sha256"] = "INVALID"

        with self.assertRaises(ValueError):
            validate_review(
                row,
                self.canonical[row["foundational_id"]],
            )


if __name__ == "__main__":
    unittest.main()
