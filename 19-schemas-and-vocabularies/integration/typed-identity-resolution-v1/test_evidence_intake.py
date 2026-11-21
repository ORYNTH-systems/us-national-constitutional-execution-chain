import copy
import hashlib
import unittest
from evidence_intake import inspect_intake


BYTES = b"SYNTHETIC OFFICIAL-RECORD TEST FIXTURE"

RECORD = {
    "record_id": "INTAKE-SYNTH-001",
    "source_locator": "https://example.invalid/synthetic",
    "acquisition_method": "OFFICIAL_HTTPS_RETRIEVAL",
    "source_class": "STATUTE",
    "acquired_at": "2026-06-01T00:00:00+00:00",
    "sha256": hashlib.sha256(BYTES).hexdigest(),
    "acquiring_actor": "TEST_HARNESS",
    "custody_reference": "SYNTHETIC-CUSTODY-001"
}

NOW = "2026-06-02T00:00:00+00:00"


def check(record=None, source_bytes=BYTES, now=NOW):
    return inspect_intake(
        copy.deepcopy(RECORD if record is None else record),
        source_bytes,
        now
    )


class EvidenceIntakeTests(unittest.TestCase):
    def test_integrity_does_not_admit_authority(self):
        result = check()
        self.assertEqual(result["intake_status"], "INTEGRITY_CHECKED")
        self.assertFalse(result["source_authenticated"])
        self.assertFalse(result["legal_authority_admitted"])
        self.assertFalse(result["effect_permission"])

    def test_missing_bytes(self):
        self.assertEqual(
            check(source_bytes=b"")["reason"], "MISSING_SOURCE_BYTES"
        )

    def test_modified_bytes(self):
        self.assertEqual(
            check(source_bytes=b"MODIFIED")["reason"],
            "SOURCE_BYTES_DIGEST_MISMATCH"
        )

    def test_missing_locator(self):
        item = dict(RECORD, source_locator="")
        self.assertEqual(
            check(item)["reason"], "MISSING_FIELD:source_locator"
        )

    def test_unsupported_method(self):
        item = dict(RECORD, acquisition_method="SELF_ASSERTION")
        self.assertEqual(
            check(item)["reason"], "UNSUPPORTED_ACQUISITION_METHOD"
        )

    def test_unsupported_class(self):
        item = dict(RECORD, source_class="UNKNOWN")
        self.assertEqual(
            check(item)["reason"], "UNSUPPORTED_SOURCE_CLASS"
        )

    def test_future_acquisition(self):
        item = dict(RECORD, acquired_at="2026-06-03T00:00:00+00:00")
        self.assertEqual(
            check(item)["reason"], "ACQUISITION_AFTER_DECISION"
        )

    def test_naive_acquisition_time(self):
        item = dict(RECORD, acquired_at="2026-06-01T00:00:00")
        self.assertEqual(
            check(item)["reason"], "INVALID_ACQUISITION_TIME"
        )

    def test_missing_custody(self):
        item = dict(RECORD, custody_reference="")
        self.assertEqual(
            check(item)["reason"], "MISSING_FIELD:custody_reference"
        )

    def test_self_certification(self):
        item = dict(RECORD, self_certified_authenticity=True)
        self.assertEqual(
            check(item)["reason"], "SELF_CERTIFICATION_NOT_ACCEPTED"
        )

    def test_invalid_record(self):
        self.assertEqual(
            inspect_intake(None, BYTES, NOW)["reason"],
            "INVALID_ACQUISITION_RECORD"
        )

    def test_missing_acquirer(self):
        item = dict(RECORD, acquiring_actor="")
        self.assertEqual(
            check(item)["reason"], "MISSING_FIELD:acquiring_actor"
        )


if __name__ == "__main__":
    unittest.main()
