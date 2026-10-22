import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIR = ROOT / "analysis/s302_drive_modes"
VERIFY = DIR / "verify_compare.py"
DATA = DIR / "compare.json"


class DriveModesCompare(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        subprocess.run([sys.executable, str(VERIFY)], cwd=ROOT, check=True)
        cls.data = json.loads(DATA.read_text())

    def test_exposure_offsets_are_shifted(self):
        a6 = self.data["exposure_offsets"]["a6000"]
        a7 = self.data["exposure_offsets"]["a7s"]
        self.assertEqual(a6["shut"], "ctx+0x1f8")
        self.assertEqual(a7["shut"], "ctx+0x200")
        self.assertEqual(a6["vdnum"], "[state+8]+0xcc")
        self.assertEqual(a7["vdnum"], "[state+8]+0xd8")
        self.assertEqual(a6["block_words"], 4)
        self.assertEqual(a7["block_words"], 3)

    def test_matrix_shapes(self):
        self.assertEqual(len(self.data["matrices"]["a6000"]["rows"]), 59)
        self.assertEqual(len(self.data["matrices"]["a7s"]["rows"]), 69)
        self.assertEqual(self.data["matrices"]["a7s"]["stride"], 20)
        self.assertEqual(len(self.data["mode_list"]["codes"]), 34)
        self.assertEqual(self.data["mode_list"]["codes"][29:31], [0x4E, 0x4F])

    def test_silent_modes_share_register_column(self):
        cols = self.data["mode_map"]["columns_for_modes"]
        self.assertEqual(cols["0x4c"], cols["0x4e"])
        self.assertEqual(cols["0x4d"], cols["0x4f"])
        self.assertEqual(cols["0x4e"], 1)

    def test_a7s_selector_codes(self):
        sel = self.data["selector_a7s"]
        self.assertEqual((sel["tipo2_sub0"], sel["tipo2_sub1"]), ("0x4e", "0x4f"))
        self.assertEqual((sel["sub0"], sel["sub1"], sel["sub2"]), ("0x0b", "0x35", "0x17"))
        self.assertEqual(sel["mode5"], "0x0c")


if __name__ == "__main__":
    unittest.main()
