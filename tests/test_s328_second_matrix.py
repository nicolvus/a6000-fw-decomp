import json
import struct
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JSON = ROOT / "analysis/s328_second_matrix/second_matrix.json"
BASE = 0x43541000
A7S = ROOT / ("firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/"
              "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin")
A6000 = ROOT / ("firmware/extracted/fw321/firmware.tar_unpacked/"
                "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin")


class SecondMatrix(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d = json.loads(JSON.read_text())
        cls.a7 = A7S.read_bytes()
        cls.a6 = A6000.read_bytes()

    def u32(self, blob, addr):
        return struct.unpack_from("<I", blob, addr - BASE)[0]

    def test_a7s_slot(self):
        e = self.d["cases"]["a7s_fw320"]
        self.assertEqual(e["slot"], "0x44026088")
        self.assertEqual(self.u32(self.a7, 0x44026088), 0x43E8DE00)
        self.assertEqual(e["offset_sites"], ["0x436f394e"])
        self.assertEqual(0x44024540 + 0x1B48, 0x44026088)

    def test_a6000_slot(self):
        e = self.d["cases"]["a6000_fw321"]
        self.assertEqual(e["slot"], "0x44026694")
        self.assertEqual(self.u32(self.a6, 0x44026694), 0x43E80160)
        self.assertEqual(e["offset_sites"], ["0x436d65a0"])
        self.assertEqual(0x4401EEE4 + 0x77B0, 0x44026694)

    def test_both_tables_are_zero(self):
        self.assertEqual(self.d["cases"]["a7s_fw320"]["table_nonzero_bytes_64"], 0)
        self.assertEqual(self.d["cases"]["a6000_fw321"]["table_nonzero_bytes_64"], 0)
        for blob, table in ((self.a7, 0x43E8DE00), (self.a6, 0x43E80160)):
            self.assertEqual(self.u32(blob, table), 0)

    def test_no_static_producer(self):
        self.assertFalse(self.d["verdict"]["static_producer"])
        self.assertFalse(self.d["verdict"]["loop_executes_on_blob"])
        # el unico literal del valor es el propio slot
        self.assertEqual(self.d["cases"]["a7s_fw320"]["slot_value_refs"], ["0x44026088"])
        self.assertEqual(self.d["cases"]["a6000_fw321"]["slot_value_refs"], ["0x44026694"])

    def test_gate_is_sub(self):
        self.assertEqual(self.d["verdict"]["gate"], "sub != 0 (S324)")
        self.assertEqual(self.d["verdict"]["sub_effect"], "NO_VERIFICADO")

    def test_limits(self):
        text = " ".join(self.d["scope_limit"])
        self.assertIn("runtime", text)
        self.assertIn("DMA", text)


if __name__ == "__main__":
    unittest.main()
