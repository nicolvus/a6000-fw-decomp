"""S332 - tests del carril B: mecanismo por modo del A6000 frente al A7S."""
import json
import struct
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JSON = ROOT / "analysis/s332_a6000_tables/a6000_tables.json"
VERIFY = ROOT / "analysis/s332_a6000_tables/verify_a6000_tables.py"
BASE = 0x43541000
A6000 = ROOT / ("firmware/extracted/fw321/firmware.tar_unpacked/"
                "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin")
A7S = ROOT / ("firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/"
              "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin")


class A6000Tables(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d = json.loads(JSON.read_text())
        cls.a6 = A6000.read_bytes()
        cls.a7 = A7S.read_bytes()

    def u32(self, blob, addr):
        return struct.unpack_from("<I", blob, addr - BASE)[0]

    def u16(self, blob, addr):
        return struct.unpack_from("<H", blob, addr - BASE)[0]

    def test_mode_list_13(self):
        m = self.d["a6000"]["mode_list"]
        self.assertEqual(m["count"], 13)
        codes = [int(c, 16) for c in m["codes"]]
        self.assertEqual(codes[:4], [0x0B, 0x01, 0x05, 0x10])
        self.assertNotIn(0x4E, codes)
        self.assertNotIn(0x4F, codes)
        ptr = int(m["pointer"], 16)
        self.assertEqual([self.u32(self.a6, ptr + 4 * i) for i in range(13)], codes)

    def test_tables_shapes(self):
        t = self.d["a6000"]["tables"]
        self.assertEqual(set(t), {"TA1", "TA2"})
        self.assertEqual(t["TA1"]["dest"], "obj+0x14")
        self.assertEqual(t["TA2"]["dest"], "obj+0xa1")
        gap = int(t["TA2"]["base"], 16) - int(t["TA1"]["base"], 16)
        self.assertEqual(gap, 13 * 0x1C)        # 0x16c: 13 filas exactas
        for meta in t.values():
            self.assertEqual(len(meta["rows"]), 13)

    def test_masks_and_descriptors(self):
        cmp_ = self.d["comparison"]
        self.assertEqual(cmp_["mask_union"]["a6000"], [3840, 4095])
        self.assertEqual(cmp_["zero_masks"]["a6000"], 0)
        self.assertEqual(cmp_["descriptor_index_used"]["a6000"], [0])
        for meta in self.d["a6000"]["tables"].values():
            for row in meta["rows"]:
                self.assertIn(row["mask"], (0xF00, 0xFFF))
                self.assertEqual(row["descriptor_index"], 0)

    def test_descriptor_table(self):
        d = self.d["a6000"]["descriptor"]
        base = int(d["base"], 16)
        self.assertTrue(d["shared_by_helpers"])
        rows = [list(self.a6[base - BASE + 12 * k:base - BASE + 12 * k + 12])
                for k in range(3)]
        self.assertEqual(rows, d["rows"])
        self.assertEqual(rows[0], list(range(12)))
        self.assertEqual(rows[1], [0, 7, 6, 1, 2, 9, 8, 3, 4, 11, 10, 5])
        self.assertEqual(rows[2], [1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0])

    def test_consumer_structure(self):
        raw = self.a6[0x436D8EB2 - BASE:0x436D8EB2 - BASE + 4].hex()
        self.assertEqual(raw, "1c225543")       # movs r2,#0x1c ; muls r5,r2,r5
        self.assertEqual(self.a6[0x436D8EB8 - BASE:
                                 0x436D8EB8 - BASE + 2].hex(), "7b44")  # add r3,pc
        self.assertEqual(self.d["a6000"]["consumer"]["signature"],
                         "(obj, posicion_modo, flag)")

    def test_setter_limits(self):
        self.assertEqual(self.a6[0x436D6B62 - BASE:0x436D6B62 - BASE + 2].hex(), "472a")
        self.assertEqual(self.d["a6000"]["setter"]["disasm"][0]["insn"],
                         "ldr r3, [pc, #0x138]")

    def test_comparison(self):
        cmp_ = self.d["comparison"]
        self.assertEqual(cmp_["counts"], {"a6000": 13, "a7s": 34})
        self.assertEqual(cmp_["blocks"]["a6000"], ["obj+0x14", "obj+0xa1"])
        self.assertEqual(cmp_["blocks"]["a7s"], ["obj+0x16", "obj+0x2e", "obj+0xa5"])
        self.assertEqual(cmp_["descriptor_rows"], {"a6000": 3, "a7s": 2})
        self.assertEqual(cmp_["zero_masks"], {"a6000": 0, "a7s": 30})
        self.assertFalse(cmp_["silent_codes_present"]["a6000"])
        self.assertTrue(cmp_["silent_codes_present"]["a7s"])

    def test_a7s_tables_recomputed(self):
        for meta in self.d["a7s"]["tables"].values():
            base = int(meta["base"], 16)
            for row in meta["rows"]:
                addr = base + 0x1C * row["index"]
                self.assertEqual(self.u16(self.a7, addr + 0x18), row["mask"])
                self.assertEqual(self.u32(self.a7, addr + 0x14),
                                 row["descriptor_index"])

    def test_verdicts(self):
        v = self.d["verdicts"]
        self.assertTrue(v["same_mechanism"])
        self.assertFalse(v["a6000_has_silent_mode"])
        self.assertFalse(v["a6000_uses_permutation_descriptor"])
        self.assertFalse(v["a6000_has_zero_masks"])

    def test_limits(self):
        text = " ".join(self.d["limits"])
        self.assertIn("INFERENCIA", text)
        self.assertIn("S51", text)

    def test_verify_script_passes(self):
        res = subprocess.run([sys.executable, str(VERIFY)], capture_output=True,
                             text=True, check=False)
        self.assertEqual(res.returncode, 0, res.stdout + res.stderr)
        self.assertIn("0 fallos", res.stdout)


if __name__ == "__main__":
    unittest.main()
