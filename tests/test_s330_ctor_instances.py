"""S330 - tests del carril B: instancias del constructor 0x436f3fc0 (idx != 0)."""
import json
import struct
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JSON = ROOT / "analysis/s330_ctor_instances/ctor_instances.json"
VERIFY = ROOT / "analysis/s330_ctor_instances/verify_ctor_instances.py"
BASE = 0x43541000
A7S = ROOT / ("firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/"
              "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin")


class CtorInstances(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d = json.loads(JSON.read_text())
        cls.a7 = A7S.read_bytes()

    def u32(self, addr):
        return struct.unpack_from("<I", self.a7, addr - BASE)[0]

    def test_single_direct_call(self):
        calls = self.d["scan_a7s"]["direct_calls"]
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0]["addr"], "0x436f2a8a")
        self.assertEqual(calls[0]["target"], "0x436f3fc0")
        self.assertEqual(calls[0]["kind"], "bl")

    def test_no_literals_or_pointers(self):
        self.assertEqual(self.d["scan_a7s"]["literal_ctor"], [])
        self.assertEqual(self.d["scan_a7s"]["literal_ctor_thumb"], [])
        self.assertEqual(self.d["vtable"]["ctor_slots"], [])
        self.assertFalse(self.d["verdict"]["ctor_in_vtable"])
        self.assertEqual(self.d["verdict"]["ctor_as_pointer"], [])

    def test_idx_is_constant_zero(self):
        dis = self.d["known_caller"]["disasm"]
        self.assertEqual(dis[1]["insn"], "movs r1, #0")
        bl = [i for i in dis if i["insn"].startswith("bl ")]
        self.assertEqual(bl[0]["insn"], "bl #0x436f3fc0")
        self.assertEqual(dis[0]["address"], "0x436f2a7c")
        self.assertEqual(self.d["known_caller"]["addr"], "0x436f2a8a")

    def test_singleton_factory(self):
        fac = self.d["factory"]
        self.assertEqual(fac["singleton_slot"], "0x440245cc")
        self.assertEqual(fac["singleton_value"], "0x43e8d994")
        self.assertEqual(self.u32(0x440245CC), 0x43E8D994)
        self.assertEqual(fac["direct_callers"], [])
        self.assertEqual(fac["register_call"], "0x439a2794")

    def test_store_of_row_index(self):
        # `str.w r6,[r4,#0x2b4]` en 0x436f40fe: el ctor guarda su argumento
        raw = self.a7[0x436F40FE - BASE:0x436F40FE - BASE + 4].hex()
        self.assertEqual(raw, "c4f8b462")

    def test_verdict(self):
        v = self.d["verdict"]
        self.assertEqual(v["static_instances"], 1)
        self.assertEqual(v["static_instances_with_idx_nonzero"], 0)
        self.assertEqual(v["singleton_row"], 0)
        self.assertEqual(v["per_mode_rows_applied"], "solo la fila 0 (modo 0x0b)")

    def test_limits(self):
        text = " ".join(self.d["limits"])
        self.assertIn("runtime", text)
        self.assertIn("S51", text)

    def test_verify_script_passes(self):
        res = subprocess.run([sys.executable, str(VERIFY)], capture_output=True,
                             text=True, check=False)
        self.assertEqual(res.returncode, 0, res.stdout + res.stderr)
        self.assertIn("0 fallos", res.stdout)


if __name__ == "__main__":
    unittest.main()
