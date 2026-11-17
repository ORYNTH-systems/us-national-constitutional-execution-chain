import csv
import importlib.util
import shutil
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / "00-constitutional-source/declaration-of-independence"
SCRIPT = ROOT / "20-conformance-and-proof/declaration_foundational/verified_adjudication.py"

spec = importlib.util.spec_from_file_location("verified_adjudication", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def pending():
    return {
        "source_verification": "VERIFIED",
        "relationship_assessment": "NOT_ASSESSED",
        "disposition": "PENDING",
        "evidence_rationale": "",
        "legal_effect": "NONE_INFERRED",
        "authority_source": "",
        "authority_verification": "",
    }


class VerifiedAdjudicationTests(unittest.TestCase):

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)

        self.base = Path(self.temp.name) / "baseline"
        self.base.mkdir()

        shutil.copytree(BASE / "evidence", self.base / "evidence")

        for name in (
            "CONSTITUTIONAL_PROVISION_SOURCE_INDEX.csv",
            "CONSTITUTIONAL_PROVISION_PASSAGES.csv",
            "DECLARATION_RELATIONSHIP_ADJUDICATION.csv",
            "DECLARATION_RELATIONSHIP_PROPOSALS.csv",
        ):
            shutil.copy2(BASE / name, self.base / name)

    def mutate(self, filename, field, value):
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

    def test_baseline_verified(self):
        result = module.verify_adjudication_baseline(self.base)
        self.assertEqual(result["verified_passages"], 17)
        self.assertEqual(result["pending_adjudications"], 27)

    def test_pending_transition_accepted(self):
        self.assertTrue(
            module.validate_proposed_transition(
                "DECL-PR-001", pending(), self.base
            )
        )

    def test_premature_approval_rejected(self):
        record = pending()
        record.update(
            disposition="RETAIN",
            relationship_assessment="SUPPORTED",
            evidence_rationale="Unapproved recommendation",
        )

        with self.assertRaises(ValueError):
            module.validate_proposed_transition(
                "DECL-PR-001", record, self.base
            )

    def test_binding_authority_rejected(self):
        record = pending()
        record["legal_effect"] = "BINDING_AUTHORITY"

        with self.assertRaises(ValueError):
            module.validate_proposed_transition(
                "DECL-PR-001", record, self.base
            )

    def test_unknown_identifier_rejected(self):
        with self.assertRaises(ValueError):
            module.validate_proposed_transition(
                "DECL-UNKNOWN", pending(), self.base
            )

    def test_canonical_passage_digest_tampering_rejected(self):
        self.mutate(
            "DECLARATION_RELATIONSHIP_ADJUDICATION.csv",
            "constitutional_source_sha256",
            "0" * 64,
        )

        with self.assertRaises(ValueError):
            module.verify_adjudication_baseline(self.base)

    def test_canonical_approval_tampering_rejected(self):
        self.mutate(
            "DECLARATION_RELATIONSHIP_ADJUDICATION.csv",
            "disposition",
            "RETAIN",
        )

        with self.assertRaises(ValueError):
            module.verify_adjudication_baseline(self.base)

    def test_proposal_reference_tampering_rejected(self):
        self.mutate(
            "DECLARATION_RELATIONSHIP_PROPOSALS.csv",
            "proposed_constitutional_provision",
            "US-CONST:INVALID",
        )

        with self.assertRaises(ValueError):
            module.verify_adjudication_baseline(self.base)


if __name__ == "__main__":
    unittest.main()
