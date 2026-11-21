import copy
import unittest
from evidence_resolver import resolve, sha256


def fixture():
    record = {
        "reference_value": "ACTOR-SYNTH-001",
        "identity_category": "PUBLIC_BODY",
        "identity_record_id": "ID-SYNTH",
        "capacity_record_id": "CAP-SYNTH",
        "authority_record_id": "AUTH-SYNTH",
        "effective_from": "2026-01-01T00:00:00+00:00",
        "effective_until": "2027-01-01T00:00:00+00:00",
        "revocation_checked_at": "2026-06-01T00:00:00+00:00",
        "revoked": False,
        "evidence": []
    }
    for kind, subject in (
        ("IDENTITY", "ID-SYNTH"),
        ("CAPACITY", "CAP-SYNTH"),
        ("AUTHORITY", "AUTH-SYNTH"),
        ("REVOCATION_STATUS", "AUTH-SYNTH")
    ):
        payload = {"subject_record_id": subject}
        record["evidence"].append({
            "kind": kind,
            "source_locator": "synthetic://test/" + kind,
            "payload": payload,
            "sha256": sha256(payload)
        })
    return record


def check(records, category="PUBLIC_BODY",
          moment="2026-06-01T00:00:00+00:00"):
    return resolve(
        "ACTOR-SYNTH-001", category, moment, records
    )


class EvidenceResolverTests(unittest.TestCase):
    def test_consistent_is_not_authorized(self):
        result = check([fixture()])
        self.assertEqual(
            result["structural_status"],
            "STRUCTURALLY_CONSISTENT"
        )
        self.assertFalse(result["authority_admitted"])
        self.assertFalse(result["effect_permission"])

    def test_missing_record(self):
        self.assertEqual(
            check([])["reason"], "REFERENCE_NOT_UNIQUE"
        )

    def test_duplicate_record(self):
        record = fixture()
        self.assertEqual(
            check([record, copy.deepcopy(record)])["reason"],
            "REFERENCE_NOT_UNIQUE"
        )

    def test_wrong_category(self):
        self.assertEqual(
            check([fixture()], "PERSON")["reason"],
            "IDENTITY_CATEGORY_MISMATCH"
        )

    def test_missing_authority_link(self):
        record = fixture()
        record["authority_record_id"] = ""
        self.assertEqual(
            check([record])["reason"], "MISSING_TYPED_LINK"
        )

    def test_missing_evidence(self):
        record = fixture()
        record["evidence"] = []
        self.assertEqual(
            check([record])["reason"], "MISSING_EVIDENCE"
        )

    def test_digest_mismatch(self):
        record = fixture()
        record["evidence"][0]["payload"]["tampered"] = True
        self.assertEqual(
            check([record])["reason"], "EVIDENCE_DIGEST_MISMATCH"
        )

    def test_wrong_subject(self):
        record = fixture()
        item = record["evidence"][0]
        item["payload"]["subject_record_id"] = "OTHER"
        item["sha256"] = sha256(item["payload"])
        self.assertEqual(
            check([record])["reason"], "EVIDENCE_SUBJECT_MISMATCH"
        )

    def test_expired(self):
        self.assertEqual(
            check(
                [fixture()], moment="2027-01-01T00:00:00+00:00"
            )["reason"], "OUTSIDE_VALIDITY_WINDOW"
        )

    def test_revoked(self):
        record = fixture()
        record["revoked"] = True
        self.assertEqual(
            check([record])["reason"], "REVOKED_OR_UNKNOWN"
        )

    def test_unknown_revocation(self):
        record = fixture()
        del record["revoked"]
        self.assertEqual(
            check([record])["reason"], "REVOKED_OR_UNKNOWN"
        )

    def test_future_revocation_check(self):
        record = fixture()
        record["revocation_checked_at"] = (
            "2026-07-01T00:00:00+00:00"
        )
        self.assertEqual(
            check([record])["reason"], "FUTURE_REVOCATION_CHECK"
        )

    def test_missing_evidence_kind(self):
        record = fixture()
        record["evidence"].pop()
        self.assertEqual(
            check([record])["reason"], "INCOMPLETE_EVIDENCE_SET"
        )

    def test_duplicate_evidence_kind(self):
        record = fixture()
        record["evidence"].append(
            copy.deepcopy(record["evidence"][0])
        )
        self.assertEqual(
            check([record])["reason"], "DUPLICATE_EVIDENCE_KIND"
        )


if __name__ == "__main__":
    unittest.main()
