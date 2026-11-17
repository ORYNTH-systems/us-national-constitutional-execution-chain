import csv
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]

BASE_REL = Path(
    "00-constitutional-source/declaration-of-independence"
)

SCRIPT_REL = Path(
    "20-conformance-and-proof/declaration_foundational/extract_passages.py"
)

EXPECTED_SPANS = {
    "US-CONST:AMENDMENT-XIV-SECTION-1": "HTML:L408-L410",
    "US-CONST:ARTICLE-I-SECTION-8-CLAUSE-3": "HTML:L445-L445",
    "US-CONST:ARTICLE-I-SECTION-8-CLAUSE-4": "HTML:L447-L447",
    "US-CONST:AMENDMENT-X": "HTML:L457-L459",
}


def load_csv(path):
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


class PassageReproducibilityTests(unittest.TestCase):

    def test_independent_rebuild(self):
        source_base = ROOT / BASE_REL

        expected = load_csv(
            source_base / "CONSTITUTIONAL_PROVISION_PASSAGES.csv"
        )

        self.assertEqual(len(expected), 17)

        expected_map = {
            row["constitutional_reference"]: row
            for row in expected
        }

        self.assertEqual(len(expected_map), 17)

        for reference, span in EXPECTED_SPANS.items():
            self.assertEqual(
                expected_map[reference]["source_span"],
                span
            )

        with tempfile.TemporaryDirectory() as temporary:
            isolated = Path(temporary)
            target_base = isolated / BASE_REL

            target_base.mkdir(parents=True)

            shutil.copytree(
                source_base / "evidence",
                target_base / "evidence"
            )

            shutil.copy2(
                source_base / "CONSTITUTIONAL_PROVISION_SOURCE_INDEX.csv",
                target_base / "CONSTITUTIONAL_PROVISION_SOURCE_INDEX.csv"
            )

            target_script = isolated / SCRIPT_REL
            target_script.parent.mkdir(parents=True)

            shutil.copy2(
                ROOT / SCRIPT_REL,
                target_script
            )

            result = subprocess.run(
                [sys.executable, str(target_script)],
                cwd=isolated,
                capture_output=True,
                text=True
            )

            self.assertEqual(
                result.returncode,
                0,
                result.stdout + result.stderr
            )

            actual = load_csv(
                target_base / "CONSTITUTIONAL_PROVISION_PASSAGES.csv"
            )

            actual_map = {
                row["constitutional_reference"]: row
                for row in actual
            }

            self.assertEqual(len(actual), 17)
            self.assertEqual(len(actual_map), 17)
            self.assertEqual(expected_map, actual_map)

            for row in actual:
                self.assertEqual(
                    row["legal_effect"],
                    "NONE_INFERRED"
                )
                self.assertEqual(
                    row["interpretation_status"],
                    "NOT_REVIEWED"
                )


if __name__ == "__main__":
    unittest.main()