import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "analysis/s160_state_open_flag_writer/verify_open_flag_store.py"
spec = importlib.util.spec_from_file_location("s160_verify", SCRIPT)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)


class OpenFlagWriter(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
        cls.data = json.loads(module.OUT.read_text())

    def test_store_targets_state_plus_zero(self):
        self.assertEqual(self.data["store"]["bytes_hex"], "1370")
        self.assertEqual(self.data["store"]["rea_typed_target"], "0x43f72d02")
        self.assertEqual(self.data["store"]["field_offset"], "0x0")

    def test_store_value_and_gate_scope(self):
        self.assertIn("stores byte value 0", self.data["store"]["store_data_semantics"])
        self.assertIn("not gate bytes +3/+6", self.data["scope_limit"])

    def test_state_pointer_slot(self):
        self.assertEqual(self.data["state_slot"]["bytes_hex"], "022df743")
        self.assertEqual(self.data["state_slot"]["value_le"], "0x43f72d02")


if __name__ == "__main__":
    unittest.main()
