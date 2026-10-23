"""S337 - tests del carril B: 0x43fef404 no es una tabla de tiempos."""
import json
import struct
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JSON = ROOT / "analysis/s337_fef404_table/fef404_table.json"
VERIFY = ROOT / "analysis/s337_fef404_table/verify_fef404_table.py"
BASE = 0x43541000
A7S = ROOT / ("firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/"
              "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin")


class Fef404Table(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d = json.loads(JSON.read_text())
        cls.a7 = A7S.read_bytes()

    def u16(self, addr):
        return struct.unpack_from("<H", self.a7, addr - BASE)[0]

    def test_shape(self):
        t = self.d["table"]
        self.assertEqual(t["address"], "0x43fef404")
        self.assertEqual(t["entry_size"], 4)
        self.assertEqual(t["entries"], 69)
        self.assertEqual(t["second_field"], "0x000d")
        self.assertTrue(t["all_second_equal"])

    def test_entries_recomputed(self):
        base = 0x43FEF404
        codes = [self.u16(base + 4 * i) for i in range(69)]
        self.assertEqual(codes, self.d["table"]["codes"])
        self.assertTrue(all(self.u16(base + 4 * i + 2) == 0x000D for i in range(69)))
        self.assertEqual(min(codes), 0x01)

    def test_not_timing(self):
        v = self.d["verdicts"]
        self.assertFalse(v["is_u16_69_timing_table"])
        self.assertEqual(v["entry_shape"], "{u16 codigo, u16 0x000d}")
        self.assertEqual(v["s329_candidate"], "falso positivo (ventana cruzada)")

    def test_no_static_consumer(self):
        self.assertEqual(self.d["literal_references"], [])
        self.assertFalse(self.d["verdicts"]["static_consumer"])

    def test_prefix(self):
        p = self.d["prefix_43f9c622"]
        self.assertEqual(p["count"], 169)
        self.assertEqual(struct.unpack_from("<I", self.a7,
                                            0x43FEF404 - BASE - 4)[0], 0x43F9C622)

    def test_limits(self):
        text = " ".join(self.d["limits"])
        self.assertIn("S51", text)
        self.assertIn("indirecto", text)

    def test_verify_script_passes(self):
        res = subprocess.run([sys.executable, str(VERIFY)], capture_output=True,
                             text=True, check=False)
        self.assertEqual(res.returncode, 0, res.stdout + res.stderr)
        self.assertIn("0 fallos", res.stdout)


if __name__ == "__main__":
    unittest.main()
