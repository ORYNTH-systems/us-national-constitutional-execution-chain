"""Proposed structural evidence resolver.

This module does not certify legal authority or permit execution.
Evidence payloads must be independently acquired and authenticated
before any consequential governmental use.
"""

import hashlib
import json
from datetime import datetime


def canonical_bytes(value):
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"),
        ensure_ascii=False
    ).encode("utf-8")


def sha256(value):
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def timestamp(value):
    if not isinstance(value, str):
        raise ValueError("INVALID_TIMESTAMP")
    result = datetime.fromisoformat(value)
    if result.tzinfo is None or result.utcoffset() is None:
        raise ValueError("TIMEZONE_REQUIRED")
    return result


def resolve(reference, identity_category, moment, records):
    """Return structural status, never effect permission."""
    denial = {
        "structural_status": "BLOCKED",
        "authority_admitted": False,
        "effect_permission": False,
    }

    def block(reason):
        return dict(denial, reason=reason)

    if not isinstance(reference, str) or not reference.strip():
        return block("INVALID_REFERENCE")

    if not isinstance(records, list):
        return block("INVALID_RECORD_SET")

    try:
        now = timestamp(moment)
    except (ValueError, TypeError):
        return block("INVALID_DECISION_TIME")

    matches = [
        r for r in records
        if isinstance(r, dict)
        and r.get("reference_value") == reference
    ]

    if len(matches) != 1:
        return block("REFERENCE_NOT_UNIQUE")

    record = matches[0]

    if record.get("identity_category") != identity_category:
        return block("IDENTITY_CATEGORY_MISMATCH")

    if identity_category not in {
        "PERSON", "OFFICE_OR_ROLE", "PUBLIC_BODY",
        "PUBLIC_INSTITUTION", "PRIVATE_LEGAL_ENTITY",
        "AUTOMATED_SYSTEM"
    }:
        return block("UNSUPPORTED_IDENTITY_CATEGORY")

    for field in (
        "identity_record_id", "capacity_record_id",
        "authority_record_id"
    ):
        if not isinstance(record.get(field), str) or not record[field]:
            return block("MISSING_TYPED_LINK")

    evidence = record.get("evidence")

    if not isinstance(evidence, list) or not evidence:
        return block("MISSING_EVIDENCE")

    kinds = set()

    for item in evidence:
        if not isinstance(item, dict):
            return block("MALFORMED_EVIDENCE")

        kind = item.get("kind")
        locator = item.get("source_locator")
        payload = item.get("payload")
        claimed_hash = item.get("sha256")

        if kind not in {
            "IDENTITY", "CAPACITY", "AUTHORITY",
            "REVOCATION_STATUS"
        }:
            return block("UNKNOWN_EVIDENCE_KIND")

        if kind in kinds:
            return block("DUPLICATE_EVIDENCE_KIND")

        kinds.add(kind)

        if not isinstance(locator, str) or not locator.strip():
            return block("MISSING_SOURCE_LOCATOR")

        if not isinstance(payload, dict):
            return block("INVALID_EVIDENCE_PAYLOAD")

        if not isinstance(claimed_hash, str) or claimed_hash != sha256(payload):
            return block("EVIDENCE_DIGEST_MISMATCH")

        expected_link = {
            "IDENTITY": record["identity_record_id"],
            "CAPACITY": record["capacity_record_id"],
            "AUTHORITY": record["authority_record_id"],
            "REVOCATION_STATUS": record["authority_record_id"]
        }[kind]

        if payload.get("subject_record_id") != expected_link:
            return block("EVIDENCE_SUBJECT_MISMATCH")

    if kinds != {
        "IDENTITY", "CAPACITY", "AUTHORITY",
        "REVOCATION_STATUS"
    }:
        return block("INCOMPLETE_EVIDENCE_SET")

    try:
        start = timestamp(record.get("effective_from"))
        end = timestamp(record.get("effective_until"))
        checked = timestamp(record.get("revocation_checked_at"))
    except (ValueError, TypeError):
        return block("INVALID_TEMPORAL_EVIDENCE")

    if not start <= now < end:
        return block("OUTSIDE_VALIDITY_WINDOW")

    if checked > now:
        return block("FUTURE_REVOCATION_CHECK")

    if record.get("revoked") is not False:
        return block("REVOKED_OR_UNKNOWN")

    # Hash matching and structural consistency are not independent
    # source authentication or adjudication of legal authority.
    return {
        "structural_status": "STRUCTURALLY_CONSISTENT",
        "authority_admitted": False,
        "effect_permission": False,
        "reason": "INDEPENDENT_SOURCE_AND_LEGAL_REVIEW_REQUIRED"
    }
