import unittest
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent
SPEC = json.loads((BASE / "NATIONAL_AUTHORITY_INTEGRATION.json").read_text(encoding="utf-8"))
MAPPINGS = SPEC["relationship_mappings_v2"]

def resolve(mapping, source, targets):
    if mapping["target_type_status"] == "UNRESOLVED_SEMANTIC_TARGET":
        return False
    value = source.get(mapping["reference_field"])
    values = value if isinstance(value, list) else [value]
    if not values or any(not isinstance(x, str) or not x for x in values):
        return False
    for value in values:
        hits = [x for x in targets if x.get("record_id") == value]
        if len(hits) != 1:
            return False
        if hits[0].get("contract_type") != mapping["candidate_target_contract"]:
            return False
    return True

class TypedRelationshipTests(unittest.TestCase):
    def test_mapping_count(self):
        self.assertEqual(len(MAPPINGS), 12)

    def test_unresolved_semantic_targets(self):
        self.assertEqual(sum(
            x["target_type_status"] == "UNRESOLVED_SEMANTIC_TARGET"
            for x in MAPPINGS
        ), 2)

    def test_wrong_type_rejected(self):
        m = next(x for x in MAPPINGS if x["reference_field"] == "office_role_ref")
        self.assertFalse(resolve(
            m, {"office_role_ref": "X"},
            [{"record_id": "X", "contract_type": "EVIDENCE"}]
        ))

    def test_missing_target_rejected(self):
        m = next(x for x in MAPPINGS if x["reference_field"] == "office_role_ref")
        self.assertFalse(resolve(m, {"office_role_ref": "X"}, []))

    def test_valid_synthetic_target(self):
        m = next(x for x in MAPPINGS if x["reference_field"] == "office_role_ref")
        self.assertTrue(resolve(
            m, {"office_role_ref": "X"},
            [{"record_id": "X", "contract_type": "OFFICE"}]
        ))

    def test_duplicate_target_rejected(self):
        m = next(x for x in MAPPINGS if x["reference_field"] == "office_role_ref")
        self.assertFalse(resolve(
            m, {"office_role_ref": "X"},
            [
                {"record_id": "X", "contract_type": "OFFICE"},
                {"record_id": "X", "contract_type": "OFFICE"}
            ]
        ))

    def test_no_admission(self):
        self.assertFalse(SPEC["certification"]["legal_authority_admitted"])
        self.assertFalse(SPEC["certification"]["effect_permission"])

if __name__ == "__main__":
    unittest.main()
