import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "analysis/s142_imager_s_init/verify_s_accesses.py"
spec = importlib.util.spec_from_file_location("s142_verify", SCRIPT)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)


class ImagerSDirectAccesses(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
        cls.data = json.loads(module.OUT.read_text())

    def test_got_load_and_zero_fill_size_bytes(self):
        regions = self.data["regions"]
        self.assertEqual(regions[0]["bytes_hex"], "0021a0584ff4a47210f2a4e9")
        self.assertEqual(regions[1]["bytes_hex"], "e058")
        self.assertTrue(any("#0x148" in x["text"] for x in regions[0]["instructions"]))

    def test_halfword_reader_thunk(self):
        thunk = self.data["regions"][2]
        self.assertEqual(thunk["bytes_hex"], "b0f8da0033f574bf")
        self.assertTrue(any("#0xda" in x["text"] for x in thunk["instructions"]))

    def test_same_firmware_identity(self):
        self.assertEqual(self.data["firmware_sha256"],
                         "b60c845ccb90c0ff86b7f62f1f3f2ecda714aa20c37805959ebee2b429e56bb9")


if __name__ == "__main__":
    unittest.main()
