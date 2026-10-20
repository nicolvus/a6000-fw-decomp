"""S60: comprueba bytes y ejecución offline del transporte de temporización."""
import sys
import unittest
from pathlib import Path

from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "analysis/s60/sol"))
import trace_payload


class PayloadTransport(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = trace_payload.probe()

    def test_binary_and_dispatch_targets(self):
        self.assertEqual(self.result["sha256"], trace_payload.SHA)
        self.assertEqual(self.result["case_targets"]["4"], "0x43806c24")
        self.assertEqual(self.result["case_targets"]["10"], "0x43806d02")

    def test_direct_calls_link_request_reply_and_receiver(self):
        binary = trace_payload.data("A6000")
        disassembler = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
        for site, target in ((0x43806C06, 0x43B00FE6),
                             (0x43806CE6, 0x43B00F62),
                             (0x43806E54, 0x438069F0)):
            with self.subTest(site=hex(site)):
                instruction = next(disassembler.disasm(
                    binary[site - trace_payload.B:site - trace_payload.B + 4], site,
                ))
                self.assertEqual((instruction.mnemonic, instruction.op_str),
                                 ("bl", f"#{target:#x}"))

    def test_publish_then_stage_next_value(self):
        result = self.result
        self.assertEqual(result["published_dd0"], result["injected_source"][0x1C * 2:0x34 * 2])
        self.assertEqual(result["staged_d64"], result["injected_next"])
        self.assertEqual(result["staged_c50"], result["injected_next"])

    def test_case_four_payload_and_receiver(self):
        result = self.result
        self.assertEqual(result["case4"]["pointer"], hex(trace_payload.OBJ + 0xD60))
        self.assertEqual(result["case4"]["size"], 0x54)
        self.assertEqual(result["case4"]["type"], 4)
        self.assertEqual(result["case4"]["payload_4"], result["receiver_4"])
        self.assertEqual(result["case4"]["payload_20"], result["injected_next"][0x1C * 2:0x34 * 2])
        self.assertEqual(result["published_4_dd0"], result["case4"]["payload_20"])

    def test_case_ten_payload_and_receiver(self):
        result = self.result
        self.assertEqual(result["case10"]["pointer"], hex(trace_payload.OBJ + 0x6C0))
        self.assertEqual(result["case10"]["size"], 0x5E0)
        self.assertEqual(result["case10"]["type"], 10)
        self.assertEqual(result["case10"]["payload_590"], result["receiver_10"])
        self.assertEqual(result["case10"]["payload_5ac"], result["injected_next"][0x1C * 2:0x34 * 2])
        self.assertEqual(result["published_10_dd0"], result["case10"]["payload_5ac"])

    def test_no_unexpected_stubs_and_synthetic_label(self):
        self.assertEqual(self.result["stubbed"], {})
        self.assertEqual(self.result["receiver_stubs"], [{}, {}, {}, {}])
        self.assertEqual(self.result["input_kind"], "sintético")
        self.assertEqual(self.result["reachability"], "NO VERIFICADO")


if __name__ == "__main__":
    unittest.main()
