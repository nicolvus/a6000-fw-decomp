"""S339 - tests del carril B: bloque 0xf292b000..8 (identidad no verificada)."""
import json
import struct
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JSON = ROOT / "analysis/s339_block_f292b/block_f292b.json"
VERIFY = ROOT / "analysis/s339_block_f292b/verify_block_f292b.py"
BASE = 0x43541000
A7S = ROOT / ("firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/"
              "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin")


class BlockF292B(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d = json.loads(JSON.read_text())
        cls.a7 = A7S.read_bytes()

    def u32(self, addr):
        return struct.unpack_from("<I", self.a7, addr - BASE)[0]

    def test_registers(self):
        self.assertEqual(self.d["registers"],
                         ["0xf292b000", "0xf292b004", "0xf292b008"])
        self.assertEqual(self.d["interface"]["registers"], 3)
        self.assertEqual(self.d["interface"]["field_width"], "12 bits")

    def test_sites(self):
        sites = self.d["literal_sites"]
        self.assertEqual(len(sites["0xf292b000"]["a7s"]), 1)
        self.assertEqual(len(sites["0xf292b004"]["a7s"]), 2)
        self.assertEqual(len(sites["0xf292b008"]["a7s"]), 3)
        for reg, info in sites.items():
            for s in info["a7s"]:
                self.assertEqual(self.u32(int(s, 16)), int(reg, 16))

    def test_only_accessors(self):
        self.assertTrue(self.d["all_sites_in_accessors"])
        for info in self.d["literal_sites"].values():
            for s in info["a7s"]:
                self.assertTrue(0x436F8290 <= int(s, 16) < 0x436F82F0)

    def test_window(self):
        win = self.d["window_0xf292x000"]["a7s"]
        self.assertEqual(win["0xf292b000"], 6)
        self.assertEqual(win["0xf292d000"], 1)
        self.assertIn("0xf2910000", self.d["known_neighbours"])

    def test_verdicts(self):
        v = self.d["verdicts"]
        self.assertEqual(v["identity"], "NO_VERIFICADO")
        self.assertFalse(v["documented_in_repo"])
        self.assertTrue(v["only_mask_layer_uses_it"])

    def test_limits(self):
        text = " ".join(self.d["limits"])
        self.assertIn("S51", text)
        self.assertIn("datasheet" if "datasheet" in text else "simbolo", text)

    def test_verify_script_passes(self):
        res = subprocess.run([sys.executable, str(VERIFY)], capture_output=True,
                             text=True, check=False)
        self.assertEqual(res.returncode, 0, res.stdout + res.stderr)
        self.assertIn("0 fallos", res.stdout)


if __name__ == "__main__":
    unittest.main()
