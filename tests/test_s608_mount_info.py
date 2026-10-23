#!/usr/bin/env python3
"""Unit tests for S608 MOUNT_INFO module analysis."""
import json
import unittest
from pathlib import Path


class TestS608MOUNTINFO(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data_path = Path(__file__).parent.parent / "analysis" / "s608_mount_info" / "mount_info.json"
        with open(cls.data_path, "r") as f:
            cls.data = json.load(f)

    def test_trace_count(self):
        self.assertEqual(self.data['traces'], 6)
        self.assertEqual(len(self.data['trace_strings']), 6)

    def test_all_traces_have_prefix(self):
        for ts in self.data['trace_strings']:
            self.assertTrue(ts['text'].startswith('[MOUNT_INFO]: '),
                          f"Trace missing prefix: {ts['text']}")

    def test_all_cores_have_bl_prefix(self):
        for ts in self.data['trace_strings']:
            self.assertTrue(ts['core_text'].startswith('[BL]'),
                          f"Core missing [BL] prefix: {ts['core_text']}")

    def test_composite_structure(self):
        for ts in self.data['trace_strings']:
            expected = '[MOUNT_INFO]: ' + ts['core_text']
            self.assertEqual(ts['text'], expected,
                           f"Composite mismatch: {ts['text']} != {expected}")

    def test_prefix_lengths(self):
        self.assertEqual(self.data['prefix_length'], 14)
        self.assertEqual(self.data['prefix'], '[MOUNT_INFO]: ')
        self.assertEqual(self.data['core_prefix_length'], 3)
        self.assertEqual(self.data['core_prefix'], '[BL]')
        self.assertEqual(self.data['composite_prefix_length'], 15)

    def test_differential_a6000(self):
        self.assertEqual(self.data['differential']['a6000_fw321']['mount_info_token_count'], 6)
        self.assertEqual(self.data['differential']['a6000_fw321']['bl_token_count'], 6)

    def test_differential_a7s(self):
        self.assertEqual(self.data['differential']['a7s_fw320']['mount_info_token_count'], 0)
        self.assertEqual(self.data['differential']['a7s_fw320']['bl_token_count'], 70)

    def test_differential_a6300(self):
        self.assertEqual(self.data['differential']['a6300_fw201']['mount_info_token_count'], 0)
        self.assertEqual(self.data['differential']['a6300_fw201']['bl_token_count'], 70)

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
        self.assertTrue(any('LIF Command Change' in t for t in texts))
        self.assertTrue(any('UUD CallBack' in t for t in texts))
        self.assertTrue(any('MSGID_GET_VERSION' in t for t in texts))
        self.assertTrue(any('MSGID_GET_FORCE_FIRMUP' in t for t in texts))
        self.assertTrue(any('MSGID_FIRM_UP_REQ' in t for t in texts))
        self.assertTrue(any('MSGID_PREPARE_UPDATE' in t for t in texts))
        self.assertTrue(any('MSGID_UNPLUG_USB' in t for t in texts))


if __name__ == "__main__":
    unittest.main()
