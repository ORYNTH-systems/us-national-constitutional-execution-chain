import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
GATE = ROOT / "20-conformance-and-proof/declaration_foundational/adjudication_gate.py"

spec = importlib.util.spec_from_file_location("adjudication_gate", GATE)
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)


def baseline():
    return {
        "source_verification": "EXTRACTED_PENDING_VERIFICATION",
        "relationship_assessment": "NOT_ASSESSED",
        "disposition": "PENDING",
        "evidence_rationale": "",
        "legal_effect": "NONE_INFERRED",
        "authority_source": "",
        "authority_verification": "",
    }


class AdjudicationGateTests(unittest.TestCase):

    def test_pending_record_allowed(self):
        self.assertTrue(gate.validate(baseline()))

    def test_premature_disposition_rejected(self):
        record = baseline()
        record.update(
            disposition="RETAIN",
            relationship_assessment="SUPPORTED",
            evidence_rationale="Provisional comparison",
        )
        with self.assertRaises(ValueError):
            gate.validate(record)

    def test_supported_transition_contract(self):
        record = baseline()
        record.update(
            source_verification="VERIFIED",
            relationship_assessment="SUPPORTED",
            disposition="RETAIN",
            evidence_rationale="Documented comparison",
        )
        self.assertTrue(gate.validate(record))

    def test_rejection_transition_contract(self):
        record = baseline()
        record.update(
            source_verification="VERIFIED",
            relationship_assessment="UNSUPPORTED",
            disposition="REJECT",
            evidence_rationale="Insufficient correspondence",
        )
        self.assertTrue(gate.validate(record))

    def test_missing_rationale_rejected(self):
        record = baseline()
        record.update(
            source_verification="VERIFIED",
            relationship_assessment="SUPPORTED",
            disposition="NARROW",
        )
        with self.assertRaises(ValueError):
            gate.validate(record)

    def test_declaration_authority_rejected(self):
        record = baseline()
        record.update(
            source_verification="VERIFIED",
            relationship_assessment="SUPPORTED",
            disposition="RETAIN",
            evidence_rationale="Comparison",
            legal_effect="BINDING_AUTHORITY",
            authority_source="DECL-1776-NA",
            authority_verification="VERIFIED",
        )
        with self.assertRaises(ValueError):
            gate.validate(record)

    def test_external_authority_not_automatically_accepted(self):
        record = baseline()
        record.update(
            source_verification="VERIFIED",
            relationship_assessment="SUPPORTED",
            disposition="RETAIN",
            evidence_rationale="Comparison",
            legal_effect="BINDING_AUTHORITY",
            authority_source="US-CONST:ARTICLE-I-SECTION-7",
            authority_verification="VERIFIED",
        )
        with self.assertRaises(ValueError):
            gate.validate(record)


if __name__ == "__main__":
    unittest.main()
