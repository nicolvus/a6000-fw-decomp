import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "analysis/s150_imager_row_gaps/verify_gap_refs.py"
spec = importlib.util.spec_from_file_location("s150_verify", SCRIPT)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)


class ImagerRowGaps(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
        cls.data = json.loads(module.OUT.read_text())

    def test_eight_exact_gap_bytes_are_zero_in_blob(self):
        self.assertEqual(len(self.data["gaps"]), 8)
        self.assertTrue(all(row["bytes_hex"] == "0000" for row in self.data["gaps"]))

    def test_control_pointer_hits_middle_row_gap(self):
        tables = self.data["tables_with_pointer_literal"]
        self.assertEqual([t["words_le"][0] for t in tables],
                         ["0x43eb0850", "0x43eb0850"])
        self.assertEqual(self.data["rea"]["literal_search"]["matches"],
                         ["0x4400812c", "0x4400b27c"])

    def test_negative_scope_does_not_claim_global_absence(self):
        self.assertIn("Alias/parameterized accesses remain unknown",
                      self.data["conclusion_scope"])
        self.assertEqual(self.data["rea"]["positive_control"]["xrefs"],
                         ["0x43836910", "0x43836916"])


if __name__ == "__main__":
    unittest.main()
