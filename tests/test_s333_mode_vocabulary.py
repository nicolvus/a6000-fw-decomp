"""S333 - tests del carril B: vocabulario de modos y columnas de matriz."""
import json
import struct
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JSON = ROOT / "analysis/s333_mode_vocabulary/mode_vocabulary.json"
VERIFY = ROOT / "analysis/s333_mode_vocabulary/verify_mode_vocabulary.py"
BASE = 0x43541000
A6000 = ROOT / ("firmware/extracted/fw321/firmware.tar_unpacked/"
                "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin")
A7S = ROOT / ("firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/"
              "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin")


class ModeVocabulary(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d = json.loads(JSON.read_text())
        cls.a6 = A6000.read_bytes()
        cls.a7 = A7S.read_bytes()

    def u32(self, blob, addr):
        return struct.unpack_from("<I", blob, addr - BASE)[0]

    def test_a6000_matrix(self):
        slot = self.d["a6000"]["matrix_slot"]
        self.assertEqual(slot, "0x44022f8c")
        base = self.u32(self.a6, int(slot, 16))
        self.assertEqual(f"0x{base:08x}", self.d["a6000"]["matrix"])
        self.assertEqual(self.d["a6000"]["rows"], 59)
        term = int(self.d["a6000"]["terminator"], 16)
        self.assertEqual(self.u32(self.a6, term), 0)
        self.assertNotEqual(self.u32(self.a6, term - 0x14), 0)

    def test_a6000_codes(self):
        codes = [int(c, 16) for c in self.d["a6000"]["codes"]]
        self.assertEqual(len(codes), 13)
        self.assertEqual(codes, [0x0B, 0x01, 0x05, 0x10, 0x07, 0x12, 0x03,
                                 0x0A, 0x0F, 0x18, 0x1A, 0x19, 0x2F])
        base = 0x43FEA070
        self.assertEqual([self.u32(self.a6, base + 4 * i) for i in range(13)], codes)

    def test_a6000_seven_distinct_vectors(self):
        c = self.d["a6000"]["columns"]
        self.assertEqual(c["distinct_vectors"], 7)
        self.assertEqual(c["aliases"],
                         [["0x05", "0x07", "0x10", "0x18", "0x19", "0x1a"],
                          ["0x0b", "0x2f"]])
        # la columna es la posicion del modo (sin mapa)
        self.assertEqual(c["columns"]["0x0b"], 0)
        self.assertEqual(c["columns"]["0x2f"], 12)

    def test_a7s_fifteen_distinct(self):
        c = self.d["a7s"]["columns"]
        self.assertEqual(self.d["a7s"]["rows"], 69)
        self.assertEqual(c["distinct_vectors"], 15)
        self.assertEqual(len(c["aliases"]), 12)
        self.assertIn(["0x4e", "0x50"], c["aliases"])
        self.assertEqual(len(self.d["a7s"]["position_map"]), 34)

    def test_vocabulary(self):
        v = self.d["vocabulary"]
        self.assertEqual(v["counts"], {"a6000": 13, "a7s": 34, "shared": 12})
        self.assertEqual(v["a6000_only"], ["0x2f"])
        self.assertIn("0x4e", v["a7s_only"])
        self.assertIn("0x4f", v["a7s_only"])
        self.assertEqual(len(v["a7s_only"]), 22)

    def test_silent_absent_from_a6000(self):
        self.assertFalse(self.d["verdicts"]["a6000_has_silent_codes"])
        self.assertEqual(self.d["verdicts"]["silent_codes_a7s_only"],
                         ["0x4c", "0x4d", "0x4e", "0x4f", "0x50", "0x51"])

    def test_coarse_vocabulary(self):
        v = self.d["verdicts"]
        self.assertTrue(v["a6000_vocabulary_is_coarse"])
        self.assertEqual(v["a6000_alias_groups"], 2)
        self.assertEqual(v["a7s_alias_groups"], 12)
        self.assertEqual(v["a7s_silent_aliases"]["0x4e"], ["0x4e", "0x50"])
        self.assertLess(v["a6000_distinct_vectors"],
                        self.d["vocabulary"]["counts"]["a6000"])

    def test_limits(self):
        text = " ".join(self.d["limits"])
        self.assertIn("S51", text)
        self.assertIn("registro", text)

    def test_verify_script_passes(self):
        res = subprocess.run([sys.executable, str(VERIFY)], capture_output=True,
                             text=True, check=False)
        self.assertEqual(res.returncode, 0, res.stdout + res.stderr)
        self.assertIn("0 fallos", res.stdout)


if __name__ == "__main__":
    unittest.main()
