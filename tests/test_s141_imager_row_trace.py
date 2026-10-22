import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "analysis/s141_imager_row_trace/verify_instructions.py"
spec = importlib.util.spec_from_file_location("s141_verify", SCRIPT)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)


class RowTrace(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
        cls.result = json.loads(module.OUT.read_text())

    def test_known_thumb_bytes(self):
        row_copy = self.result["regions"][0]
        self.assertEqual(row_copy["address"], "0x43b0893c")
        self.assertEqual(row_copy["bytes_hex"], "10b500f1c404037800eb031304330fcb84e80f0010bd")

    def test_row_selector_and_16_byte_copy_instructions(self):
        lines = [item["text"] for item in self.result["regions"][0]["thumb_instructions"]]
        self.assertTrue(any("ldrb" in line and "[r0]" in line for line in lines))
        self.assertTrue(any("lsl #4" in line for line in lines))
        self.assertTrue(any(line.startswith("ldm") for line in lines))
        self.assertTrue(any(line.startswith("stm") for line in lines))

    def test_exposure_builder_bytes_are_extracted_at_va_offset(self):
        builder = self.result["regions"][1]
        self.assertEqual(builder["address"], "0x43849fb8")
        self.assertEqual(builder["file_offset"], hex(0x43849FB8 - 0x43541000))
        self.assertEqual(len(bytes.fromhex(builder["bytes_hex"])), 0xA0)


if __name__ == "__main__":
    unittest.main()
