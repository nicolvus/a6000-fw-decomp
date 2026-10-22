import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "analysis/s146_rea_seed_capability/verify_offsets.py"
spec = importlib.util.spec_from_file_location("s146_verify", SCRIPT)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)


class ReaSeedCapability(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
        cls.data = json.loads(module.OUT.read_text())

    def test_candidate_addresses_use_correct_file_offsets(self):
        maps = {item["address"]: item["file_offset"]
                for item in self.data["address_mappings"]}
        self.assertEqual(maps["0x43843a44"], "0x302a44")
        self.assertEqual(maps["0x437b617e"], "0x27517e")

    def test_off_by_0x1000_candidate_is_distinct(self):
        wrong = next(item for item in self.data["address_mappings"]
                     if item["address"] == "0x437b717e")
        self.assertEqual(wrong["file_offset"], "0x27617e")
        self.assertNotEqual(wrong["address"], "0x437b617e")

    def test_rea_selector_limit_is_explicit(self):
        self.assertIn("does not create or seed",
                      self.data["rea_tool_result"]["procedure_pseudo_code_selector"])
        self.assertEqual(len(self.data["evidence_ids"]), 5)


if __name__ == "__main__":
    unittest.main()
