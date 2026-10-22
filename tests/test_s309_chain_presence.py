import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIR = ROOT / "analysis/s309_chain_presence"
VERIFY = DIR / "verify_presence.py"
DATA = DIR / "presence.json"


class ChainPresence(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        subprocess.run([sys.executable, str(VERIFY)], cwd=ROOT, check=True)
        cls.data = json.loads(DATA.read_text())

    def test_seven_functions_and_all_absent(self):
        self.assertEqual(len(self.data["chain"]), 7)
        self.assertTrue(all(r["a6000_hits"] == 0 for r in self.data["chain"]))

    def test_selector_and_timing_entries(self):
        entries = {r["label"]: r["entry"] for r in self.data["chain"]}
        self.assertEqual(entries["selector"], "0x43826d58")
        self.assertEqual(entries["timing_block"], "0x438645bc")

    def test_scope_limit_is_explicit(self):
        self.assertIn("reescrita", self.data["scope_limit"])


if __name__ == "__main__":
    unittest.main()
