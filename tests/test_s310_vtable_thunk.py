import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIR = ROOT / "analysis/s310_vtable_thunk"
VERIFY = DIR / "verify_thunk.py"
DATA = DIR / "thunk.json"


class VtableThunk(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        subprocess.run([sys.executable, str(VERIFY)], cwd=ROOT, check=True)
        cls.data = json.loads(DATA.read_text())

    def test_first_thunk_loads_vtable_slot_064(self):
        first = self.data["thunks"][0]
        self.assertEqual(first["entry"], "0x43ad96fa")
        self.assertEqual(first["vtable_slot"], "0x64")
        self.assertIn("blx r3", first["insn"])

    def test_six_thunks_with_distinct_slots(self):
        slots = [t["vtable_slot"] for t in self.data["thunks"]]
        self.assertEqual(len(slots), 6)
        self.assertEqual(len(set(slots)), 6)

    def test_selector_result_goes_to_thunk(self):
        path = self.data["selector_result_path"]
        self.assertEqual(path["passed_to"], "0x435490c4 bl 0x43ad9704")


if __name__ == "__main__":
    unittest.main()
