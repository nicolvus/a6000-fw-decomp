"""S334 - tests del carril B: los pares se colapsan en mascaras u16."""
import json
import struct
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JSON = ROOT / "analysis/s334_pair_dataflow/pair_dataflow.json"
VERIFY = ROOT / "analysis/s334_pair_dataflow/verify_pair_dataflow.py"
BASE = 0x43541000
A7S = ROOT / ("firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/"
              "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin")


class PairDataflow(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d = json.loads(JSON.read_text())
        cls.a7 = A7S.read_bytes()

    def u32(self, addr):
        return struct.unpack_from("<I", self.a7, addr - BASE)[0]

    def u16(self, addr):
        return struct.unpack_from("<H", self.a7, addr - BASE)[0]

    def test_collapse_bit_index(self):
        c = self.d["collapse"]["obj_68"]
        self.assertEqual(c["input"], "obj+0x16 (12 pares)")
        self.assertEqual(c["output"], "u16 en obj+0x68")
        self.assertEqual(c["loop"], "r2 = 0,2,...,0x16; cmp r2,#0x18")
        self.assertIn("1", c["bit_op"])
        # el bucle compara con 0x18 y el shift usa el byte del par
        self.assertEqual(self.a7[0x43ADA38C - BASE:0x43ADA38C - BASE + 2].hex(), "182a")
        self.assertEqual(self.a7[0x43ADA382 - BASE:0x43ADA382 - BASE + 4].hex(),
                         "15fa04f4")

    def test_collapse_destination(self):
        d = self.d["collapse"]["dst"]
        self.assertEqual(d["output"], "u16 en [r2]")
        self.assertEqual(self.a7[0x43ADA420 - BASE:0x43ADA420 - BASE + 2].hex(), "1580")
        self.assertEqual(d["callers"], {"0x436f61f8": "obj+0xa5 -> obj+0xf8, op=1"})

    def test_mask_destinations(self):
        self.assertEqual(self.d["verdicts"]["mask_destinations"],
                         ["obj+0x68", "obj+0xf8"])
        self.assertTrue(self.d["verdicts"]["blocks_collapse_to_u16_masks"])
        self.assertTrue(self.d["verdicts"]["pair_second_byte_is_bit_index"])
        self.assertFalse(self.d["verdicts"]["pair_second_byte_is_state_offset"])

    def test_op_codes(self):
        ops = self.d["op_select"]["per_code"]
        self.assertEqual(ops["0x4c"], {"T1_w0": 0, "T2_w0": 2, "T3_w0": 4})
        self.assertEqual(ops["0x50"], {"T1_w0": 1, "T2_w0": 3, "T3_w0": 4})
        self.assertEqual(self.d["verdicts"]["silent_op_codes"]["0x4e"], [0, 2])
        self.assertTrue(self.d["verdicts"]["w0_is_op_code"])

    def test_apply_ops(self):
        a = self.d["apply"]
        self.assertEqual(a["address"], "0x436f822c")
        self.assertIn("0x436f82a0", a["ops"]["0"])
        self.assertIn("0x436f8300", a["ops"]["1"])
        self.assertIn("traza", a["ops"]["2/otros"])

    def test_per_code_recomputed(self):
        codes = [self.u32(0x43FEE370 + 4 * i) for i in range(34)]
        pos = {c: i for i, c in enumerate(codes)}
        bases = {"T1": 0x43BBEB70, "T2": 0x43BBF2E8, "T3": 0x43BBEF30}
        for code, meta in self.d["per_code"].items():
            c = int(code, 16)
            self.assertEqual(meta["position"], pos[c])
            for name, base in bases.items():
                addr = base + 0x1C * pos[c]
                self.assertEqual(self.u32(addr), meta[name]["w0"])
                self.assertEqual(self.u16(addr + 0x18), meta[name]["mask"])

    def test_silent_t2_mask(self):
        per = self.d["per_code"]
        self.assertEqual(per["0x4c"]["T2"]["mask"], 0x3FF)
        self.assertEqual(per["0x4e"]["T2"]["mask"], 0)
        self.assertEqual(per["0x4f"]["T2"]["mask"], 0)

    def test_limits(self):
        text = " ".join(self.d["limits"])
        self.assertIn("MMIO", text)
        self.assertIn("S51", text)

    def test_verify_script_passes(self):
        res = subprocess.run([sys.executable, str(VERIFY)], capture_output=True,
                             text=True, check=False)
        self.assertEqual(res.returncode, 0, res.stdout + res.stderr)
        self.assertIn("0 fallos", res.stdout)


if __name__ == "__main__":
    unittest.main()
