import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "analysis/s147_imager_g_rows/verify_g_rows.py"
spec = importlib.util.spec_from_file_location("s147_verify", SCRIPT)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)


class ImagerGRows(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
        cls.data = json.loads(module.OUT.read_text())

    def test_caller_forms_G_plus_224_and_calls_builder(self):
        region = next(r for r in self.data["regions"] if r["address"] == "0x437b5f00")
        text = [i["text"] for i in region["thumb_instructions"]]
        self.assertIn("add.w r1, r6, #0x224", text)
        self.assertIn("bl #0x4383bf2c", text)

    def test_builder_calls_four_row_writer(self):
        region = next(r for r in self.data["regions"] if r["address"] == "0x4383bf2c")
        text = [i["text"] for i in region["thumb_instructions"]]
        self.assertIn("bl #0x4383c9dc", text)
        rows = self.data["row_layout_observed"]
        self.assertEqual(rows["row_count"], 4)
        self.assertEqual(rows["row_stride"], "0x10")

    def test_other_xref_sites_are_not_mistaken_for_row_writer(self):
        reader = next(r for r in self.data["regions"] if r["address"] == "0x43836a00")
        lines = [i["text"] for i in reader["thumb_instructions"]]
        self.assertEqual(sum("ldrh.w r2, [r3, #0x224]" in line for line in lines), 2)
        self.assertIn("0x8", self.data["row_layout_observed"]["not_written_by_this_loop"])


if __name__ == "__main__":
    unittest.main()
