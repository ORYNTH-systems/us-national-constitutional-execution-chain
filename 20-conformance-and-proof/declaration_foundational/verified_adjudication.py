"""Evidence-bound, fail-closed constitutional adjudication entry point."""

import csv
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "00-constitutional-source/declaration-of-independence"
MODULE_DIR = Path(__file__).resolve().parent


def load_module(name):
    path = MODULE_DIR / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


verifier = load_module("verify_passages")
gate = load_module("adjudication_gate")


def read_csv(path):
    with path.open(newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def indexed(rows, field):
    result = {}

    for row in rows:
        key = row[field]

        if not key or key in result:
            raise ValueError(f"Duplicate or missing identifier: {key}")

        result[key] = row

    return result


def verify_adjudication_baseline(base=BASE):
    base = Path(base)

    evidence = verifier.verify_all(base)

    canonical = read_csv(
        base / "DECLARATION_RELATIONSHIP_ADJUDICATION.csv"
    )

    proposals = read_csv(
        base / "DECLARATION_RELATIONSHIP_PROPOSALS.csv"
    )

    passages = read_csv(
        base / "CONSTITUTIONAL_PROVISION_PASSAGES.csv"
    )

    canonical_map = indexed(canonical, "foundational_id")
    proposal_map = indexed(proposals, "foundational_id")
    passage_map = indexed(passages, "constitutional_reference")

    if len(canonical_map) != 27 or len(proposal_map) != 27:
        raise ValueError("Incomplete adjudication coverage")

    if set(canonical_map) != set(proposal_map):
        raise ValueError("Proposal and adjudication mismatch")

    for fid, record in canonical_map.items():
        proposal = proposal_map[fid]
        ref = record["constitutional_reference"]

        if ref not in evidence or ref not in passage_map:
            raise ValueError(f"Missing verified provision: {fid}")

        passage = passage_map[ref]
        verified = evidence[ref]

        if ref != proposal["proposed_constitutional_provision"]:
            raise ValueError(f"Proposal reference mismatch: {fid}")

        if (
            record["proposed_relationship_class"]
            != proposal["proposed_relationship_class"]
        ):
            raise ValueError(f"Proposed class mismatch: {fid}")

        if (
            record["constitutional_source_span"]
            != verified["source_span"]
        ):
            raise ValueError(f"Source span mismatch: {fid}")

        if (
            record["constitutional_source_sha256"].upper()
            != verified["passage_sha256"]
        ):
            raise ValueError(f"Passage digest mismatch: {fid}")

        if record["source_verification"] != passage["extraction_status"]:
            raise ValueError(f"Extraction state mismatch: {fid}")

        if record["disposition"] != "PENDING":
            raise ValueError(f"Premature canonical disposition: {fid}")

        if record["review_status"] != "NOT_REVIEWED":
            raise ValueError(f"Premature canonical approval: {fid}")

        if record["legal_effect"] != "NONE_INFERRED":
            raise ValueError(f"Unauthorized legal effect: {fid}")

        if record["adjudicated_relationship_class"]:
            raise ValueError(f"Premature adjudicated class: {fid}")

    return {
        "verified_passages": len(evidence),
        "pending_adjudications": len(canonical_map),
        "verified_references": frozenset(evidence),
    }


def validate_proposed_transition(
    foundational_id,
    proposed_record,
    base=BASE,
):
    """Reject transitions until evidence and independent review are complete."""

    baseline = verify_adjudication_baseline(base)

    canonical = indexed(
        read_csv(
            Path(base) / "DECLARATION_RELATIONSHIP_ADJUDICATION.csv"
        ),
        "foundational_id",
    )

    if foundational_id not in canonical:
        raise ValueError("Unknown foundational identifier")

    ref = canonical[foundational_id]["constitutional_reference"]

    if ref not in baseline["verified_references"]:
        raise ValueError("Constitutional evidence not verified")

    if proposed_record.get("legal_effect") != "NONE_INFERRED":
        raise ValueError("Legal authority cannot arise from crosswalk")

    if proposed_record.get("disposition") != "PENDING":
        raise ValueError(
            "Adjudication requires independent relationship-review gate"
        )

    if proposed_record.get("relationship_assessment") != "NOT_ASSESSED":
        raise ValueError("Premature relationship assessment")

    record = dict(proposed_record)
    record["source_verification"] = "EXTRACTED_PENDING_VERIFICATION"

    return gate.validate(record)


if __name__ == "__main__":
    result = verify_adjudication_baseline()

    print(
        "PASS:",
        result["verified_passages"],
        "constitutional passage digests verified",
    )
    print(
        "PASS:",
        result["pending_adjudications"],
        "canonical adjudications remain pending",
    )
    print("PASS: Evidence and adjudication references bound")
    print("PASS: No relationship or legal authority promoted")
