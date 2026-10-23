import json
import struct
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JSON = ROOT / "analysis/s325_position_map/position_map.json"
MATRIX = ROOT / "analysis/s321_matrix_rows/matrix_rows.json"
BASE = 0x43541000
A7S = ROOT / ("firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/"
              "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin")


class PositionMap(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d = json.loads(JSON.read_text())
        cls.m = json.loads(MATRIX.read_text())
        cls.a7 = A7S.read_bytes()

    def u32(self, addr):
        return struct.unpack_from("<I", self.a7, addr - BASE)[0]

    def test_helper_returns_index(self):
        ins = {i["address"]: i["insn"] for i in self.d["helper"]["instructions"]}
        self.assertEqual(ins["0x43ada28a"], "ldr r4, [r2], #4")
        self.assertEqual(ins["0x43ada292"], "uxtb r0, r0")
        self.assertEqual(ins["0x43ada296"], "adds r0, #1")
        self.assertEqual(ins["0x43ada29c"], "movs r0, #0xff")

    def test_call_chain_passes_index_to_slot40(self):
        ins = {i["address"]: i["insn"] for i in self.d["call_chain"]["instructions"]}
        self.assertEqual(ins["0x436f3bbe"], "movs r3, #0x22")
        self.assertEqual(ins["0x436f3bc0"], "bl #0x43ada284")
        self.assertEqual(ins["0x436f3bc6"], "mov r1, r0")
        self.assertEqual(ins["0x436f3bd2"], "ldr.w r3, [r3, #0xa0]")
        codes = [self.u32(0x43FEE370 + 4 * i) for i in range(34)]
        self.assertEqual(codes.index(0x44), 25)

    def test_map_has_34_entries_all_within_15_columns(self):
        map34 = list(self.a7[0x43C9C5B5 - BASE:0x43C9C5B5 - BASE + 34])
        self.assertEqual(map34, self.d["map"]["values"])
        self.assertEqual(max(map34), 14)
        tail = list(self.a7[0x43C9C5B5 + 34 - BASE:0x43C9C5B5 + 82 - BASE])
        self.assertEqual(tail[:10], tail[10:20])
        self.assertEqual(len(tail), 48)

    def test_silent_columns_are_12_and_13(self):
        sil = self.d["silent"]
        self.assertEqual(sil["0x4e"]["position"], 29)
        self.assertEqual(sil["0x4e"]["column"], 12)
        self.assertEqual(sil["0x4f"]["position"], 30)
        self.assertEqual(sil["0x4f"]["column"], 13)
        self.assertEqual(sil["0x4c"]["column"], 5)
        self.assertEqual(sil["0x4d"]["column"], 5)

    def test_matrix_distinguishes_silent(self):
        rows = self.m["matrix_a7s"]["rows_detail"]
        regs = [r["reg"] for r in rows]
        vals = [[int(r["payload_hex"][2 * i:2 * i + 2], 16) for i in range(16)]
                for r in rows]
        d4e = [regs[i] for i in range(69) if vals[i][12] != vals[i][5]]
        d4f = [regs[i] for i in range(69) if vals[i][13] != vals[i][5]]
        self.assertEqual(len(d4e), 14)
        self.assertEqual(len(d4f), 11)
        self.assertIn(0x0C, d4e)
        self.assertIn(0x0A, d4e)
        self.assertIn(0x0C, d4f)
        self.assertIn(0x0A, d4f)

    def test_0x50_0x51_share_silent_columns(self):
        self.assertEqual(self.d["pairs_share_column"]["col12_positions"], [29, 31])
        self.assertEqual(self.d["pairs_share_column"]["col13_positions"], [30, 32])
        codes = [self.u32(0x43FEE370 + 4 * i) for i in range(34)]
        self.assertEqual((codes[31], codes[32]), (0x50, 0x51))

    def test_corrections_are_declared(self):
        text = json.dumps(self.d["corrections"])
        self.assertIn("posicion->columna", text)
        self.assertIn("matriz SI distingue", text)
        self.assertIn("S321", text)
        self.assertTrue(any("S51" in x for x in self.d["scope_limit"]))


if __name__ == "__main__":
    unittest.main()
