import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "analysis/s149_imager_row_helpers/verify_helper_stores.py"
spec = importlib.util.spec_from_file_location("s149_verify", SCRIPT)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)


class ImagerRowHelpers(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
        cls.data = json.loads(module.OUT.read_text())

    def test_writer_initializes_four_rows_and_loops_by_16(self):
        init = self.data["regions"][0]
        tail = self.data["regions"][1]
        self.assertEqual(init["bytes_hex"][4:12], "04200490")
        tail_text = [i["text"] for i in tail["thumb_instructions"]]
        self.assertIn("adds r4, #0x10", tail_text)
        self.assertTrue(any(line.startswith("bne.w") for line in tail_text))
        self.assertEqual(self.data["loop"]["count_initial"], 4)

    def test_row_gap_is_only_unwritten_in_scoped_writer(self):
        self.assertEqual(self.data["loop"]["unwritten_by_row_writer"], ["0x8", "0x9"])
        self.assertEqual(self.data["loop"]["row_bases_relative_to_G_plus_0x224"],
                         ["0x2c", "0x3c", "0x4c", "0x5c"])

    def test_helper_dossiers_are_retained_and_scoped(self):
        helpers = self.data["rea_evidence_ids"]["four_helper_dossiers"]
        self.assertEqual(len(helpers), 4)
        self.assertEqual(self.data["firmware_sha256"],
                         "b60c845ccb90c0ff86b7f62f1f3f2ecda714aa20c37805959ebee2b429e56bb9")


if __name__ == "__main__":
    unittest.main()
