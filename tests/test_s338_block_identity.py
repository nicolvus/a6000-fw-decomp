"""S338 - tests del carril B: identidad del bloque DFE/CISIF."""
import json
import struct
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JSON = ROOT / "analysis/s338_block_identity/block_identity.json"
VERIFY = ROOT / "analysis/s338_block_identity/verify_block_identity.py"
BASE = 0x43541000
A7S = ROOT / ("firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/"
              "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin")
A6000 = ROOT / ("firmware/extracted/fw321/firmware.tar_unpacked/"
                "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin")


class BlockIdentity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d = json.loads(JSON.read_text())
        cls.a7 = A7S.read_bytes()
        cls.a6 = A6000.read_bytes()

    def u32(self, blob, addr):
        return struct.unpack_from("<I", blob, addr - BASE)[0]

    def test_block_and_register(self):
        self.assertEqual(self.d["dfe_block"]["base"], "0xfc02a000")
        self.assertEqual(self.d["dfe_block"]["register"], "0xfc02a00c")
        self.assertEqual(int(self.d["dfe_block"]["register"], 16) -
                         int(self.d["dfe_block"]["base"], 16), 0xC)

    def test_literal_sites(self):
        sites = self.d["dfe_block"]["literal_sites"]
        self.assertEqual(sites["a7s"], ["0x436f2034", "0x436f2044"])
        self.assertEqual(sites["a6000"], ["0x436d2cbc", "0x436d2d78"])
        for blob, key in ((self.a7, "a7s"), (self.a6, "a6000")):
            for s in sites[key]:
                self.assertEqual(self.u32(blob, int(s, 16)), 0xFC02A000)

    def test_getters_and_writers(self):
        self.assertEqual(self.d["dfe_block"]["a7s_code"]["getter_base_plus_8"]["address"],
                         "0x436f2014")
        self.assertEqual(self.d["dfe_block"]["a7s_code"]["writer_base"]["address"],
                         "0x436f202c")
        self.assertEqual(self.d["dfe_block"]["a6000_code"]["getter_base_plus_8"]["address"],
                         "0x436d2c9c")
        self.assertEqual(self.d["dfe_block"]["a6000_code"]["writer_base"]["address"],
                         "0x436d2cb4")
        # el getter devuelve base+8 en ambos
        for blob, addr in ((self.a7, 0x436F201C), (self.a6, 0x436D2CA4)):
            raw = blob[addr - BASE:addr - BASE + 2].hex()
            self.assertEqual(raw, "0833")       # adds r3,#8

    def test_strings(self):
        strings = self.d["strings"]
        self.assertTrue(strings["DFECore"]["a7s"])
        self.assertTrue(strings["DFECore"]["a6000"])
        self.assertTrue(strings["CISIF"]["a7s"])
        self.assertTrue(strings["SIF SetSyncCode"]["a7s"])
        at = int(strings["CISIF"]["a6000"][0], 16)
        self.assertEqual(self.a6[at - BASE:at - BASE + 5], b"CISIF")

    def test_repo_evidence(self):
        ev = self.d["repo_evidence"]
        self.assertIn("fc02a008", ev["ghidra_snippet"])
        self.assertTrue(any("0x43bc20dc" in line for line in ev["s56_lines"]))

    def test_verdicts(self):
        v = self.d["verdicts"]
        self.assertTrue(v["block_is_cisif_receiver"])
        self.assertFalse(v["p2s_transport_affected"])
        self.assertFalse(v["unknown_block_identified"])
        self.assertIn("INFERENCIA", v["dfe_block_identification"])

    def test_corrections(self):
        text = " ".join(self.d["corrections"])
        self.assertIn("P2S", text)
        self.assertIn("CISIF", text)

    def test_limits(self):
        text = " ".join(self.d["limits"])
        self.assertIn("0xf292b000", text)
        self.assertIn("S51", text)

    def test_verify_script_passes(self):
        res = subprocess.run([sys.executable, str(VERIFY)], capture_output=True,
                             text=True, check=False)
        self.assertEqual(res.returncode, 0, res.stdout + res.stderr)
        self.assertIn("0 fallos", res.stdout)


if __name__ == "__main__":
    unittest.main()
