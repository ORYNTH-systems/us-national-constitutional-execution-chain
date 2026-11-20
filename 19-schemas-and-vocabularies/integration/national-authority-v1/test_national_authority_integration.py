import unittest
import json
import pathlib
import datetime

BASE = pathlib.Path(__file__).resolve().parent
SPEC = json.loads(
    (BASE / "NATIONAL_AUTHORITY_INTEGRATION.json").read_text(
        encoding="utf-8"
    )
)

def parse_time(value):
    if not value:
        return None
    try:
        dt = datetime.datetime.fromisoformat(
            value.replace("Z", "+00:00")
        )
        if dt.tzinfo is None:
            return None
        return dt
    except (ValueError, TypeError, AttributeError):
        return None

def evaluate(record, effect_time):
    """Synthetic conformance evaluator; not a legal authority engine."""
    at = parse_time(effect_time)
    start = parse_time(record.get("valid_from"))
    end_raw = record.get("valid_until")
    end = parse_time(end_raw)
    if at is None or start is None:
        return False
    if end_raw is None and not record.get("open_end_evidenced", False):
        return False
    if end_raw is not None and end is None:
        return False
    if at < start or (end is not None and at >= end):
        return False
    if record.get("revoked_at"):
        revoked = parse_time(record["revoked_at"])
        if revoked is None or at >= revoked:
            return False
    if not record.get("source_verified", False):
        return False
    if not record.get("scope_verified", False):
        return False
    if not record.get("installation_verified", False):
        return False
    if record.get("acting", False) and not record.get(
        "acting_basis_verified", False
    ):
        return False
    if record.get("external_actor", False) and not record.get(
        "government_retained_decision_verified", False
    ):
        return False
    if not record.get("fresh_effect_check", False):
        return False
    return True

def sample():
    return {
        "valid_from": "2026-01-01T00:00:00+00:00",
        "valid_until": "2027-01-01T00:00:00+00:00",
        "source_verified": True,
        "scope_verified": True,
        "installation_verified": True,
        "fresh_effect_check": True
    }

class NationalAuthorityIntegrationTests(unittest.TestCase):
    def test_contract_count(self):
        self.assertEqual(len(SPEC["source_contracts"]), 13)

    def test_relationship_count(self):
        self.assertEqual(len(SPEC["relationship_candidates"]), 12)

    def test_rule_count(self):
        self.assertEqual(len(SPEC["temporal_rules"]), 10)

    def test_office_person_separation(self):
        self.assertTrue(SPEC["identity_boundaries"]["office_not_person"])

    def test_contract_no_automatic_authority(self):
        self.assertTrue(
            SPEC["identity_boundaries"]["contract_not_governmental_authority"]
        )

    def test_valid_synthetic_case(self):
        self.assertTrue(evaluate(
            sample(), "2026-06-01T00:00:00+00:00"
        ))

    def test_before_validity(self):
        self.assertFalse(evaluate(
            sample(), "2025-12-31T23:59:59+00:00"
        ))

    def test_at_expiration(self):
        self.assertFalse(evaluate(
            sample(), "2027-01-01T00:00:00+00:00"
        ))

    def test_revocation(self):
        r = sample()
        r["revoked_at"] = "2026-05-01T00:00:00+00:00"
        self.assertFalse(evaluate(
            r, "2026-06-01T00:00:00+00:00"
        ))

    def test_missing_installation(self):
        r = sample()
        r["installation_verified"] = False
        self.assertFalse(evaluate(
            r, "2026-06-01T00:00:00+00:00"
        ))

    def test_acting_requires_basis(self):
        r = sample()
        r["acting"] = True
        self.assertFalse(evaluate(
            r, "2026-06-01T00:00:00+00:00"
        ))

    def test_external_requires_government_boundary(self):
        r = sample()
        r["external_actor"] = True
        self.assertFalse(evaluate(
            r, "2026-06-01T00:00:00+00:00"
        ))

    def test_stale_authorization(self):
        r = sample()
        r["fresh_effect_check"] = False
        self.assertFalse(evaluate(
            r, "2026-06-01T00:00:00+00:00"
        ))

    def test_unknown_end(self):
        r = sample()
        r["valid_until"] = None
        self.assertFalse(evaluate(
            r, "2026-06-01T00:00:00+00:00"
        ))

    def test_unknown_effect_time(self):
        self.assertFalse(evaluate(sample(), "unknown"))

    def test_evidence_not_self_certifying(self):
        self.assertTrue(
            SPEC["identity_boundaries"]["evidence_not_self_certifying"]
        )
        r = sample()
        r["source_verified"] = False
        self.assertFalse(evaluate(
            r, "2026-06-01T00:00:00+00:00"
        ))

    def test_no_legal_certification(self):
        c = SPEC["certification"]
        self.assertFalse(c["legal_authority_admitted"])
        self.assertFalse(c["effect_permission"])
        self.assertFalse(c["schema_adopted"])
        self.assertEqual(c["master_sections_certified"], 0)

if __name__ == "__main__":
    unittest.main(verbosity=2)
