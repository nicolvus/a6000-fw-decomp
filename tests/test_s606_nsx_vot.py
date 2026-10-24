#!/usr/bin/env python3
"""Unit tests for S606 NSX_VOT module analysis."""
import json
import unittest
from pathlib import Path


class TestS606NSXVOT(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data_path = Path(__file__).parent.parent / "analysis" / "s606_nsx_vot" / "nsx_vot.json"
        with open(cls.data_path, "r") as f:
            cls.data = json.load(f)

    def test_trace_count(self):
        self.assertEqual(self.data['traces'], 7)
        self.assertEqual(len(self.data['trace_strings']), 7)

    def test_all_traces_have_prefix(self):
        for ts in self.data['trace_strings']:
            self.assertTrue(ts['text'].startswith('[NSX_VOT]: '),
                          f"Trace missing prefix: {ts['text']}")

    def test_all_twins_have_trk_prefix(self):
        for ts in self.data['trace_strings']:
            self.assertTrue(ts['twin_text'].startswith('[TRK]: '),
                          f"Twin missing prefix: {ts['twin_text']}")

    def test_core_text_matches(self):
        for ts in self.data['trace_strings']:
            core_nsx = ts['text'][10:]  # after "[NSX_VOT]: "
            core_trk = ts['twin_text'][6:]  # after "[TRK]: "
            self.assertEqual(core_nsx, core_trk,
                           f"Core mismatch: '{core_nsx}' != '{core_trk}'")

    def test_prefix_length(self):
        self.assertEqual(self.data['prefix_length'], 11)
        self.assertEqual(self.data['prefix'], '[NSX_VOT]: ')
        self.assertEqual(self.data['twin_prefix_length'], 6)
        self.assertEqual(self.data['twin_prefix'], '[TRK]: ')

    def test_differential_a6000(self):
        self.assertEqual(self.data['differential']['a6000_fw321']['nsx_vot_token_count'], 7)
        self.assertEqual(self.data['differential']['a6000_fw321']['trk_token_count'], 7)

    def test_differential_a7s(self):
        self.assertEqual(self.data['differential']['a7s_fw320']['nsx_vot_token_count'], 0)
        self.assertEqual(self.data['differential']['a7s_fw320']['trk_token_count'], 7)

    def test_differential_a6300(self):
        self.assertEqual(self.data['differential']['a6300_fw201']['nsx_vot_token_count'], 0)
        self.assertEqual(self.data['differential']['a6300_fw201']['trk_token_count'], 7)

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

    def test_twin_addresses_sorted(self):
        addrs = [int(ts['twin_vaddr'], 16) for ts in self.data['trace_strings']]
        self.assertEqual(addrs, sorted(addrs), "Twin addresses not sorted")

    def test_key_functions_present(self):
        texts = [ts['text'] for ts in self.data['trace_strings']]
        twin_texts = [ts['twin_text'] for ts in self.data['trace_strings']]
        all_texts = texts + twin_texts
        # Check for key function names in traces
        self.assertTrue(any('almhdl' in t for t in all_texts))
        self.assertTrue(any('bt stop error' in t for t in all_texts))
        self.assertTrue(any('osal_alloc_timer' in t for t in all_texts))
        self.assertTrue(any('osal_free_timer' in t for t in all_texts))
        self.assertTrue(any('osal_set_timer' in t for t in all_texts))
        self.assertTrue(any('osal_can_timer' in t for t in all_texts))
        self.assertTrue(any('handle alloc again' in t for t in all_texts))
        self.assertTrue(any('handle NULL' in t for t in all_texts))


if __name__ == "__main__":
    unittest.main()
