import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "analysis/s161_imager_state_spill/verify_state_spill.py"
spec = importlib.util.spec_from_file_location("s161_verify", SCRIPT)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)


class StatePointerSpill(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
        cls.data = json.loads(module.OUT.read_text())

    def test_pointer_slot_and_stack_spill(self):
        self.assertEqual(self.data["state_got_slot"]["value_le"], "0x43f72d02")
        instructions = [i["text"] for r in self.data["regions"] for i in r["instructions"]]
        self.assertIn("ldr.w r3, [r8, r3]", instructions)
        self.assertIn("str r3, [sp, #0x20]", instructions)

    def test_typed_write_is_scoped_to_stack(self):
        self.assertEqual(self.data["regions"][0]["bytes_hex"][16:20], "0893")
        self.assertIn("actual instruction writes stack",
                      self.data["scope_limit"])

    def test_firmware_identity(self):
        self.assertEqual(self.data["firmware_sha256"],
                         "b60c845ccb90c0ff86b7f62f1f3f2ecda714aa20c37805959ebee2b429e56bb9")


if __name__ == "__main__":
    unittest.main()
