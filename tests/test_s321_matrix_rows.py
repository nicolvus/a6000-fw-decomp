import json
import struct
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JSON = ROOT / "analysis/s321_matrix_rows/matrix_rows.json"
BASE = 0x43541000
A7S = ROOT / ("firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/"
              "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin")
A6000 = ROOT / ("firmware/extracted/fw321/firmware.tar_unpacked/"
                "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin")


class MatrixRows(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d = json.loads(JSON.read_text())
        cls.a7 = A7S.read_bytes()
        cls.a6 = A6000.read_bytes()

    def u16(self, addr):
        return struct.unpack_from("<H", self.a7, addr - BASE)[0]

    def u32(self, addr):
        return struct.unpack_from("<I", self.a7, addr - BASE)[0]

    def u32a6(self, addr):
        return struct.unpack_from("<I", self.a6, addr - BASE)[0]

    def test_the_68_rows_are_rows_1_to_68(self):
        m = self.d["matrix_a7s"]
        self.assertEqual(m["base"], "0x43fee598")
        self.assertEqual(m["rows"], 69)
        self.assertEqual(m["terminator"], "0x43feeafc")
        q = m["queue_base_0x43fee5ac"]
        self.assertEqual(q["addr"], "0x43fee5ac")
        self.assertEqual(q["is_row_index"], 1)
        self.assertEqual(q["rows_from_there"], 68)
        # el terminador coincide: 0x43fee598 + 69*0x14
        self.assertEqual(0x43FEE598 + 69 * 0x14, 0x43FEEAFC)
        self.assertEqual(q["literal_refs"], [])

    def test_table_reaches_code_only_through_its_slot(self):
        m = self.d["matrix_a7s"]
        self.assertEqual(m["literal_refs_base"], ["lit@0x44028844"])
        self.assertEqual(self.u32(0x44028844), 0x43FEE598)
        # el slot primario del accesor es exactamente esa direccion
        self.assertEqual(self.d["consumer_a7s"]["slot1"], "0x44028844")

    def test_row_destinations_are_data_bytes_of_6_byte_records(self):
        rows = self.d["matrix_a7s"]["rows_detail"]
        self.assertEqual(len(rows), 69)
        self.assertEqual(len({r["dest"] for r in rows}), 69)
        for r in rows:
            dest = int(r["dest"], 16)
            self.assertIn(self.a7[dest - 4 - BASE], (0x81, 0x83))
            self.assertEqual(self.a7[dest - 3 - BASE], 0)
            self.assertEqual(struct.unpack_from("<H", self.a7, dest - 2 - BASE)[0],
                             r["reg"])
            self.assertEqual(self.a7[dest - BASE], r["data_initial"])

    def test_record_pool_is_98_contiguous_records(self):
        pool = self.d["record_pool"]
        self.assertEqual(pool["start"], "0x44021ec2")
        self.assertEqual(pool["end"], "0x44022108")
        self.assertEqual(pool["count"], 98)
        self.assertEqual(pool["dev_histogram"], {"0x81": 97, "0x83": 1})
        self.assertEqual(pool["targeted_by_matrix"], 69)
        self.assertTrue(pool["all_targets_in_pool"])
        self.assertEqual(pool["all_targets_aligned"], [0])
        self.assertEqual(len(pool["not_targeted"]), 29)

    def test_single_0x83_record_is_targeted(self):
        dev83 = self.d["record_pool"]["dev83_records"][0]
        self.assertEqual(dev83["addr"], "0x440220d8")
        self.assertEqual((dev83["reg"], dev83["data"]), (0x17, 0x4A))
        dests = {r["dest"] for r in self.d["matrix_a7s"]["rows_detail"]}
        self.assertIn("0x440220dc", dests)

    def test_lists_partition_the_pool(self):
        rl = self.d["register_lists"]
        self.assertEqual(rl["matrix_targets_in_L95"], 66)
        self.assertEqual(rl["matrix_targets_only_in_L5"],
                         ["0x44022018", "0x44022072", "0x44022090"])
        self.assertEqual(rl["pool_not_in_L95"],
                         ["0x44021fac", "0x44022018", "0x44022072", "0x44022090"])
        self.assertEqual(rl["L1"]["ptrs"], ["0x44021fee"])

    def test_a7s_consumer_maps_mode_to_column(self):
        c = self.d["consumer_a7s"]
        self.assertEqual(c["function"], "0x436f3928")
        self.assertEqual(c["map_addr"], "0x43c9c5b5")
        self.assertEqual(c["map_len"], 82)
        self.assertEqual(c["slot1"], "0x44028844")
        self.assertEqual(c["slot1_value"], "0x43fee598")
        self.assertEqual(c["vtable_entry"], 40)
        self.assertEqual(self.u32(0x43FCE050 + 4 * 40), 0x436F3929)
        ins = {i["address"]: i["insn"] for i in c["instructions"]}
        self.assertEqual(ins["0x436f3930"], "ldrb r1, [r2, r1]")
        self.assertEqual(ins["0x436f393e"], "ldrb r5, [r5, #4]")
        self.assertEqual(ins["0x436f3940"], "strb r5, [r4]")

    def test_second_matrix_is_zero_in_the_blob(self):
        c = self.d["consumer_a7s"]
        self.assertEqual(c["slot2"], "0x44026088")
        self.assertEqual(c["slot2_value"], "0x43e8de00")
        self.assertEqual(c["slot2_bytes_nonzero"], 0)
        self.assertEqual(c["gate_field"], "+0x2b0")

    def test_a6000_has_the_same_class_but_no_map(self):
        c = self.d["consumer_a6000"]
        self.assertEqual(c["function"], "0x436d6570")
        self.assertEqual(c["vtable_entry"], 40)
        self.assertEqual(self.u32a6(0x43FCC090 + 4 * 40), 0x436D6571)
        self.assertEqual(c["slot1_value"], "0x43fe9b74")
        self.assertEqual(c["matrix_rows"], 59)
        self.assertEqual(c["gate_field"], "+0x266")
        self.assertFalse(c["has_mode_map"])
        self.assertFalse(c["map_insn_present"])
        ins = {i["address"]: i["insn"] for i in c["instructions"]}
        self.assertEqual(ins["0x436d6582"], "strb r5, [r2]")
        self.assertEqual(ins["0x436d658e"], "ldrb.w r0, [r0, #0x266]")

    def test_a6000_records_are_4_bytes(self):
        rl = self.d["consumer_a6000"]["record_layout"]
        self.assertEqual(rl["size"], 4)
        self.assertEqual(rl["alignment_mod4"], [0])
        self.assertEqual(len(rl["regs"]), 59)
        for k, reg in enumerate(rl["regs"]):
            dest = self.u32a6(0x43FE9B74 + 0x14 * k)
            self.assertEqual(dest & 3, 2)  # dest = registro + 2 (&data)
            self.assertEqual(struct.unpack_from("<H", self.a6, dest - 2 - BASE)[0], reg)

    def test_vtables_have_45_entries(self):
        vt = self.d["vtables"]
        self.assertEqual(vt["a7s"]["entries"], 45)
        self.assertEqual(vt["a6000"]["entries"], 45)
        self.assertTrue(vt["same_length"])
        self.assertEqual(self.u32(0x43FCE050 + 4 * 45), 0)
        self.assertEqual(self.u32a6(0x43FCC090 + 4 * 45), 0)

    def test_silent_modes_share_column_1(self):
        mc = self.d["mode_columns"]
        self.assertEqual(mc["silent_columns"],
                         {"0x4c": 1, "0x4d": 1, "0x4e": 1, "0x4f": 1})
        self.assertFalse(mc["any_column_exclusive_to_silent"])
        self.assertEqual(mc["max_column"], 14)
        self.assertIn("0x02", mc["silent_shares_column_with"])

    def test_column_15_unused(self):
        m = self.d["matrix_a7s"]
        self.assertTrue(m["payload_last_byte_all_zero"])
        self.assertEqual(m["payload_columns_used"], list(range(15)))
        for r in m["rows_detail"]:
            self.assertTrue(r["payload_hex"].endswith("00"))

    def test_scope_does_not_claim_runtime(self):
        limits = " ".join(self.d["scope_limit"])
        self.assertIn("NO_VERIFICADOS", limits)
        self.assertIn("S51", limits)


if __name__ == "__main__":
    unittest.main()
