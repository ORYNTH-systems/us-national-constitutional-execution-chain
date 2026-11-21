import json
import unittest
from pathlib import Path

BASE = Path(__file__).resolve().parent
MODEL = json.loads((BASE / "TYPED_IDENTITY_RESOLUTION.json").read_text(encoding="utf-8"))

class ResolutionContractTests(unittest.TestCase):
    def test_three_bindings(self):
        self.assertEqual(len(MODEL["reference_bindings"]), 3)

    def test_separation(self):
        self.assertTrue(MODEL["capacity_separate_from_identity"])
        self.assertTrue(MODEL["authority_separate_from_capacity"])

    def test_no_admission(self):
        self.assertEqual(MODEL["admission_state"]["legal_authority_admissions"], 0)
        self.assertEqual(MODEL["admission_state"]["effect_permissions"], 0)

    def test_no_certification(self):
        self.assertEqual(MODEL["admission_state"]["master_sections_certified"], 0)

if __name__ == "__main__":
    unittest.main()
