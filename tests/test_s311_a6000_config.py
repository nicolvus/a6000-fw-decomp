import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIR = ROOT / "analysis/s311_a6000_config"
VERIFY = DIR / "verify_config.py"
DATA = DIR / "config.json"


class A6000Config(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        subprocess.run([sys.executable, str(VERIFY)], cwd=ROOT, check=True)
        cls.data = json.loads(DATA.read_text())

    def test_four_writers_with_two_absent_in_a7s(self):
        hits = [r["a7s_head_hits"] for r in self.data["writers"]]
        self.assertEqual(len(hits), 4)
        self.assertEqual(hits.count(0), 2)
        self.assertEqual(hits.count(1), 2)

    def test_exclusive_writers_match_s307_offsets(self):
        by_func = {r["function"]: r for r in self.data["writers"]}
        self.assertEqual(by_func["0x43833ff8"]["field"], "state+0x02")
        self.assertEqual(by_func["0x4383ace0"]["field"], "state+0x02")
        self.assertEqual(by_func["0x4383abec"]["field"], "state+0x00")

    def test_callers_are_recorded(self):
        for row in self.data["writers"]:
            self.assertGreaterEqual(len(row["callers"]), 1, row["function"])


if __name__ == "__main__":
    unittest.main()
