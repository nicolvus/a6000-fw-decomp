import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "analysis/s163_imager_state_event_reader/verify_state_event.py"
spec = importlib.util.spec_from_file_location("s163_verify", SCRIPT)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)


class StateEventReader(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
        cls.data = json.loads(module.OUT.read_text())

    def test_reads_halfword_plus_1c_and_byte_plus_1e(self):
        lines = [i["text"] for i in self.data["regions"][0]["instructions"]]
        self.assertIn("ldrh r7, [r3, #0x1c]", lines)
        self.assertIn("ldrb.w r8, [r3, #0x1e]", lines)

    def test_state_pointer_slot_and_other_write_targets(self):
        self.assertEqual(self.data["state_pointer_slots"][0]["value_le"], "0x43f72d02")
        self.assertNotIn("0x43f72d02", self.data["write_destinations_not_state"])
        self.assertIn("runtime reachability", self.data["scope_limit"])

    def test_firmware_identity(self):
        self.assertEqual(self.data["firmware_sha256"],
                         "b60c845ccb90c0ff86b7f62f1f3f2ecda714aa20c37805959ebee2b429e56bb9")


if __name__ == "__main__":
    unittest.main()
