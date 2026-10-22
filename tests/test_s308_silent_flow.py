import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIR = ROOT / "analysis/s308_silent_flow"
VERIFY = DIR / "verify_flow.py"
DATA = DIR / "flow.json"


class SilentFlow(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        subprocess.run([sys.executable, str(VERIFY)], cwd=ROOT, check=True)
        cls.data = json.loads(DATA.read_text())

    def test_selector_result_goes_to_message_builder(self):
        by_label = {c["label"]: c for c in self.data["selector_site"]}
        self.assertEqual(by_label["selector_call"]["insn"], "bl #0x43826d58")
        self.assertEqual(by_label["selector_result_saved"]["insn"], "str r0, [sp, #0x2c]")
        self.assertEqual(by_label["selector_result_used"]["insn"], "bl #0x43ad9704")

    def test_timing_entry_is_bc_with_one_caller(self):
        by_label = {c["label"]: c for c in self.data["selector_site"]}
        self.assertEqual(by_label["timing_entry"]["address"], "0x438645bc")
        self.assertEqual(self.data["timing_entry_direct_callers"], ["0x43861be4"])

    def test_no_pointer_targets_timing_entry(self):
        values = {p["value"] for p in self.data["pointers_into_0x43864xxx"]}
        self.assertNotIn("0x438645bc", values)
        self.assertEqual(len(self.data["pointers_into_0x43864xxx"]), 4)


if __name__ == "__main__":
    unittest.main()
