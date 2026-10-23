"""S343 - tests del carril B: la fila T configura los seis bloques de canal."""
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JSON = ROOT / "analysis/s343_row_copy_chain/row_copy_chain.json"
VERIFY = ROOT / "analysis/s343_row_copy_chain/verify_row_copy_chain.py"


class RowCopyChain(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d = json.loads(JSON.read_text())

    def test_block_layout(self):
        layout = self.d["chain"]["block_layout"]
        self.assertEqual(layout["row_bytes"], 20)
        self.assertEqual(layout["pairs"], 12)
        self.assertEqual(layout["total"], 44)
        self.assertEqual(layout["padding_pair"], [0, 0x0B])

    def test_chain_calls(self):
        self.assertTrue(any(i["insn"] == "bl #0x43ada310"
                            for i in self.d["chain"]["copy_code"]))
        self.assertTrue(any(i["insn"] == "bl #0x43ada480"
                            for i in self.d["chain"]["block_code"]))

    def test_dispatcher(self):
        disp = self.d["chain"]["dispatch"]
        self.assertEqual(disp["max_flags"], 12)
        self.assertIn("obj+8", disp["flag_count"])

    def test_tbh_six_cases(self):
        h = self.d["handlers"]["0x436f6710"]
        self.assertEqual(len(h["tbh"]), 6)
        self.assertEqual(h["tbh"][0], "0x436f672c")

    def test_case0_twelve_fields(self):
        bytes_ = [x["row_byte"] for x in self.d["decompress_case0"]]
        self.assertEqual(bytes_, list(range(1, 0x19, 2)))
        self.assertTrue(all(x["writer"].startswith("#0x436f75")
                            for x in self.d["decompress_case0"]))

    def test_single_bit_per_case(self):
        s = self.d["single_bit_writers"]
        self.assertEqual([x["case"] for x in s], [0, 1, 2, 3, 4, 5])
        self.assertEqual([x["block"] for x in s],
                         ["0xf3122300", "0xf3122200", "0xf3123300",
                          "0xf3123200", "0xfc0a3100", "0xfc0a4100"])

    def test_writer_library(self):
        lib = self.d["writer_library"]
        self.assertEqual(lib["total"], 178)
        self.assertEqual(lib["per_block"], {
            "0xf3122200": 25, "0xf3122300": 31, "0xf3123200": 25,
            "0xf3123300": 31, "0xfc0a3100": 34, "0xfc0a4100": 32})

    def test_cross_model(self):
        c = self.d["cross_model"]
        self.assertEqual(c["writers"], {"a7s": 178, "a6000": 177, "a6300": 178})
        self.assertEqual(c["a7s_only_fields"],
                         [{"block": "0xfc0a3100", "offset": 12, "lsb": 24, "width": 1}])
        self.assertEqual(c["a6000_only_fields"], [])

    def test_same_blocks_as_w0(self):
        self.assertTrue(self.d["s340_cross_check"]["blocks_equal"])
        self.assertEqual(self.d["getters"]["total"], 6)

    def test_verdicts_and_limits(self):
        v = self.d["verdicts"]
        self.assertFalse(v["ends_in_log"])
        self.assertFalse(v["ends_in_p2s"])
        self.assertTrue(v["same_blocks_as_w0"])
        self.assertEqual(v["channel_semantics"], "NO_VERIFICADO")
        self.assertIn("S51", " ".join(self.d["limits"]))

    def test_verify_script_passes(self):
        res = subprocess.run([sys.executable, str(VERIFY)], capture_output=True,
                             text=True, check=False)
        self.assertEqual(res.returncode, 0, res.stdout + res.stderr)
        self.assertIn("0 fallos", res.stdout)


if __name__ == "__main__":
    unittest.main()
