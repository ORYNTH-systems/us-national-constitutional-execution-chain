"""Proposed evidence-intake boundary.

This module checks acquisition metadata and source-byte integrity.
It does not independently authenticate a source, interpret law,
admit governmental authority, or authorize an effect.
"""

import hashlib
from datetime import datetime, timezone


ALLOWED_METHODS = frozenset({
    "OFFICIAL_HTTPS_RETRIEVAL",
    "OFFICIAL_ARCHIVE_DOWNLOAD",
    "CERTIFIED_RECORD_DELIVERY",
    "DOCUMENTED_PHYSICAL_INSPECTION"
})

ALLOWED_CLASSES = frozenset({
    "CONSTITUTIONAL_TEXT",
    "STATUTE",
    "REGULATION",
    "COURT_RECORD",
    "OFFICIAL_APPOINTMENT_RECORD",
    "OFFICIAL_DELEGATION_RECORD",
    "OFFICIAL_REVOCATION_RECORD",
    "OTHER_OFFICIAL_RECORD"
})


def parse_time(value):
    if not isinstance(value, str):
        raise ValueError("INVALID_TIME")
    result = datetime.fromisoformat(value)
    if result.tzinfo is None or result.utcoffset() is None:
        raise ValueError("TIMEZONE_REQUIRED")
    return result


def inspect_intake(record, source_bytes, decision_time):
    def block(reason):
        return {
            "intake_status": "BLOCKED",
            "reason": reason,
            "source_authenticated": False,
            "legal_authority_admitted": False,
            "effect_permission": False
        }

    if not isinstance(record, dict):
        return block("INVALID_ACQUISITION_RECORD")

    if not isinstance(source_bytes, bytes) or not source_bytes:
        return block("MISSING_SOURCE_BYTES")

    required = (
        "record_id", "source_locator", "acquisition_method",
        "source_class", "acquired_at", "sha256",
        "acquiring_actor", "custody_reference"
    )

    for field in required:
        if not isinstance(record.get(field), str) or not record[field].strip():
            return block("MISSING_FIELD:" + field)

    if record["acquisition_method"] not in ALLOWED_METHODS:
        return block("UNSUPPORTED_ACQUISITION_METHOD")

    if record["source_class"] not in ALLOWED_CLASSES:
        return block("UNSUPPORTED_SOURCE_CLASS")

    try:
        acquired = parse_time(record["acquired_at"])
        decision = parse_time(decision_time)
    except (ValueError, TypeError):
        return block("INVALID_ACQUISITION_TIME")

    if acquired > decision:
        return block("ACQUISITION_AFTER_DECISION")

    computed = hashlib.sha256(source_bytes).hexdigest()

    if computed != record["sha256"]:
        return block("SOURCE_BYTES_DIGEST_MISMATCH")

    if record.get("self_certified_authenticity") is True:
        return block("SELF_CERTIFICATION_NOT_ACCEPTED")

    return {
        "intake_status": "INTEGRITY_CHECKED",
        "reason": "EXTERNAL_AUTHENTICATION_AND_LEGAL_REVIEW_PENDING",
        "source_sha256": computed,
        "source_authenticated": False,
        "legal_authority_admitted": False,
        "effect_permission": False
    }
