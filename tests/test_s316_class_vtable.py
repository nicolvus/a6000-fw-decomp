import json
import struct
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JSON = ROOT / "analysis/s316_class_vtable/class.json"
BASE = 0x43541000
A7S = ROOT / ("firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/"
              "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin")
A6000 = ROOT / ("firmware/extracted/fw321/firmware.tar_unpacked/"
                "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin")


class ClassVtable(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d = json.loads(JSON.read_text())
        cls.a7 = A7S.read_bytes()
        cls.a6 = A6000.read_bytes()

    def u32(self, addr):
        return struct.unpack_from("<I", self.a7, addr - BASE)[0]

    def test_constructor_sets_vptr(self):
        ctor = self.d["constructor"]
        self.assertEqual(ctor["got"]["slot"], "0x4402ac80")
        self.assertEqual(ctor["got"]["value"], "0x43fce048")
        self.assertEqual(ctor["vptr_stored"], "0x43fce050")
        self.assertEqual(self.u32(0x4402AC80), 0x43FCE048)

    def test_vtable_shape(self):
        vt = self.d["vtable"]
        self.assertEqual(vt["metadata"], "0x43fce048")
        self.assertEqual(vt["offset_to_top"], 0)
        self.assertEqual(vt["typeinfo"], "0x43feeb20")
        self.assertEqual(vt["count"], 45)
        self.assertEqual(vt["end"], "0x43fce104")
        self.assertEqual(self.u32(0x43FCE104), 0)

    def test_list_methods_are_slots_38_and_44(self):
        self.assertEqual(self.d["method_slots"]["0x436f5a14"]["vtable_entry"]["slot"], "0x38")
        self.assertEqual(self.d["method_slots"]["0x436f53f4"]["vtable_entry"]["slot"], "0x44")
        self.assertEqual(self.u32(0x43FCE088) & ~1, 0x436F5A14)
        self.assertEqual(self.u32(0x43FCE094) & ~1, 0x436F53F4)

    def test_wrapper_is_slot_04(self):
        self.assertEqual(self.d["method_slots"]["0x43ad9840"]["vtable_entry"]["slot"], "0x04")
        self.assertEqual(self.u32(0x43FCE054) & ~1, 0x43AD9840)

    def test_class_is_a7s_only(self):
        for addr, n in [(0x436F27B4, 32), (0x43AD9840, 16),
                        (0x436F5A14, 32), (0x436F53F4, 24)]:
            sig = self.a7[addr - BASE:addr - BASE + n]
            self.assertEqual(self.a6.count(sig), 0)

    def test_fields_and_limits(self):
        self.assertIn("obj+0x2b4", self.d["fields"])
        text = " ".join(self.d["limits"])
        self.assertIn("NO_VERIFICADO", text)
        self.assertIn("S51 sin cambios", text)


if __name__ == "__main__":
    unittest.main()
