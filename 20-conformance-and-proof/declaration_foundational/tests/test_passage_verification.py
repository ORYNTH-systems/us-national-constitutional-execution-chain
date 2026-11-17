import csv
import importlib.util
import shutil
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / "00-constitutional-source/declaration-of-independence"
SCRIPT = ROOT / "20-conformance-and-proof/declaration_foundational/verify_passages.py"

spec = importlib.util.spec_from_file_location("verify_passages", SCRIPT)
verifier = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verifier)


class PassageVerificationTests(unittest.TestCase):

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)

        self.base = Path(self.temp.name) / "evidence_baseline"
        self.base.mkdir()

        shutil.copytree(BASE / "evidence", self.base / "evidence")

        for name in (
            "CONSTITUTIONAL_PROVISION_SOURCE_INDEX.csv",
            "CONSTITUTIONAL_PROVISION_PASSAGES.csv",
        ):
            shutil.copy2(BASE / name, self.base / name)

    def change_register(self, filename, field, value):
        path = self.base / filename

        with path.open(newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            fields = reader.fieldnames
            rows = list(reader)

        rows[0][field] = value

        with path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)

    def test_unmodified_evidence_passes(self):
        self.assertEqual(len(verifier.verify_all(self.base)), 17)

    def test_archived_source_tampering_rejected(self):
        path = (
            self.base / "evidence" /
            "national-archives-constitution-transcript.html"
        )

        with path.open("ab") as f:
            f.write(b"\nTAMPERED")

        with self.assertRaises(ValueError):
            verifier.verify_all(self.base)

    def test_passage_digest_tampering_rejected(self):
        self.change_register(
            "CONSTITUTIONAL_PROVISION_PASSAGES.csv",
            "extracted_html_sha256",
            "0" * 64,
        )

        with self.assertRaises(ValueError):
            verifier.verify_all(self.base)

    def test_source_span_tampering_rejected(self):
        self.change_register(
            "CONSTITUTIONAL_PROVISION_PASSAGES.csv",
            "source_span",
            "HTML:L1-L2",
        )

        with self.assertRaises(ValueError):
            verifier.verify_all(self.base)

    def test_line_boundary_tampering_rejected(self):
        self.change_register(
            "CONSTITUTIONAL_PROVISION_PASSAGES.csv",
            "start_line",
            "1",
        )

        with self.assertRaises(ValueError):
            verifier.verify_all(self.base)

    def test_fabricated_extraction_status_rejected(self):
        self.change_register(
            "CONSTITUTIONAL_PROVISION_PASSAGES.csv",
            "extraction_status",
            "VERIFIED",
        )

        with self.assertRaises(ValueError):
            verifier.verify_all(self.base)

    def test_unauthorized_legal_effect_rejected(self):
        self.change_register(
            "CONSTITUTIONAL_PROVISION_PASSAGES.csv",
            "legal_effect",
            "BINDING_AUTHORITY",
        )

        with self.assertRaises(ValueError):
            verifier.verify_all(self.base)


if __name__ == "__main__":
    unittest.main()
