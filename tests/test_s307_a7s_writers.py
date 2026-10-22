import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIR = ROOT / "analysis/s307_a7s_writers"
VERIFY = DIR / "verify_writers.py"
DATA = DIR / "writers.json"


class A7sOnlyWriters(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        subprocess.run([sys.executable, str(VERIFY)], cwd=ROOT, check=True)
        cls.data = json.loads(DATA.read_text())

    def test_de_and_trio_are_absent_from_a6000(self):
        by_field = {}
        for row in self.data["writers"]:
            for w in row["write_sites"]:
                by_field.setdefault(row["field"], []).append(w["a6000_signature_hits"])
        self.assertEqual(by_field["state+0xde"], [0])
        self.assertEqual(by_field["state+0xe6/+0xe8/+0xea"], [0, 0, 0])

    def test_shared_zero_and_plus2_stores_exist_in_a6000(self):
        rows = {r["function"]: r for r in self.data["writers"]}
        zero = rows["0x4385a290"]["write_sites"][0]
        self.assertEqual(zero["a6000_signature_hits"], 1)
        plus2 = rows["0x4385a98c"]["write_sites"][0]
        self.assertEqual(plus2["a6000_signature_hits"], 1)

    def test_timing_function_has_one_direct_caller_and_no_pointer(self):
        tf = self.data["timing_function"]
        self.assertEqual(tf["entry"], "0x438645bc")
        self.assertEqual(tf["direct_callers"], ["0x43861be4"])
        self.assertEqual(tf["literal_pointer_hits"], 0)

    def test_selector_has_two_callers(self):
        sel = self.data["selector"]
        self.assertEqual(sel["insn"], "cmp r0, #5")
        self.assertEqual(sel["callers_direct"], ["0x4354908c", "0x43826df2"])


if __name__ == "__main__":
    unittest.main()
