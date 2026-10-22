import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIR = ROOT / "analysis/s303_ref_tree"
VERIFY = DIR / "verify_tree.py"
DATA = DIR / "ref_tree.json"


class RefTree(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        subprocess.run([sys.executable, str(VERIFY)], cwd=ROOT, check=True)
        cls.data = json.loads(DATA.read_text())

    def test_table_has_148_entries_and_state_at_18(self):
        t = self.data["table"]
        self.assertEqual(t["entries"], 148)
        self.assertEqual(t["state_index"], 18)
        self.assertEqual(t["state_entry"], "0x43ff3248")
        self.assertEqual(t["terminator"], "0x43ff3450")
        self.assertTrue(t["unique"])
        self.assertEqual(t["got_slot"]["value"], "0x43ff3200")

    def test_dumper_has_two_direct_callers_in_one_function(self):
        callers = self.data["dumper"]["direct_callers"]
        self.assertEqual({c["site"] for c in callers}, {"0x43859868", "0x43859892"})
        self.assertEqual({c["container_rea"] for c in callers}, {"0x43859710"})
        self.assertTrue(self.data["dumper"]["prologue_insn"].startswith("push"))

    def test_caller_function_has_ten_sites(self):
        callers = self.data["caller_function"]["callers"]
        self.assertEqual(len(callers), 10)
        self.assertIn("0x438599c6", {c["site"] for c in callers})

    def test_published_shifted_addresses_are_not_entries(self):
        for addr in ("0x438581e8", "0x43858390"):
            entry = self.data["corrections"][addr]
            self.assertFalse(entry["insn"].startswith("push"), addr)
            self.assertIn("no es entrada", entry["why"])


if __name__ == "__main__":
    unittest.main()
