import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "analysis/s322_frame_format/frame_format.json"


class TestS322FrameFormat(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d = json.loads(DATA.read_text())

    def test_formatter_result_contract(self):
        contract = self.d["formatter"]["return_contract"]
        self.assertEqual(contract, {"success": 0, "rejected": 1, "full": 2})

    def test_byte_aligned_frame(self):
        frame = self.d["byte_aligned_frame"]
        self.assertEqual(frame["layout"], "81 | 03 | device | address8 | data8")
        self.assertEqual(frame["example"], "810381001c")

    def test_length_is_payload_after_length_byte(self):
        frame = self.d["byte_aligned_frame"]
        self.assertEqual(frame["length_value"], 3)
        self.assertEqual(frame["length_covers"], ["device", "address8", "data8"])

    def test_registers_are_not_coalesced(self):
        tx = self.d["existing_emulation"]
        self.assertEqual(tx["decoded_frames"], tx["registers"])
        self.assertTrue(tx["one_frame_per_register"])

    def test_mode_two_does_not_change_encoding(self):
        self.assertEqual(self.d["mode_effect"], "seleccion de lista y reintento; misma codificacion")

    def test_scope_stays_static(self):
        self.assertIn("NO_VERIFICADO", " ".join(self.d["limits"]))


if __name__ == "__main__":
    unittest.main()
