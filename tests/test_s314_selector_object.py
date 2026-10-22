import json
import struct
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JSON = ROOT / "analysis/s314_selector_object/selector.json"
BASE = 0x43541000
A7S = ROOT / ("firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/"
              "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin")
A6000 = ROOT / ("firmware/extracted/fw321/firmware.tar_unpacked/"
                "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin")


class SelectorObject(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d = json.loads(JSON.read_text())
        cls.a7 = A7S.read_bytes()
        cls.a6 = A6000.read_bytes()

    def u16(self, addr):
        return struct.unpack_from("<H", self.a7, addr - BASE)[0]

    def test_call_site_is_selector_not_vtable(self):
        call = self.d["call_site"]["selector_call"]
        self.assertEqual(call["address"], "0x4354908c")
        self.assertEqual(call["insn"], "bl #0x43826d58")
        self.assertEqual(self.d["call_site"]["selector_callers"],
                         ["0x4354908c", "0x43826df2"])

    def test_no_r0_at_0x43549084(self):
        # Es ldr.w r1,[r3,#0x21c], no una carga de r0.
        self.assertEqual(self.u16(0x43549084), 0xF8D3)
        self.assertEqual(self.d["call_site"]["provenance"]["r1"][:19],
                         "[[0x43ea70a6] + 0x2")

    def test_ctx_address(self):
        self.assertEqual(self.d["call_site"]["ctx_getter"]["ctx"], "0x43ea709e")

    def test_slot64_thunk_is_0x43ad96f8(self):
        self.assertEqual(self.d["vtable_thunks"]["slot_0x64_thunk"]["entry"],
                         "0x43ad96f8")
        self.assertEqual(self.u16(0x43AD96FE), 0x6E5B)  # ldr r3,[r3,#0x64]
        self.assertIn("NO usa vtable+0x64",
                      self.d["vtable_thunks"]["wrapper_0x43ad9704"]["semantics"])
        self.assertEqual(self.d["vtable_thunks"]["wrapper_0x43ad9704"]["callers"],
                         ["0x435490c4", "0x43826e3e"])

    def test_selector_truth_table(self):
        rows = self.d["selector"]["truth_table"]
        self.assertEqual(len(rows), 9)
        self.assertEqual([r["result"] for r in rows if r["c"] == "2"],
                         ["0x4e", "0x4f", "0x4e + log"])
        self.assertEqual(self.u16(0x43826D7C), 0x204E)
        self.assertEqual(self.u16(0x43826DA6), 0x204F)

    def test_register_list_is_95_not_19(self):
        reg = self.d["register_list"]
        self.assertEqual(reg["count"], 95)
        self.assertEqual(reg["terminator"], "0x43fee574")
        self.assertEqual(reg["record_size"], 6)
        self.assertEqual(reg["dev_counts"], {"129": 94, "131": 1})
        self.assertEqual(reg["records"][94]["bytes"], "830017004a00")
        self.assertNotEqual(reg["count"], 19)

    def test_register_consumer_reads_five_bytes(self):
        self.assertEqual(self.u16(0x436F4526), 0x7819)  # ldrb r1,[r3]
        self.assertEqual(self.u16(0x436F452A), 0x885A)  # ldrh r2,[r3,#2]
        self.assertEqual(self.u16(0x436F452C), 0x791B)  # ldrb r3,[r3,#4]

    def test_descriptor_rows_are_68(self):
        rows = self.d["descriptor_rows"]
        self.assertEqual(rows["count"], 68)
        self.assertEqual(rows["row_size"], 0x14)
        self.assertEqual(rows["end"], "0x43feeafc")

    def test_a6000_lacks_the_pair_and_the_table(self):
        self.assertEqual(self.d["a6000"]["pair_0x21c_0x220_occurrences"], 0)
        self.assertNotEqual(
            self.a6[0x43549084 - BASE:0x43549084 - BASE + 4],
            self.a7[0x43549084 - BASE:0x43549084 - BASE + 4])
        self.assertEqual(struct.unpack_from("<I", self.a6, 0x43FEE41C - BASE)[0], 0)

    def test_limits_are_explicit(self):
        text = " ".join(self.d["limits"])
        self.assertIn("NO_VERIFICADO", text)
        self.assertIn("no se ejecuto firmware", text.lower())


if __name__ == "__main__":
    unittest.main()
