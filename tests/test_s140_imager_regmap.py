import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "analysis/s140_imager_regmap/extract_regmap.py"
spec = importlib.util.spec_from_file_location("s140_extract", SCRIPT)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)


class ImagerRegmap(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
        cls.result = json.loads(module.OUT.read_text())

    def test_pointer_count_and_terminator(self):
        table = self.result["pointer_table"]
        self.assertEqual(table["pointer_count"], 119)
        self.assertEqual(table["terminator_address"], "0x43fe9b38")
        self.assertEqual(table["records"][1]["address"], "0x4401ca2c")

    def test_records_decode_as_little_endian_id_and_two_bytes(self):
        records = self.result["pointer_table"]["records"]
        self.assertEqual(len(records), 119)
        for record in records:
            raw = bytes.fromhex(record["raw_hex"])
            self.assertEqual(record["id_u16_le"], int.from_bytes(raw[:2], "little"))
            self.assertEqual(record["value_plus_2"], raw[2])
            self.assertEqual(record["byte_plus_3"], raw[3])

    def test_banks_are_zero_initialized_image_ranges(self):
        banks = self.result["banks"]
        self.assertEqual([bank["length"] for bank in banks], [0x148, 0x100])
        self.assertTrue(all(bank["all_zero_in_firmware_image"] for bank in banks))
        self.assertEqual(len(banks[0]["rows_16_bytes"]), 0x148 // 16)
        self.assertEqual(len(bytes.fromhex(banks[0]["trailing_bytes_hex"])), 8)


if __name__ == "__main__":
    unittest.main()
