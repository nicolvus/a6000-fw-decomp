"""S335 - tests del carril B: la capa de mascaras termina en MMIO."""
import json
import struct
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JSON = ROOT / "analysis/s335_mmio_layer/mmio_layer.json"
VERIFY = ROOT / "analysis/s335_mmio_layer/verify_mmio_layer.py"
BASE = 0x43541000
A7S = ROOT / ("firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/"
              "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin")
A6000 = ROOT / ("firmware/extracted/fw321/firmware.tar_unpacked/"
                "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin")


class MmioLayer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d = json.loads(JSON.read_text())
        cls.a7 = A7S.read_bytes()
        cls.a6 = A6000.read_bytes()

    def u32(self, blob, addr):
        return struct.unpack_from("<I", blob, addr - BASE)[0]

    def test_mmio_addresses(self):
        self.assertEqual(self.d["mmio"]["addresses"],
                         ["0xf292b000", "0xf292b004", "0xf292b008", "0xfc02a00c"])
        for addr, site in self.d["mmio"]["sites"].items():
            self.assertEqual(len(site["a7s"]), len(site["a6000"]))
            for s in site["a7s"]:
                self.assertEqual(self.u32(self.a7, int(s, 16)), int(addr, 16))

    def test_literals_are_absolute(self):
        for info in self.d["a7s_layer"].values():
            self.assertTrue(info["literals"])
            for lit in info["literals"]:
                value = int(lit["value"], 16)
                self.assertGreaterEqual(value, 0xF0000000)
                self.assertEqual(self.u32(self.a7, int(lit["literal_addr"], 16)), value)

    def test_roles(self):
        roles = {k: v["role"] for k, v in self.d["a7s_layer"].items()}
        self.assertIn("0xf292b000", roles["0x436f82b0"])
        self.assertIn("0xf292b004", roles["0x436f82a0"])
        self.assertIn("0xf292b008", roles["0x436f8290"])
        self.assertIn("0xfc02a00c", roles["0x436f82e8"])
        self.assertIn("0xfc02a00c", roles["0x436f8324"])

    def test_field_widths(self):
        self.assertEqual(self.d["verdicts"]["field_width"],
                         "12 bits (lsls #0x14 / lsrs #0x14, bfi #0,#0xc)")
        self.assertEqual(self.d["verdicts"]["extra_bit"],
                         "bit 12 (bfc #0xc,#1 en 0x436f8324)")
        # bfi con #0,#0xc en 0x436f8300
        raw = self.a7[0x436F8308 - BASE:0x436F8308 - BASE + 4].hex()
        self.assertEqual(raw, "62f30b01")

    def test_verdicts(self):
        v = self.d["verdicts"]
        self.assertTrue(v["mask_path_ends_in_mmio"])
        self.assertEqual(v["p2s_hypothesis"], "DESCARTADA")
        self.assertTrue(v["same_layer_in_a6000"])
        self.assertEqual(v["mmio_semantics"], "NO_VERIFICADO")

    def test_a6000_same_layer(self):
        values = set()
        for entry in self.d["a6000_layer"].values():
            values.update(int(lit["value"], 16) for lit in entry["literals"])
        self.assertIn(0xF292B004, values)
        self.assertIn(0xF292B008, values)

    def test_limits(self):
        text = " ".join(self.d["limits"])
        self.assertIn("datasheet", text)
        self.assertIn("S51", text)

    def test_verify_script_passes(self):
        res = subprocess.run([sys.executable, str(VERIFY)], capture_output=True,
                             text=True, check=False)
        self.assertEqual(res.returncode, 0, res.stdout + res.stderr)
        self.assertIn("0 fallos", res.stdout)


if __name__ == "__main__":
    unittest.main()
