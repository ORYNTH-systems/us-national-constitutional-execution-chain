import csv
import shutil
import tempfile
import unittest
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))

from verify_review_coverage import BASE, verify_review_coverage

FILES = [
    "DECLARATION_RELATIONSHIP_PROPOSALS.csv",
    "DECLARATION_RELATIONSHIP_ADJUDICATION.csv",
    "DECLARATION_RELATIONSHIP_REVIEW_WAVE_01.csv",
] + [
    f"DECLARATION_RELATIONSHIP_REVIEW_WAVE_02_GROUP_{g}.csv"
    for g in "ABCDE"
]


class ReviewCoverageTests(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)

        for filename in FILES:
            shutil.copy2(BASE / filename, self.base / filename)

    def change(self, filename, field, value):
        path = self.base / filename
        with path.open(newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            fields = reader.fieldnames
            rows = list(reader)

        rows[0][field] = value

        with path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)

    def verify(self):
        return verify_review_coverage(self.base, BASE)

    def test_complete_baseline(self):
        result = self.verify()
        self.assertEqual(result["total"], 27)
        self.assertEqual(sum(result["distribution"].values()), 27)

    def test_unauthorized_authority_rejected(self):
        self.change(
            FILES[3], "legal_effect", "BINDING_AUTHORITY"
        )
        with self.assertRaises(ValueError):
            self.verify()

    def test_premature_review_approval_rejected(self):
        self.change(
            FILES[3], "review_state", "APPROVED"
        )
        with self.assertRaises(ValueError):
            self.verify()

    def test_reference_substitution_rejected(self):
        self.change(
            FILES[3], "constitutional_reference", "US-CONST:INVALID"
        )
        with self.assertRaises(ValueError):
            self.verify()

    def test_unacknowledged_class_change_rejected(self):
        self.change(
            FILES[3], "recommended_relationship_class", "DIRECT_TEXTUAL"
        )
        with self.assertRaises(ValueError):
            self.verify()

    def test_historical_causation_promotion_rejected(self):
        self.change(
            FILES[3], "historical_causation", "ESTABLISHED"
        )
        with self.assertRaises(ValueError):
            self.verify()

    def test_canonical_promotion_rejected(self):
        self.change(
            FILES[1], "disposition", "RETAIN"
        )
        with self.assertRaises(ValueError):
            self.verify()

    def test_missing_group_rejected(self):
        path = self.base / FILES[3]
        path.unlink()
        with self.assertRaises(FileNotFoundError):
            self.verify()


if __name__ == "__main__":
    unittest.main()
