import json
import struct
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JSON = ROOT / "analysis/s324_columns_audit/columns_audit.json"
MATRIX = ROOT / "analysis/s321_matrix_rows/matrix_rows.json"
BASE = 0x43541000
A7S = ROOT / ("firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/"
              "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin")
A6000 = ROOT / ("firmware/extracted/fw321/firmware.tar_unpacked/"
                "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin")


class ColumnsAudit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d = json.loads(JSON.read_text())
        cls.m = json.loads(MATRIX.read_text())
        cls.a7 = A7S.read_bytes()
        cls.a6 = A6000.read_bytes()

    def u32(self, addr):
        return struct.unpack_from("<I", self.a7, addr - BASE)[0]

    def u32a6(self, addr):
        return struct.unpack_from("<I", self.a6, addr - BASE)[0]

    def test_mode_array_is_u32_not_bytes(self):
        ma = self.d["mode_array"]
        self.assertEqual(ma["kind"], "u32[34]")
        codes = [self.u32(0x43FEE370 + 4 * i) for i in range(34)]
        self.assertEqual(codes, [int(c, 16) for c in ma["codes"]])
        self.assertTrue(all(c < 0x100 for c in codes))
        # 34 u32 = 136 B y termina justo en L95
        self.assertEqual(0x43FEE370 + 136, 0x43FEE3F8)
        self.assertNotEqual(self.u32(0x43FEE3F8), 0)

    def test_s204_positions_are_mode_array_indices(self):
        ma = self.d["mode_array"]
        self.assertEqual((ma["index_of_0x4c"], ma["index_of_0x4d"]), (27, 28))
        self.assertEqual((ma["index_of_0x4e"], ma["index_of_0x4f"]), (29, 30))
        codes = [self.u32(0x43FEE370 + 4 * i) for i in range(34)]
        self.assertEqual(codes[29:31], [0x4E, 0x4F])
        # y no son columnas de la matriz de 16
        self.assertEqual(self.m["matrix_a7s"]["payload_bytes"], 16)
        self.assertEqual(self.m["mode_columns"]["silent_columns"],
                         {"0x4c": 1, "0x4d": 1, "0x4e": 1, "0x4f": 1})

    def test_slot_and_offset(self):
        self.assertEqual(self.u32(0x44027230), 0x43FEE370)
        self.assertEqual(self.d["mode_array"]["literal_refs"], ["lit@0x44027230"])
        self.assertEqual(0x44024540 + 0x2CF0, 0x44027230)
        self.assertIn("0x436f4468", self.d["slot"]["offset_le_sites"])

    def test_a7s_setter_slot8(self):
        self.assertEqual(self.u32(0x43FCE050 + 32), 0x436F3B45)
        ins = {i["address"]: i["insn"] for i in
               self.d["setter_a7s"]["instructions"]}
        self.assertEqual(ins["0x436f3b54"], "cmp r3, #0x51")
        self.assertEqual(ins["0x436f3b5a"], "str.w r3, [r0, #0x1ac]")
        self.assertEqual(ins["0x436f3b62"], "strb.w r1, [r0, #0x2b0]")

    def test_a6000_setter_rejects_silent_codes(self):
        self.assertEqual(self.u32a6(0x43FCC090 + 32), 0x436D6B51)
        ins = {i["address"]: i["insn"] for i in
               self.d["setter_a6000"]["instructions"]}
        self.assertEqual(ins["0x436d6b62"], "cmp r2, #0x47")
        self.assertEqual(ins["0x436d6b70"], "strb.w r1, [r0, #0x266]")
        # 0x4e > 0x47 y 0x4f > 0x47: rechazados por el limite
        self.assertGreater(0x4E, 0x47)
        self.assertGreater(0x4F, 0x47)

    def test_no_column_pair_differs_in_one_register(self):
        rows = self.m["matrix_a7s"]["rows_detail"]
        vals = [[int(r["payload_hex"][2 * i:2 * i + 2], 16) for i in range(16)]
                for r in rows]
        import itertools
        counts = [sum(1 for i in range(69) if vals[i][a] != vals[i][b])
                  for a, b in itertools.combinations(range(15), 2)]
        self.assertEqual(len(counts), 105)
        self.assertEqual(min(counts), 2)
        self.assertNotIn(1, counts)
        self.assertFalse(
            self.d["column_claim_s204"]["reproducible_with_this_matrix"])

    def test_second_matrix_gate_is_the_sub_field(self):
        gate = self.d["setter_a7s"]["sub_field"]
        self.assertEqual(gate, "+0x2b0")
        self.assertEqual(self.d["consumer_a7s"]["gate_field"]
                         if "consumer_a7s" in self.d else "+0x2b0", "+0x2b0")
        self.assertEqual(self.d["setter_a6000"]["sub_field"], "+0x266")
        self.assertEqual(self.m["consumer_a6000"]["gate_field"], "+0x266")

    def test_verdicts(self):
        v = self.d["verdict"]
        self.assertIn("NO_VERIFICADO", v["s204_34_columns"])
        self.assertIn("VERIFICADO", v["a6000_rejects_0x4e_0x4f"])
        self.assertIn("A=NO", v["s51"])


if __name__ == "__main__":
    unittest.main()
