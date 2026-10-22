import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "analysis/s153_imager_dump_gates/verify_gates.py"
spec = importlib.util.spec_from_file_location("s153_verify", SCRIPT)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)


class ImagerDumpGates(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
        cls.data = json.loads(module.OUT.read_text())

    def test_gate_instruction_bytes(self):
        gates = self.data["gate_bytes"]
        self.assertEqual(gates["offset_3_mask_0x02"]["bytes_hex"], "f37813f0020f08d0")
        self.assertEqual(gates["offset_6_mask_0x20"]["bytes_hex"], "b37913f0200f08d0")

    def test_flags_are_zero_only_in_static_image(self):
        self.assertEqual(self.data["gate_bytes"]["state_object_initial_image"]["bytes_hex"],
                         "0000000000000000")
        self.assertIn("do not establish runtime state",
                      self.data["scope_limit"])

    def test_direct_refs_are_bounded_to_dump_read_sites(self):
        self.assertEqual(len(self.data["rea_xrefs"]["flag_3"]["read_sites"]), 8)
        self.assertEqual(len(self.data["rea_xrefs"]["flag_6"]["read_sites"]), 8)
        self.assertIn("No writer is proven", self.data["scope_limit"])


if __name__ == "__main__":
    unittest.main()
