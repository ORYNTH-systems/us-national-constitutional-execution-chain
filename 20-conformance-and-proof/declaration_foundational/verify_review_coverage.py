import csv
from collections import Counter
from pathlib import Path

from verified_adjudication import verify_adjudication_baseline

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "00-constitutional-source/declaration-of-independence"

GROUP_COUNTS = {"A": 4, "B": 5, "C": 4, "D": 5, "E": 2}
DISPOSITIONS = {"RETAIN", "NARROW", "RECLASSIFY", "REJECT"}
CLASSES = {"DIRECT_TEXTUAL", "STRUCTURAL", "HISTORICAL_CONTEXT"}


def load(base, filename):
    with (base / filename).open(newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def indexed(rows, label):
    ids = [r["foundational_id"] for r in rows]
    if len(ids) != len(set(ids)):
        raise ValueError(f"Duplicate foundational IDs: {label}")
    return {r["foundational_id"]: r for r in rows}


def verify_review_coverage(base=BASE, evidence_base=BASE):
    verified = verify_adjudication_baseline(evidence_base)

    proposals = indexed(
        load(base, "DECLARATION_RELATIONSHIP_PROPOSALS.csv"),
        "proposals",
    )
    canonical = indexed(
        load(base, "DECLARATION_RELATIONSHIP_ADJUDICATION.csv"),
        "canonical",
    )
    wave1 = load(base, "DECLARATION_RELATIONSHIP_REVIEW_WAVE_01.csv")
    wave1_ids = set(indexed(wave1, "Wave 01"))

    wave2 = []
    for group, expected_count in GROUP_COUNTS.items():
        rows = load(
            base,
            f"DECLARATION_RELATIONSHIP_REVIEW_WAVE_02_GROUP_{group}.csv",
        )
        if len(rows) != expected_count:
            raise ValueError(f"Group {group} coverage mismatch")
        wave2.extend(rows)

    reviews = indexed(wave1 + wave2, "combined review")

    if len(proposals) != 27 or len(canonical) != 27 or len(reviews) != 27:
        raise ValueError("Expected exactly 27 records in each register")

    if set(reviews) != set(proposals) or set(reviews) != set(canonical):
        raise ValueError("Proposal, review, and canonical coverage mismatch")

    verified_refs = verified["verified_references"]

    for fid, review in reviews.items():
        proposal = proposals[fid]
        canon = canonical[fid]

        ref = review["constitutional_reference"]

        if ref != proposal["proposed_constitutional_provision"]:
            raise ValueError(f"Proposal reference mismatch: {fid}")

        if ref != canon["constitutional_reference"]:
            raise ValueError(f"Canonical reference mismatch: {fid}")

        if ref not in verified_refs:
            raise ValueError(f"Unverified constitutional reference: {fid}")

        if review["recommended_disposition"] not in DISPOSITIONS:
            raise ValueError(f"Invalid disposition: {fid}")

        if review["legal_effect"] != "NONE_INFERRED":
            raise ValueError(f"Unauthorized review legal effect: {fid}")

        if review["historical_causation"] != "NOT_ESTABLISHED":
            raise ValueError(f"Unsupported historical causation: {fid}")

        if review["review_state"] != "ANALYTICAL_RECOMMENDATION":
            raise ValueError(f"Unauthorized review state: {fid}")

        if not review["review_rationale"].strip():
            raise ValueError(f"Missing review rationale: {fid}")

        if canon["disposition"] != "PENDING":
            raise ValueError(f"Premature canonical disposition: {fid}")

        if canon["legal_effect"] != "NONE_INFERRED":
            raise ValueError(f"Canonical authority promotion: {fid}")

        if fid in wave1_ids:
            continue

        original = review["existing_relationship_class"]
        recommended = review["recommended_relationship_class"]

        if original != proposal["proposed_relationship_class"]:
            raise ValueError(f"Original class mismatch: {fid}")

        if recommended not in CLASSES:
            raise ValueError(f"Invalid recommended class: {fid}")

        if original != recommended and review["recommended_disposition"] != "RECLASSIFY":
            raise ValueError(f"Unacknowledged reclassification: {fid}")

        if not review["scope_limitations"].strip():
            raise ValueError(f"Missing scope limitation: {fid}")

        if review["independent_historical_sources"] != "NOT_YET_ADMITTED":
            raise ValueError(f"Unadmitted historical evidence: {fid}")

    return {
        "total": len(reviews),
        "distribution": dict(
            Counter(r["recommended_disposition"] for r in reviews.values())
        ),
    }


if __name__ == "__main__":
    result = verify_review_coverage()
    print(f"PASS: {result['total']}/27 unique reviews verified")
    for disposition, count in sorted(result["distribution"].items()):
        print(f"  {disposition}: {count}")
    print("PASS: No canonical adjudication promoted")
    print("PASS: No legal authority inferred")
