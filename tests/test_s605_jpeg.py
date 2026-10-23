#!/usr/bin/env python3
"""Unit tests for S605 JPEG module analysis."""
import json
import unittest
from pathlib import Path


class TestS605JPEG(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data_path = Path(__file__).parent.parent / "analysis" / "s605_jpeg" / "jpeg.json"
        with open(cls.data_path, "r") as f:
            cls.data = json.load(f)

    def test_trace_count(self):
        self.assertEqual(self.data['traces'], 17)
        self.assertEqual(len(self.data['trace_strings']), 17)

    def test_all_traces_have_prefix(self):
        for ts in self.data['trace_strings']:
            self.assertTrue(ts['text'].startswith('[JPEG]: '),
                          f"Trace missing prefix: {ts['text']}")

    def test_prefix_length(self):
        self.assertEqual(self.data['prefix_length'], 7)
        self.assertEqual(self.data['prefix'], '[JPEG]: ')

    def test_differential_a6000(self):
        self.assertEqual(self.data['differential']['a6000_fw321']['token_count'], 17)

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

    def test_dgi_jpeg_symbols(self):
        self.assertEqual(self.data['dgi_jpeg_symbols'], 35)

    def test_trace_addresses_sorted(self):
        addrs = [int(ts['vaddr'], 16) for ts in self.data['trace_strings']]
        self.assertEqual(addrs, sorted(addrs), "Trace addresses not sorted")

    def test_key_functions_present(self):
        texts = [ts['text'] for ts in self.data['trace_strings']]
        # Check for key function names in traces
        self.assertTrue(any('cbJpegDebugOpen' in t for t in texts))
        self.assertTrue(any('cbJpegDebugClose' in t for t in texts))
        self.assertTrue(any('f_sa_dummy_send_msg' in t for t in texts))
        self.assertTrue(any('f_2open' in t for t in texts))
        self.assertTrue(any('f_2close' in t for t in texts))
        self.assertTrue(any('NormalOpen' in t for t in texts))
        self.assertTrue(any('SortOpen' in t for t in texts))
        self.assertTrue(any('TanzOpen' in t for t in texts))
        self.assertTrue(any('NormalClose' in t for t in texts))
        self.assertTrue(any('SortClose' in t for t in texts))


if __name__ == "__main__":
    unittest.main()