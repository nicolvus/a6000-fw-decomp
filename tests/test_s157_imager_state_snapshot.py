import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "analysis/s157_imager_state_snapshot/verify_snapshot_ref.py"
spec = importlib.util.spec_from_file_location("s157_verify", SCRIPT)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)


class StateSnapshotRef(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
        cls.data = json.loads(module.OUT.read_text())

    def test_reference_loads_got_slot_to_state_base(self):
        self.assertEqual(self.data["got_slots"][0]["bytes_hex"], "022df743")
        self.assertEqual(self.data["got_slots"][0]["value_le"], "0x43f72d02")
        text = [i["text"] for i in self.data["procedures"][0]["instructions"]]
        self.assertIn("ldr r2, [r4, r3]", text)

    def test_procedure_reads_other_offsets_and_has_no_gate_store_in_listing(self):
        text = [i["text"] for i in self.data["procedures"][0]["instructions"]]
        self.assertTrue(any("#5" in line and line.startswith("ldrb") for line in text))
        self.assertTrue(any("#0xf" in line and line.startswith("ldrb") for line in text))
        self.assertFalse(any("[r2, #3]" in line or "[r2, #6]" in line
                             for line in text if line.startswith("str")))

    def test_stores_are_scoped_to_this_procedure(self):
        self.assertIn("Only FUN_43859944", self.data["scope_limit"])
        self.assertEqual(self.data["firmware_sha256"],
                         "b60c845ccb90c0ff86b7f62f1f3f2ecda714aa20c37805959ebee2b429e56bb9")


if __name__ == "__main__":
    unittest.main()
