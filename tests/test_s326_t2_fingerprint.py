import json
import struct
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JSON = ROOT / "analysis/s326_t2_fingerprint/t2_silent_fingerprint.json"
BASE = 0x43541000
A7S = ROOT / ("firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/"
              "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin")


class T2Fingerprint(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d = json.loads(JSON.read_text())
        cls.a7 = A7S.read_bytes()
        cls.codes = [struct.unpack_from("<I", cls.a7, 0x43FEE370 + 4 * i - BASE)[0]
                     for i in range(34)]

    def row(self, base, pos):
        return [struct.unpack_from("<I", self.a7, base + 0x1C * pos + 4 * j - BASE)[0]
                for j in range(7)]

    def at(self, code):
        return self.row(0x43BBF2EC, self.codes.index(code))

    def test_three_tables_have_34_rows(self):
        for name, addr in (("T1", 0x43BBEB70), ("T3", 0x43BBEF34), ("T2", 0x43BBF2EC)):
            self.assertEqual(self.d["tables"][name]["base"], f"0x{addr:08x}")
            self.assertEqual(self.d["tables"][name]["rows"], 34)
        # T3 y T2 son contiguas: 34 filas de 0x1c
        self.assertEqual(0x43BBEF34 + 34 * 0x1C, 0x43BBF2EC)

    def test_t2_separates_silent_from_mechanical(self):
        self.assertEqual([j for j in range(7) if self.at(0x4E)[j] != self.at(0x4C)[j]], [5])
        self.assertEqual([j for j in range(7) if self.at(0x4F)[j] != self.at(0x4D)[j]], [5, 6])
        self.assertEqual([j for j in range(7) if self.at(0x4E)[j] != self.at(0x4F)[j]], [6])

    def test_field_values(self):
        self.assertEqual((self.at(0x4C)[5], self.at(0x4E)[5]), (0x3FF, 0))
        self.assertEqual((self.at(0x4D)[6], self.at(0x4F)[6]), (2, 3))
        self.assertEqual(sorted({self.at(c)[5] for c in self.codes}), [0, 0x3FF])

    def test_identical_pairs(self):
        self.assertEqual(self.at(0x4E), self.at(0x51))
        self.assertEqual(self.at(0x4F), self.at(0x50))
        self.assertEqual(self.at(0x4C), self.at(0x4D))

    def test_signature_groupings_are_not_silent_specific(self):
        # 0x3ff agrupa 0x13/0x1f con 0x4c/0x4d
        self.assertEqual(self.d["t2_signature"]["field14_0x3ff_rows"],
                         ["0x13", "0x1f", "0x4c", "0x4d"])
        # el valor 3 de +0x18 agrupa 0x0b/0x35 con 0x4f/0x50
        self.assertEqual(self.d["t2_signature"]["field18_3_rows"],
                         ["0x0b", "0x35", "0x4f", "0x50"])

    def test_t1_and_t3_are_constant_in_the_silent_range(self):
        t3 = {tuple(self.row(0x43BBEF34, p)) for p in range(27, 33)}
        self.assertEqual(len(t3), 1)
        t1_first = [self.row(0x43BBEB70, p)[0] for p in range(27, 33)]
        self.assertEqual(t1_first, [0, 0, 0, 0, 1, 1])

    def test_verdict(self):
        v = self.d["s204_verdict"]
        self.assertTrue(v["structure_reproduced"])
        self.assertFalse(v["numeric_labels_match"])
        self.assertIn("T2", v["table_identity"])


if __name__ == "__main__":
    unittest.main()
