import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "analysis/s159_imager_state_ref/verify_state_spill.py"
spec = importlib.util.spec_from_file_location("s159_verify", SCRIPT)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)


class StateSpill(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
        cls.data = json.loads(module.OUT.read_text())

    def test_got_value_and_stack_spill(self):
        self.assertEqual(self.data["state_got_slot"]["value_le"], "0x43f72d02")
        ins = [i["text"] for i in self.data["regions"][0]["instructions"]]
        self.assertIn("str r3, [sp, #0x1c]", ins)

    def test_accessor_reads_fields_not_gate_offsets(self):
        ins = [i["text"] for region in self.data["regions"]
               for i in region["instructions"]]
        self.assertTrue(any("#0xa2" in i for i in ins))
        self.assertIn("strb.w sl, [r3, #0x34b]", ins)
        self.assertIn("This function xref is a stack spill",
                      self.data["scope_limit"])

    def test_firmware_identity(self):
        self.assertEqual(self.data["firmware_sha256"],
                         "b60c845ccb90c0ff86b7f62f1f3f2ecda714aa20c37805959ebee2b429e56bb9")


if __name__ == "__main__":
    unittest.main()
