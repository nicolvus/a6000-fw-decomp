"""S342 - tests del carril B: 0x43fef404 tiene consumidores PIC (ODL)."""
import json
import struct
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JSON = ROOT / "analysis/s342_fef404_consumers/fef404_consumers.json"
VERIFY = ROOT / "analysis/s342_fef404_consumers/verify_fef404_consumers.py"
BASE = 0x43541000
A7S = ROOT / ("firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/"
              "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin")


class Fef404Consumers(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d = json.loads(JSON.read_text())
        cls.a7 = A7S.read_bytes()

    def u16(self, addr):
        return struct.unpack_from("<H", self.a7, addr - BASE)[0]

    def u32(self, addr):
        return struct.unpack_from("<I", self.a7, addr - BASE)[0]

    def test_table_shape(self):
        t = self.d["a7s"]["table"]
        self.assertEqual(t["address"], "0x43fef404")
        self.assertEqual(t["entries"], 69)
        self.assertEqual(t["end"], "0x43fef518")
        self.assertEqual(t["second_field"], "0x000d")

    def test_ids_recomputed(self):
        ids = [self.u16(0x43FEF404 + 4 * i) for i in range(69)]
        self.assertEqual(ids, self.d["a7s"]["table"]["ids"])
        self.assertEqual(len(set(ids)), 69)

    def test_prefix_array_is_256_entries(self):
        p = self.d["a7s"]["prefix_array"]
        self.assertEqual(p["start"], "0x43fef004")
        self.assertEqual(p["entries"], 256)
        self.assertEqual(p["ends_at"], "0x43fef404")
        self.assertEqual(p["contiguous_43f9c622_before_table"], 169)
        self.assertEqual(self.u32(0x43FEF404 - 4), 0x43F9C622)

    def test_two_pic_consumers(self):
        sites = [s["ldr"] for s in self.d["a7s"]["pic_sites"]]
        self.assertEqual(sites, ["0x437056f8", "0x43705754"])
        for s in self.d["a7s"]["pic_sites"]:
            self.assertEqual(s["base"], "0x43fef404")

    def test_loop_equals_entry_count(self):
        a = self.d["a7s"]["consumers"]["A"]
        b = self.d["a7s"]["consumers"]["B"]
        self.assertEqual(a["loop"]["cmp"], "cmp r7, #0x45")
        self.assertEqual(a["loop_count"], 69)
        self.assertEqual(b["loop"]["cmp"], "cmp.w r5, #0x114")
        self.assertEqual(b["loop"]["step"], 4)
        self.assertEqual(b["loop_count"], 69)

    def test_companion_array(self):
        c = self.d["a7s"]["companion_array"]
        self.assertEqual(c["address"], "0x43fef520")
        self.assertEqual(c["entries"], 69)
        self.assertEqual(self.u32(0x44028C78), 0x43FEF520)
        self.assertTrue(c["all_in_zero_run"])
        self.assertEqual(c["pic_sites"], [])

    def test_callers_in_odl_init(self):
        self.assertEqual(self.d["a7s"]["callers"]["A"], ["0x4373d0b4"])
        self.assertEqual(self.d["a7s"]["callers"]["B"], ["0x4373d2f2"])
        joined = " ".join(self.d["a7s"]["module_strings"])
        self.assertIn("Camera::Lens::ODL", joined)
        self.assertIn("Initialize(UPM_BOOT_FACTOR*)", joined)

    def test_cross_model(self):
        c = self.d["cross_model"]
        self.assertEqual(c["entries"], {"a7s": 69, "a6000": 47, "a6300": 69})
        self.assertTrue(c["a6000_subset_of_a7s"])
        self.assertEqual(c["a6000_missing"], [f"0x{x:02x}" for x in range(0x4F, 0x65)])
        self.assertTrue(c["a6300_equals_a7s"])
        self.assertEqual(c["loop_bounds"], {"a7s": 69, "a6000": 47, "a6300": 69})

    def test_verdicts(self):
        v = self.d["verdicts"]
        self.assertFalse(v["is_timing_table"])
        self.assertTrue(v["has_static_consumers"])
        self.assertEqual(v["consumer_count_per_model"], 2)
        self.assertFalse(v["indexed_by_drive_mode"])
        self.assertIn("ODL", v["subsystem"])
        self.assertEqual(v["s329_negative"], "se mantiene")

    def test_limits(self):
        text = " ".join(self.d["limits"])
        self.assertIn("S51", text)
        self.assertIn("INFERENCIA", text)
        self.assertIn(".bss", text)

    def test_verify_script_passes(self):
        res = subprocess.run([sys.executable, str(VERIFY)], capture_output=True,
                             text=True, check=False)
        self.assertEqual(res.returncode, 0, res.stdout + res.stderr)
        self.assertIn("0 fallos", res.stdout)


if __name__ == "__main__":
    unittest.main()
