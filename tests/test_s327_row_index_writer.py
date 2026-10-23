import json
import struct
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JSON = ROOT / "analysis/s327_row_index_writer/row_index_writer.json"
BASE = 0x43541000
A7S = ROOT / ("firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/"
              "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin")


class RowIndexWriter(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d = json.loads(JSON.read_text())
        cls.a7 = A7S.read_bytes()

    def test_only_two_writers(self):
        self.assertEqual([s["address"] for s in self.d["stores"]],
                         ["0x436f2d74", "0x436f40fe"])
        self.assertEqual(self.d["store_count"], 2)

    def test_parametric_ctor_stores_its_parameter(self):
        entry = {i["address"]: i["insn"] for i in self.d["parametric_ctor"]["entry"]}
        tail = {i["address"]: i["insn"] for i in self.d["parametric_ctor"]["tail"]}
        self.assertEqual(entry["0x436f3fc8"], "mov r6, r1")
        self.assertEqual(tail["0x436f40fe"], "str.w r6, [r4, #0x2b4]")
        # bytes del store
        h1, h2 = struct.unpack_from("<HH", self.a7, 0x436F40FE - BASE)
        self.assertEqual((h1, h2), (0xF8C4, 0x62B4))

    def test_base_constructor_zeroes_the_field(self):
        base = {i["address"]: i["insn"] for i in self.d["base_ctor_zero_init"]["instructions"]}
        self.assertEqual(base["0x436f2d62"], "movs r3, #0")
        self.assertEqual(base["0x436f2d74"], "str.w r3, [r4, #0x2b4]")

    def test_single_caller_passes_zero(self):
        call = {i["address"]: i["insn"] for i in self.d["caller"]["instructions"]}
        self.assertEqual(call["0x436f2a7e"], "movs r1, #0")
        self.assertEqual(call["0x436f2a8a"], "bl #0x436f3fc0")
        self.assertEqual(self.d["caller"]["idx_value"], 0)

    def test_nine_field_readers(self):
        self.assertEqual(len(self.d["loads"]), 9)
        for x in self.d["loads"]:
            self.assertTrue(x["insn"].startswith("ldr"))
            self.assertNotIn("[pc", x["insn"])

    def test_verdict_unsupports_s326_mapping(self):
        v = self.d["verdict"]
        self.assertEqual(v["rows_reached"], [0])
        self.assertFalse(v["silent_rows_29_30_reachable"])
        self.assertIn("NO_VERIFICADO", v["s326_row_mode_mapping"])


if __name__ == "__main__":
    unittest.main()
