import json
import struct
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JSON = ROOT / "analysis/s318_ctor_mode/ctor_mode.json"
BASE = 0x43541000
A7S = ROOT / ("firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/"
              "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin")


class CtorMode(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d = json.loads(JSON.read_text())
        cls.a7 = A7S.read_bytes()

    def u16(self, addr):
        return struct.unpack_from("<H", self.a7, addr - BASE)[0]

    def u32(self, addr):
        return struct.unpack_from("<I", self.a7, addr - BASE)[0]

    def test_constructor(self):
        self.assertEqual(self.d["constructor"]["entry"], "0x436f3fc0")
        self.assertEqual(self.d["constructor"]["vptr"], "0x43fce050")
        self.assertEqual(self.u16(0x436F3FE4), 0xF853)  # ldr.w r3,[r3,r6,lsl#2]

    def test_table_base(self):
        self.assertEqual(self.d["constructor"]["table"], "0x43bbe1cc")
        self.assertEqual(self.u32(0x43BBE1CC), 1)
        self.assertEqual(self.u32(0x43BBE1D0), 2)
        self.assertEqual(self.u32(0x43BBE1E8), 0x01EC0000)

    def test_mapper(self):
        self.assertEqual(self.d["mapper"]["mapping"][0]["obj8"], "0x10")
        self.assertEqual(self.d["mapper"]["mapping"][1]["obj8"], "0x40")
        self.assertEqual(self.u16(0x43AD917C), 0x2310)
        self.assertEqual(self.u16(0x43AD9180), 0x2340)
        self.assertEqual(self.u16(0x43AD9184), 0x2301)

    def test_only_caller_uses_index_zero(self):
        self.assertEqual(self.d["constructor"]["callers"], ["0x436f2a8a"])
        self.assertEqual(self.u16(0x436F2A7E), 0x2100)  # movs r1,#0

    def test_a7s_only(self):
        self.assertEqual(self.d["a6000_ctor_hits"], 0)

    def test_limits(self):
        text = " ".join(self.d["limits"])
        self.assertIn("NO_VERIFICADOS", text)
        self.assertIn("S51", text)


if __name__ == "__main__":
    unittest.main()
