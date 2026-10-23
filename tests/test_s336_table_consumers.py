"""S336 - tests del carril B: mapa de consumidores de T1/T2/T3."""
import json
import struct
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JSON = ROOT / "analysis/s336_table_consumers/table_consumers.json"
VERIFY = ROOT / "analysis/s336_table_consumers/verify_table_consumers.py"
BASE = 0x43541000
A7S = ROOT / ("firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/"
              "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin")


class TableConsumers(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d = json.loads(JSON.read_text())
        cls.a7 = A7S.read_bytes()

    def u32(self, addr):
        return struct.unpack_from("<I", self.a7, addr - BASE)[0]

    def test_reference_count(self):
        self.assertEqual(self.d["reference_count"], 13)
        tables = [r["table"] for r in self.d["references"]]
        self.assertEqual(tables.count("T1"), 5)
        self.assertEqual(tables.count("T2"), 4)
        self.assertEqual(tables.count("T3"), 2)
        self.assertEqual(tables.count("B"), 2)

    def test_functions(self):
        got = {name: len(c["references"]) for name, c in self.d["consumers"].items()}
        self.assertEqual(got["index_and_mask"], 3)
        self.assertEqual(got["copy_row_patch"], 3)
        self.assertEqual(got["op_code_w0"], 2)
        self.assertEqual(got["sum_w0"], 2)
        self.assertEqual(got["row_selectors_entry"], 1)
        self.assertEqual(self.d["verdicts"]["consumer_functions"], 7)
        self.assertEqual(self.d["verdicts"]["row_field_consumers"], 5)

    def test_copy_row_patch(self):
        c = self.d["consumers"]["copy_row_patch"]
        self.assertEqual(c["tables"], ["T1", "T2", "T3"])
        self.assertEqual(c["range"], ["0x436f5f7c", "0x436f6044"])
        raw = self.a7[0x436F5FA6 - BASE:0x436F5FA6 - BASE + 4].hex()
        self.assertEqual(raw, "bee80f00")       # ldm.w lr!,{r0-r3}

    def test_row_selectors(self):
        c = self.d["consumers"]["row_selectors_entry"]
        self.assertEqual(c["tables"], ["T1"])
        ops = [i["insn"] for i in self.d["consumers"]["row_selectors"]["disasm"]]
        self.assertIn("ldrb r3, [r0, #5]", ops)
        self.assertIn("ldrb r2, [r0, #6]", ops)
        self.assertIn("ldrb r2, [r0, #4]", ops)

    def test_index_and_mask_scope(self):
        c = self.d["consumers"]["index_and_mask"]
        self.assertEqual(c["fields"], ["+0x14 (indice)", "+0x18 (mascara)"])
        self.assertFalse(self.d["verdicts"]["only_index_and_mask"])
        self.assertIn("valido solo para 0x436f618c",
                      self.d["verdicts"]["s331_claim_scope"])

    def test_w4_unverified(self):
        v = self.d["verdicts"]
        self.assertIn("NO_VERIFICADO", v["w4_semantics"])
        self.assertIn("+0x04", v["fields_consumed_superset"])

    def test_corrections(self):
        text = " ".join(self.d["corrections"])
        self.assertIn("22 B", text)
        self.assertIn("0x436f6240", text)

    def test_limits(self):
        text = " ".join(self.d["limits"])
        self.assertIn("S51", text)

    def test_verify_script_passes(self):
        res = subprocess.run([sys.executable, str(VERIFY)], capture_output=True,
                             text=True, check=False)
        self.assertEqual(res.returncode, 0, res.stdout + res.stderr)
        self.assertIn("0 fallos", res.stdout)


if __name__ == "__main__":
    unittest.main()
