"""S344 - tests del carril B: tablas selectoras de 0x436f6240."""
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JSON = ROOT / "analysis/s344_selector_tables/selector_tables.json"
VERIFY = ROOT / "analysis/s344_selector_tables/verify_selector_tables.py"


class SelectorTables(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d = json.loads(JSON.read_text())

    def test_tables(self):
        self.assertEqual(self.d["tables"]["table_a"]["values"], [0, 1, 4])
        self.assertEqual(self.d["tables"]["table_b"]["values"], [6, 5, 4])
        self.assertTrue(self.d["tables"]["table_b"]["starts_at_t1_end"])
        self.assertEqual(self.d["tables"]["table_a"]["ends_at"], "0x43bbeb70")

    def test_selector_semantics(self):
        f = self.d["function"]
        self.assertEqual(f["wrapper_index_limit"], 0x21)
        self.assertEqual(f["wrapper_t1_base"], "0x43bbeb70")
        self.assertEqual(f["core"], "0x436f6240")

    def test_a7s_per_mode(self):
        self.assertEqual(self.d["verdicts"]["a7s_values"], {"1": 32, "4": 2})
        self.assertEqual(self.d["verdicts"]["a7s_modes_with_4"], ["0x37", "0x38"])
        vals = [p["value"] for p in self.d["per_mode_a7s"]]
        self.assertEqual(len(vals), 34)
        self.assertEqual(vals.count(4), 2)

    def test_a6000_per_mode(self):
        self.assertEqual(self.d["verdicts"]["a6000_values"], {"1": 13})
        self.assertEqual([p["value"] for p in self.d["per_mode_a6000"]], [1] * 13)

    def test_no_static_caller(self):
        c = self.d["callers"]
        self.assertEqual(c["core"], [])
        self.assertEqual(c["wrapper"], [])
        self.assertEqual(c["literal_core"], [])
        self.assertEqual(c["literal_wrapper"], [])
        self.assertFalse(self.d["verdicts"]["static_caller"])

    def test_not_silent(self):
        self.assertFalse(self.d["verdicts"]["silent_related"])
        self.assertEqual(self.d["verdicts"]["meaning_of_value"], "NO_VERIFICADO")

    def test_limits_and_verify(self):
        self.assertIn("S51", " ".join(self.d["limits"]))
        res = subprocess.run([sys.executable, str(VERIFY)], capture_output=True,
                             text=True, check=False)
        self.assertEqual(res.returncode, 0, res.stdout + res.stderr)
        self.assertIn("0 fallos", res.stdout)


if __name__ == "__main__":
    unittest.main()
