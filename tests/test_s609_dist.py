#!/usr/bin/env python3
"""Unit tests for S609 CAMERA_IS/DIST module analysis."""
import json
import unittest
from pathlib import Path


class TestS609DIST(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data_path = Path(__file__).parent.parent / "analysis" / "s609_dist" / "dist.json"
        with open(cls.data_path, "r") as f:
            cls.data = json.load(f)

    def test_trace_count(self):
        self.assertEqual(self.data['traces'], 5)
        self.assertEqual(len(self.data['trace_strings']), 5)

    def test_all_traces_have_prefix(self):
        for ts in self.data['trace_strings']:
            self.assertTrue(ts['text'].startswith('[CAMERA_IS][DIST]: '),
                          f"Trace missing prefix: {ts['text']}")

    def test_prefix_length(self):
        self.assertEqual(self.data['prefix_length'], 19)
        self.assertEqual(self.data['prefix'], '[CAMERA_IS][DIST]: ')

    def test_differential_a6000(self):
        self.assertEqual(self.data['differential']['a6000_fw321']['token_count'], 5)
        self.assertEqual(self.data['differential']['a6000_fw321']['parent_token_count'], 14)

    def test_differential_a7s(self):
        self.assertEqual(self.data['differential']['a7s_fw320']['token_count'], 0)
        self.assertEqual(self.data['differential']['a7s_fw320']['parent_token_count'], 0)

    def test_differential_a6300(self):
        self.assertEqual(self.data['differential']['a6300_fw201']['token_count'], 0)
        self.assertEqual(self.data['differential']['a6300_fw201']['parent_token_count'], 0)

    def test_shutter_line_negative(self):
        self.assertEqual(self.data['shutter_line'], "NEGATIVO ACOTADO")

    def test_logger_dual(self):
        vs = self.data.get('verification_status', {})
        ld = vs.get('logger_dual', {})
        self.assertEqual(ld.get('status'), 'NO_VERIFICADO',
                         'logger_dual no es NO_VERIFICADO')

    def test_global_logger(self):
        self.assertEqual(self.data['global_logger'], "0x43902718")

    def test_trace_addresses_sorted(self):
        addrs = [int(ts['vaddr'], 16) for ts in self.data['trace_strings']]
        self.assertEqual(addrs, sorted(addrs), "Trace addresses not sorted")

    def test_key_functions_present(self):
        texts = [ts['text'] for ts in self.data['trace_strings']]
        self.assertTrue(any('MakeDistCorPrm' in t for t in texts))
        self.assertTrue(any('CnvPosInvDistCorr' in t for t in texts))
        self.assertTrue(any('MakeDistRawAppliTag' in t for t in texts))
        self.assertTrue(any('prm=null' in t for t in texts))
        self.assertTrue(any('inv1' in t for t in texts))
        self.assertTrue(any('inv2' in t for t in texts))


if __name__ == "__main__":
    unittest.main()
