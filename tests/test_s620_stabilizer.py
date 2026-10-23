#!/usr/bin/env python3
"""Unit tests for S620 STABILIZER module analysis."""
import json
import unittest
from pathlib import Path


class TestS620STABILIZER(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data_path = Path(__file__).parent.parent / "analysis" / "s620_stabilizer" / "stabilizer.json"
        with open(cls.data_path, "r") as f:
            cls.data = json.load(f)

    def test_trace_count(self):
        self.assertEqual(self.data['traces'], 3)
        self.assertEqual(len(self.data['trace_strings']), 3)

    def test_all_traces_have_prefix(self):
        for ts in self.data['trace_strings']:
            self.assertTrue(ts['text'].startswith('[CAMERA_IS][AS]: [STABILIZER][AS]'),
                          f"Trace missing prefix: {ts['text']}")

    def test_prefix_length(self):
        self.assertEqual(self.data['prefix_length'], 33)
        self.assertEqual(self.data['prefix'], '[CAMERA_IS][AS]: [STABILIZER][AS]')

    def test_differential_a6000(self):
        self.assertEqual(self.data['differential']['a6000_fw321']['token_count'], 3)

    def test_differential_a7s(self):
        self.assertEqual(self.data['differential']['a7s_fw320']['token_count'], 0)

    def test_differential_a6300(self):
        self.assertEqual(self.data['differential']['a6300_fw201']['token_count'], 0)

    def test_shutter_line_negative(self):
        self.assertEqual(self.data['shutter_line'], "NEGATIVO ACOTADO")

    def test_logger_dual(self):
        self.assertTrue(self.data['logger_dual'])

    def test_global_logger(self):
        self.assertEqual(self.data['global_logger'], "0x43902718")

    def test_trace_addresses_sorted(self):
        addrs = [int(ts['vaddr'], 16) for ts in self.data['trace_strings']]
        self.assertEqual(addrs, sorted(addrs), "Trace addresses not sorted")

    def test_key_functions_present(self):
        texts = [ts['text'] for ts in self.data['trace_strings']]
        self.assertTrue(any('osal_reg_sync_msg_queue_cb' in t for t in texts))
        self.assertTrue(any('upm_get_hcrn_ura' in t for t in texts))
        self.assertTrue(any('osal_unreg_sync_msg_queue_cb' in t for t in texts))


if __name__ == "__main__":
    unittest.main()
