import json
import struct
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JSON = ROOT / "analysis/s315_register_lists/lists.json"
BASE = 0x43541000
A7S = ROOT / ("firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/"
              "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin")
A6000 = ROOT / ("firmware/extracted/fw321/firmware.tar_unpacked/"
                "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin")


class RegisterLists(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d = json.loads(JSON.read_text())
        cls.a7 = A7S.read_bytes()
        cls.a6 = A6000.read_bytes()

    def u16(self, addr):
        return struct.unpack_from("<H", self.a7, addr - BASE)[0]

    def u32(self, addr):
        return struct.unpack_from("<I", self.a7, addr - BASE)[0]

    def test_three_call_sites_and_modes(self):
        self.assertEqual([c["call"] for c in self.d["consumer"]["call_sites"]],
                         ["0x436f5422", "0x436f5b32", "0x436f5b52"])
        self.assertEqual(self.d["modes"],
                         {"0x436f5422": 2, "0x436f5b32": 2, "0x436f5b52": 0})
        self.assertEqual(self.u16(0x436F5B4E), 0x2100)  # movs r1,#0

    def test_got_slots_resolve_lists(self):
        self.assertEqual(self.u32(0x4402C940), 0x43FEE3F8)
        self.assertEqual(self.u32(0x44025EC0), 0x43FEE578)
        self.assertEqual(self.u32(0x440292B0), 0x43FEE590)

    def test_l95(self):
        lst = self.d["lists"]["L95"]
        self.assertEqual(lst["count"], 95)
        self.assertEqual(lst["terminator"], "0x43fee574")
        self.assertEqual(sum(1 for r in lst["records"] if r["dev"] == 0x83), 1)

    def test_l5_not_a_subset(self):
        lst = self.d["lists"]["L5"]
        self.assertEqual(lst["count"], 5)
        self.assertEqual(lst["terminator"], "0x43fee58c")
        regs = [r["reg"] for r in lst["records"]]
        self.assertEqual(regs, [0x5F, 0x61, 0x88, 0x94, 0xE3])
        # 0x61/0x88/0xe3 no estan en L95: L5 no es subconjunto (0x5f y 0x94 si).
        l95 = {r["reg"] for r in self.d["lists"]["L95"]["records"]}
        self.assertTrue({0x61, 0x88, 0xE3}.isdisjoint(l95))
        self.assertIn(0x5F, l95)

    def test_l1(self):
        lst = self.d["lists"]["L1"]
        self.assertEqual(lst["count"], 1)
        self.assertEqual((lst["records"][0]["reg"], lst["records"][0]["data"]), (0, 4))

    def test_consumer_reads_five_bytes(self):
        self.assertEqual(self.u16(0x436F4526), 0x7819)
        self.assertEqual(self.u16(0x436F452A), 0x885A)
        self.assertEqual(self.u16(0x436F452C), 0x791B)
        self.assertEqual(self.u16(0x436F4532), 0xF856)

    def test_consumer_and_getter_are_a7s_only(self):
        for addr, n in [(0x436F44C4, 24), (0x436F4588, 16)]:
            sig = self.a7[addr - BASE:addr - BASE + n]
            self.assertEqual(self.a6.count(sig), 0)

    def test_limits_do_not_claim_silent_link(self):
        text = " ".join(self.d["limits"])
        self.assertIn("NO_VERIFICADO", text)
        self.assertIn("NO es por si mismo el modo silent", text)


if __name__ == "__main__":
    unittest.main()
