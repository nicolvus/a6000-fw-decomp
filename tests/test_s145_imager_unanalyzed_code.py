import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "analysis/s145_imager_unanalyzed_code/verify_code_gap.py"
spec = importlib.util.spec_from_file_location("s145_verify", SCRIPT)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)


class UnanalyzedCodeGap(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
        cls.data = json.loads(module.OUT.read_text())

    def test_candidate_caller_prologue_bytes(self):
        r = self.data["regions"][0]
        self.assertEqual(r["address"], "0x437b617e")
        self.assertEqual(r["bytes_hex"][:24], "2de9f34705463d4c8a465b78")

    def test_direct_thumb_call_targets_staging_address(self):
        lines = [i["text"] for i in self.data["regions"][0]["thumb_instructions"]]
        self.assertIn("bl #0x43843a44", lines)

    def test_observed_setter_ends_before_candidate_code(self):
        r = self.data["regions"][1]
        self.assertEqual(r["bytes_hex"], "014b7b4418707047cb7a75002de9f04f")
        self.assertEqual(self.data["regions"][2]["address"], "0x43843a44")


if __name__ == "__main__":
    unittest.main()
