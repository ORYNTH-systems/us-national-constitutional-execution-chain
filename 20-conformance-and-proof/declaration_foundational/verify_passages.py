"""Read-only independent verification of archived constitutional passages."""

import csv
import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "00-constitutional-source/declaration-of-independence"
EVIDENCE = BASE / "evidence"

INDEX = BASE / "CONSTITUTIONAL_PROVISION_SOURCE_INDEX.csv"
PASSAGES = BASE / "CONSTITUTIONAL_PROVISION_PASSAGES.csv"


def digest(data):
    return hashlib.sha256(data).hexdigest().upper()


def read_csv(path):
    with path.open(newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def unique_map(rows, key):
    result = {}

    for row in rows:
        value = row[key]

        if not value or value in result:
            raise ValueError(f"Missing or duplicate identifier: {value}")

        result[value] = row

    return result


def verify_all(base=BASE):
    base = Path(base)
    evidence = base / "evidence"

    index = read_csv(
        base / "CONSTITUTIONAL_PROVISION_SOURCE_INDEX.csv"
    )

    passages = read_csv(
        base / "CONSTITUTIONAL_PROVISION_PASSAGES.csv"
    )

    if len(index) != 17 or len(passages) != 17:
        raise ValueError("Expected exactly 17 source and passage records")

    indexed = unique_map(index, "constitutional_reference")
    registered = unique_map(passages, "constitutional_reference")

    if set(indexed) != set(registered):
        raise ValueError("Index and passage coverage mismatch")

    verified = {}

    for ref, record in registered.items():
        source = indexed[ref]

        if source["source_status"] != "HEADING_LOCATED":
            raise ValueError(f"Unresolved source heading: {ref}")

        if record["source_file"] != source["source_file"]:
            raise ValueError(f"Source file mismatch: {ref}")

        if record["source_sha256"] != source["source_sha256"]:
            raise ValueError(f"Source digest register mismatch: {ref}")

        if record["extraction_status"] != "EXTRACTED_PENDING_VERIFICATION":
            raise ValueError(f"Unexpected extraction state: {ref}")

        if record["interpretation_status"] != "NOT_REVIEWED":
            raise ValueError(f"Unexpected interpretation state: {ref}")

        if record["legal_effect"] != "NONE_INFERRED":
            raise ValueError(f"Unauthorized legal effect: {ref}")

        filename = source["source_file"]

        if not filename or Path(filename).name != filename:
            raise ValueError(f"Unsafe source filename: {ref}")

        path = evidence / filename
        raw = path.read_bytes()

        actual_source_hash = digest(raw)

        if actual_source_hash != source["source_sha256"].upper():
            raise ValueError(f"Archived source digest mismatch: {ref}")

        lines = raw.decode("utf-8-sig").splitlines()

        start = int(record["start_line"])
        end = int(record["end_line"])
        heading = int(source["heading_line"])

        if not (1 <= start <= end <= len(lines)):
            raise ValueError(f"Invalid passage boundaries: {ref}")

        if not (1 <= heading <= len(lines)):
            raise ValueError(f"Invalid indexed heading: {ref}")

        if source["source_file"] != filename:
            raise ValueError(f"Source mismatch: {ref}")

        if not (
            start == heading
            or ref in {
                "US-CONST:ARTICLE-I-SECTION-8-CLAUSE-3",
                "US-CONST:ARTICLE-I-SECTION-8-CLAUSE-4",
                "US-CONST:AMENDMENT-XIV-SECTION-1",
            }
        ):
            raise ValueError(f"Unexplained heading offset: {ref}")

        expected_span = f"HTML:L{start}-L{end}"

        if record["source_span"] != expected_span:
            raise ValueError(f"Source span mismatch: {ref}")

        exact_html = "\n".join(lines[start - 1:end])

        if "<p" not in exact_html:
            raise ValueError(f"No constitutional paragraph: {ref}")

        actual_passage_hash = digest(
            exact_html.encode("utf-8")
        )

        if actual_passage_hash != record["extracted_html_sha256"]:
            raise ValueError(f"Extracted passage digest mismatch: {ref}")

        verified[ref] = {
            "source_sha256": actual_source_hash,
            "passage_sha256": actual_passage_hash,
            "source_span": expected_span,
        }

    return verified


if __name__ == "__main__":
    verified = verify_all()

    print(f"PASS: {len(verified)}/17 constitutional passages verified")
    print("PASS: Archived source bytes match indexed hashes")
    print("PASS: Recorded passage digests independently reproduced")
    print("PASS: No interpretation or legal authority inferred")
    print("NOTE: Verification does not establish historical causation")
