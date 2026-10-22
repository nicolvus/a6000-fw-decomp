import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "analysis/s158_imager_state_ref/verify_gate_accessor.py"
spec = importlib.util.spec_from_file_location("s158_verify", SCRIPT)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)


class StateAccessorRef(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
        cls.data = json.loads(module.OUT.read_text())

    def test_xref_instruction_spills_pointer_to_stack(self):
        self.assertEqual(self.data["got_slot"]["bytes_hex"], "022df743")
        lines = [i["text"] for i in self.data["procedure_ranges"][1]["instructions"]]
        self.assertIn("str r3, [sp, #0x20]", lines)

    def test_state_accessor_reads_non_gate_fields(self):
        lines = [i["text"] for region in self.data["procedure_ranges"]
                 for i in region["instructions"]]
        self.assertTrue(any("#0x28" in line for line in lines))
        self.assertTrue(any("#0x26" in line for line in lines))
        self.assertTrue(any("#0x29" in line for line in lines))
        self.assertIn("Only FUN_4385b234", self.data["scope_limit"])

    def test_firmware_identity(self):
        self.assertEqual(self.data["firmware_sha256"],
                         "b60c845ccb90c0ff86b7f62f1f3f2ecda714aa20c37805959ebee2b429e56bb9")


if __name__ == "__main__":
    unittest.main()
