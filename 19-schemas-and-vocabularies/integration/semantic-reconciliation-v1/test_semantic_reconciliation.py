import json
import pathlib
import unittest

ROOT = pathlib.Path(__file__).parent
DATA = json.loads(
    (ROOT / "SEMANTIC_RECONCILIATION.json").read_text(encoding="utf-8")
)

class SemanticReconciliationTests(unittest.TestCase):
    def test_proposal_not_adopted(self):
        self.assertEqual(DATA["status"], "PROPOSED_NOT_ADOPTED")

    def test_exact_references(self):
        self.assertEqual(
            {r["reference"] for r in DATA["reference_rules"]},
            {
                "JURISDICTION.actor_ref",
                "EXTERNAL_EXECUTION.public_principal_ref",
                "AUTHORITY_CHAIN.actor_ref"
            }
        )

    def test_no_semantic_admissions(self):
        self.assertTrue(all(
            r["semantic_target_admitted"] is False
            for r in DATA["reference_rules"]
        ))

    def test_no_authority_or_execution_admissions(self):
        self.assertEqual(DATA["legal_authority_admissions"], 0)
        self.assertEqual(DATA["execution_permissions_granted"], 0)
        self.assertEqual(DATA["master_sections_certified"], 0)

    def test_no_role_collapse(self):
        prohibited = set(DATA["prohibited_inferences"])
        self.assertIn("identity_implies_capacity", prohibited)
        self.assertIn("capacity_implies_authority", prohibited)
        self.assertIn("authority_chain_implies_public_principal", prohibited)

    def test_public_capacity_requirement(self):
        record = next(
            r for r in DATA["reference_rules"]
            if r["reference"] == "EXTERNAL_EXECUTION.public_principal_ref"
        )
        self.assertIn("public_capacity_evidence", record["requires"])

if __name__ == "__main__":
    unittest.main(verbosity=2)
