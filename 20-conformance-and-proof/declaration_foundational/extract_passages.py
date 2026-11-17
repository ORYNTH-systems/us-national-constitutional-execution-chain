import csv
import hashlib
import html
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "00-constitutional-source" / "declaration-of-independence"
EVIDENCE = BASE / "evidence"
INDEX = BASE / "CONSTITUTIONAL_PROVISION_SOURCE_INDEX.csv"
OUTPUT = BASE / "CONSTITUTIONAL_PROVISION_PASSAGES.csv"

ARTICLE = re.compile(r'<h2 id="([1-7])">')
SECTION = re.compile(r'<h3 id="([1-7])-(\d+)">')
BILL_AMENDMENT = re.compile(r'<h3>Amendment ([IVX]+)</h3>')
LATER_AMENDMENT = re.compile(
    r'<h2[^>]*>.*AMENDMENT\s+([IVX]+)\b',
    re.IGNORECASE,
)
MAIN_CLOSE = re.compile(r"</section\s*>", re.IGNORECASE)

def sha256(data):
    return hashlib.sha256(data).hexdigest().upper()

def load_lines(path):
    raw = path.read_bytes()
    return raw, raw.decode("utf-8-sig").splitlines()

def boundary(lines, start, reference):
    if reference == "US-CONST:PREAMBLE":
        for i in range(start, len(lines)):
            if ARTICLE.search(lines[i]):
                return i
        raise ValueError("Preamble closing boundary missing")

    if ":ARTICLE-" in reference:
        section_specific = "-SECTION-" in reference

        for i in range(start, len(lines)):
            if ARTICLE.search(lines[i]):
                return i
            if section_specific and SECTION.search(lines[i]):
                return i

        raise ValueError("Article or section closing boundary missing")

    if ":AMENDMENT-" in reference:
        is_bill = "bill-of-rights" in reference_source[reference]

        for i in range(start, len(lines)):
            line = lines[i]

            if is_bill and BILL_AMENDMENT.search(line):
                return i

            if not is_bill and LATER_AMENDMENT.search(line):
                return i

            if MAIN_CLOSE.search(line):
                return i

        raise ValueError("Amendment closing boundary missing")

    raise ValueError("Unknown reference type")

with INDEX.open(newline="", encoding="utf-8-sig") as f:
    entries = list(csv.DictReader(f))

if len(entries) != 17:
    raise ValueError("Expected 17 indexed provisions")

reference_source = {
    row["constitutional_reference"]: row["source_file"]
    for row in entries
}

if len(reference_source) != 17:
    raise ValueError("Duplicate constitutional reference")

results = []

for entry in entries:
    reference = entry["constitutional_reference"]
    path = EVIDENCE / entry["source_file"]

    raw, lines = load_lines(path)

    if sha256(raw) != entry["source_sha256"].upper():
        raise ValueError(f"Source hash mismatch: {reference}")

    if entry["source_status"] != "HEADING_LOCATED":
        raise ValueError(f"Unresolved heading: {reference}")

    start = int(entry["heading_line"]) - 1

    if not 0 <= start < len(lines):
        raise ValueError(f"Invalid heading line: {reference}")

    end = boundary(lines, start + 1, reference)

    precision_rules = {
        "US-CONST:ARTICLE-I-SECTION-8-CLAUSE-3": (
            445, 445, "To regulate Commerce with foreign Nations"
        ),
        "US-CONST:ARTICLE-I-SECTION-8-CLAUSE-4": (
            447, 447, "To establish an uniform Rule of Naturalization"
        ),
        "US-CONST:AMENDMENT-XIV-SECTION-1": (
            408, 410, "All persons born or naturalized in the United States"
        ),
    }

    if reference in precision_rules:
        first, last, expected = precision_rules[reference]

        if not (start <= first - 1 < last <= end):
            raise ValueError(f"Invalid precision boundary: {reference}")

        candidate = "\n".join(lines[first - 1:last])

        if expected not in candidate:
            raise ValueError(f"Missing provision text: {reference}")

        if reference.endswith("AMENDMENT-XIV-SECTION-1"):
            if 'id="xiv1"' not in candidate or 'id="xiv2"' in candidate:
                raise ValueError("Incorrect Fourteenth Amendment section")
        elif candidate.count("<p>") != 1:
            raise ValueError(f"Clause not isolated: {reference}")

        start = first - 1
        end = last

    if end <= start:
        raise ValueError(f"Empty passage: {reference}")

    section = lines[start:end]

    if reference == "US-CONST:AMENDMENT-X":
        # The actual constitutional text ends at line 459.
        # Exclude the navigation beginning at line 461.
        text_line = next(
            (
                i for i in range(start + 1, end)
                if "The powers not delegated to the United States"
                in lines[i]
            ),
            None,
        )

        if text_line is None:
            raise ValueError("Amendment X text not found")

        end = text_line + 1
        section = lines[start:end]

    if not any("<p" in line for line in section):
        raise ValueError(f"No constitutional paragraph: {reference}")

    exact_html = "\n".join(section)

    results.append({
        "constitutional_reference": reference,
        "source_file": entry["source_file"],
        "source_sha256": sha256(raw),
        "start_line": start + 1,
        "end_line": end,
        "source_span": f"HTML:L{start + 1}-L{end}",
        "extracted_html_sha256": sha256(exact_html.encode("utf-8")),
        "extraction_status": "EXTRACTED_PENDING_VERIFICATION",
        "interpretation_status": "NOT_REVIEWED",
        "legal_effect": "NONE_INFERRED",
    })

if len(results) != 17:
    raise ValueError("Incomplete extraction")

if OUTPUT.exists():
    raise FileExistsError("Output exists; refusing overwrite")

with OUTPUT.open("x", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=results[0].keys())
    writer.writeheader()
    writer.writerows(results)

print("PASS: 17 candidate constitutional passages extracted")
print("PASS: Source hashes match acquisition evidence")
print("PASS: Interpretation remains unreviewed")
for row in results:
    print(
        row["constitutional_reference"],
        row["source_span"],
        row["extraction_status"],
        sep=" | ",
    )