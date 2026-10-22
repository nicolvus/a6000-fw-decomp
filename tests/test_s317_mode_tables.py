import json
import struct
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JSON = ROOT / "analysis/s317_mode_tables/mode_tables.json"
BASE = 0x43541000
A7S = ROOT / ("firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/"
              "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin")


class ModeTables(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d = json.loads(JSON.read_text())
        cls.a7 = A7S.read_bytes()

    def u16(self, addr):
        return struct.unpack_from("<H", self.a7, addr - BASE)[0]

    def test_entry_and_stride(self):
        self.assertEqual(self.u16(0x436F61A4), 0x221C)  # movs r2,#0x1c
        self.assertEqual(self.u16(0x436F61A6), 0x4355)  # muls r5,r2,r5
        self.assertEqual(self.d["entry"]["stride"], "0x1c")

    def test_three_tables(self):
        self.assertEqual(self.d["tables"]["T1"]["computed"], 0x43BBEB70)
        self.assertEqual(self.d["tables"]["T2"]["computed"], 0x43BBF2EC)
        self.assertEqual(self.d["tables"]["T3"]["computed"], 0x43BBEF34)

    def test_spacing_is_34_rows(self):
        self.assertEqual(self.d["spacing"]["T3_to_T2_rows"], 34)
        self.assertEqual(0x43BBF2EC - 0x43BBEF34, 34 * 0x1C)
        self.assertEqual(self.d["spacing"]["T1_to_T3"], "0x3c4")

    def test_fields_read(self):
        self.assertEqual(self.d["entry"]["fields"], {"u32": "+0x14", "u16": "+0x18"})
        self.assertEqual(self.u16(0x436F61AE), 0x8B19)  # ldrh r1,[r3,#0x18]
        self.assertEqual(self.u16(0x436F61B0), 0x695A)  # ldr r2,[r3,#0x14]

    def test_entry_is_a7s_only(self):
        self.assertEqual(self.d["a6000_entry_hits"], 0)

    def test_limits(self):
        text = " ".join(self.d["limits"])
        self.assertIn("REA/Ghidra", text)
        self.assertIn("REA/Ghidra", text)


if __name__ == "__main__":
    unittest.main()
