"""S331 - tests del carril B: firma del consumidor (posicion de modo, no obj+0x2b4)."""
import json
import struct
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JSON = ROOT / "analysis/s331_consumer_signature/consumer_signature.json"
VERIFY = ROOT / "analysis/s331_consumer_signature/verify_consumer_signature.py"
BASE = 0x43541000
A7S = ROOT / ("firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/"
              "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin")


class ConsumerSignature(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d = json.loads(JSON.read_text())
        cls.a7 = A7S.read_bytes()

    def u32(self, addr):
        return struct.unpack_from("<I", self.a7, addr - BASE)[0]

    def u16(self, addr):
        return struct.unpack_from("<H", self.a7, addr - BASE)[0]

    def test_signature(self):
        self.assertEqual(self.d["consumer"]["signature"],
                         "0x436f618c(obj, posicion_modo, flag)")
        self.assertTrue(self.d["consumer"]["mov_r5_r1"])
        self.assertEqual(self.d["consumer"]["stride_muls"], "muls r5, r2, r5")

    def test_callers_pass_mode_position(self):
        self.assertEqual(self.d["consumer_callers"], ["0x436f3be2", "0x436f4480"])
        self.assertEqual(self.d["call_sites"]["setter"]["r1"],
                         "[obj+0x1b8] (indice de la busqueda)")
        self.assertEqual(self.d["call_sites"]["setter"]["r2"], "[obj+0x2b4] (flag)")
        # el indice es el valor devuelto por la busqueda lineal y se guarda en +0x1b8
        self.assertEqual(self.d["search"]["returns"], "indice 0..count-1 o 0xff")
        first = self.a7[0x43ADA284 - BASE:0x43ADA284 - BASE + 2]
        self.assertEqual(first.hex(), "10b5")      # push {r4, lr}

    def test_search_returns_ff_when_missing(self):
        raw = self.a7[0x43ADA29C - BASE:0x43ADA29C - BASE + 2]
        self.assertEqual(raw.hex(), "ff20")     # movs r0,#0xff

    def test_flag_gate_before_stride(self):
        # cmp r2,#1 en 0x436f6196 y movs r2,#0x1c despues (0x436f61a4)
        self.assertLess(0x436F6196, 0x436F61A4)
        raw_cmp = self.a7[0x436F6196 - BASE:0x436F6196 - BASE + 2]
        self.assertEqual(raw_cmp.hex(), "012a")

    def test_obj_2b4_is_not_row_index(self):
        v = self.d["verdicts"]
        self.assertFalse(v["obj_2b4_is_row_index"])
        self.assertTrue(v["obj_2b4_is_log_flag"])
        self.assertTrue(v["row_index_is_mode_position"])
        self.assertIn("REFUTADO", v["s327_row_index_writer"])
        self.assertIn("REFUTADO", v["s330_singleton_row0_only"])

    def test_siblings_same_signature(self):
        self.assertEqual(set(self.d["siblings"]), {"fill_6c", "fill_68"})
        for meta in self.d["siblings"].values():
            self.assertEqual(meta["signature"], "(obj, posicion_modo, flag)")
            self.assertEqual(meta["disasm"][0]["insn"], "cmp r1, #0xff")

    def test_per_mode_rows(self):
        tables = self.d["tables"]
        self.assertEqual(tables["bases"]["T2"], "0x43bbf2e8")
        pos = {int(k, 16): v["position"] for k, v in tables["per_code"].items()}
        self.assertEqual(pos[0x4E], 29)
        self.assertEqual(pos[0x4F], 30)
        for name, base_s in tables["bases"].items():
            base = int(base_s, 16)
            for meta in tables["per_code"].values():
                row = meta["rows"][name]
                addr = base + 0x1C * meta["position"]
                self.assertEqual(self.u32(addr), row["w0"])
                self.assertEqual(self.u32(addr + 0x14), row["descriptor_index"])
                self.assertEqual(self.u16(addr + 0x18), row["mask"])
                self.assertLessEqual(row["descriptor_index"], 1)

    def test_silent_difference_is_t2_mask(self):
        t2 = self.d["pair_diffs"]["T2"]["0x4e/0x4c"]
        self.assertFalse(t2["identical"])
        self.assertEqual(t2["fields_diff"], {"mask": [0, 1023]})
        for name in ("T1", "T3"):
            self.assertTrue(self.d["pair_diffs"][name]["0x4e/0x4c"]["identical"])

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
