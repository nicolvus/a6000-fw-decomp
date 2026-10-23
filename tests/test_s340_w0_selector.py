"""S340 - tests del carril B: w0 como selector de registro MMIO."""
import json
import struct
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JSON = ROOT / "analysis/s340_w0_selector/w0_selector.json"
VERIFY = ROOT / "analysis/s340_w0_selector/verify_w0_selector.py"
BASE = 0x43541000
A7S = ROOT / ("firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/"
              "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin")


class W0Selector(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d = json.loads(JSON.read_text())
        cls.a7 = A7S.read_bytes()

    def u32(self, addr):
        return struct.unpack_from("<I", self.a7, addr - BASE)[0]

    def test_switch(self):
        s = self.d["switch"]
        self.assertEqual(s["address"], "0x436f74c0")
        self.assertEqual(s["case_count"], 6)
        self.assertEqual(s["tbb_bytes"], [3, 6, 9, 12, 15, 18])
        self.assertEqual(self.a7[0x436F74C6 - BASE:0x436F74C6 - BASE + 2].hex(),
                         "dfe8")                         # tbb [pc,r1]

    def test_cases(self):
        cases = self.d["cases"]
        self.assertEqual(len(cases), 6)
        self.assertEqual([c["literal"] for c in cases],
                         ["0xf3122300", "0xf3122200", "0xf3123300",
                          "0xf3123200", "0xfc0a3100", "0xfc0a4100"])
        self.assertTrue(all(c["matches"] for c in cases))
        offsets = [c["offset"] for c in cases]
        self.assertEqual(offsets, ["0x30", "0x24", "0x30", "0x24", "0x30", "0x30"])

    def test_sum(self):
        s = self.d["sum"]
        self.assertEqual(s["address"], "0x436f605c")
        self.assertEqual(s["reads"], "w0 de T1 y de T2")
        self.assertEqual(s["combines"], "suma")

    def test_per_code(self):
        per = self.d["per_code"]
        self.assertEqual(per["0x4c"]["selectors"], {"T1": 0, "T2": 2, "T3": 4})
        self.assertEqual(per["0x50"]["selectors"], {"T1": 1, "T2": 3, "T3": 4})
        codes = [self.u32(0x43FEE370 + 4 * i) for i in range(34)]
        pos = {c: i for i, c in enumerate(codes)}
        for code, meta in per.items():
            self.assertEqual(meta["position"], pos[int(code, 16)])

    def test_verdicts(self):
        v = self.d["verdicts"]
        self.assertTrue(v["w0_is_mmio_selector"])
        self.assertEqual(v["selector_offsets"], {"0x30": 4, "0x24": 2})
        self.assertEqual(v["t1_channels"], [0, 1])
        self.assertEqual(v["t2_channels"], [2, 3])
        self.assertEqual(v["t3_selector"], [4])
        self.assertEqual(v["measured_quantity"], "NO_VERIFICADO")

    def test_corrections(self):
        text = " ".join(self.d["corrections"])
        self.assertIn("selector", text)
        self.assertIn("S334", text)

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
