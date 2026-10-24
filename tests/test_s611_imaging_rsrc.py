"""Unit tests for S611 IMAGING_RSRC module analysis."""
import json
import unittest
from pathlib import Path


class TestS611IMAGINGRSRC(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data_path = Path(__file__).parent.parent / "analysis" / "s611_imaging_rsrc" / "imaging_rsrc.json"
        with open(cls.data_path, "r") as f:
            cls.data = json.load(f)

    def test_trace_count(self):
        self.assertEqual(self.data['traces'], 5)
        self.assertEqual(len(self.data['trace_strings']), 5)

    def test_all_traces_have_prefix(self):
        for ts in self.data['trace_strings']:
            self.assertTrue(ts['text'].startswith('[IMAGING_RSRC]: '),
                          f"Trace missing prefix: {ts['text']}")

    def test_all_cores_have_golfshot_prefix(self):
        for ts in self.data['trace_strings']:
            self.assertTrue(ts['core_text'].startswith('[GOLFSHOT]'),
                          f"Core missing [GOLFSHOT] prefix: {ts['core_text']}")

    def test_composite_structure(self):
        for ts in self.data['trace_strings']:
            expected = '[IMAGING_RSRC]: ' + ts['core_text']
            self.assertEqual(ts['text'], expected,
                           f"Composite mismatch: {ts['text']} != {expected}")

    def test_prefix_lengths(self):
        self.assertEqual(self.data['prefix_length'], 16)
        self.assertEqual(self.data['prefix'], '[IMAGING_RSRC]: ')
        self.assertEqual(self.data['core_prefix_length'], 10)
        self.assertEqual(self.data['core_prefix'], '[GOLFSHOT]')
        self.assertEqual(self.data['composite_prefix_length'], 26)

    def test_differential_a6000(self):
        self.assertEqual(self.data['differential']['a6000_fw321']['imaging_rsrc_token_count'], 5)
        self.assertEqual(self.data['differential']['a6000_fw321']['golfshot_token_count'], 5)

    def test_differential_a7s(self):
        self.assertEqual(self.data['differential']['a7s_fw320']['imaging_rsrc_token_count'], 0)
        self.assertEqual(self.data['differential']['a7s_fw320']['golfshot_token_count'], 5)

    def test_differential_a6300(self):
        self.assertEqual(self.data['differential']['a6300_fw201']['imaging_rsrc_token_count'], 0)
        self.assertEqual(self.data['differential']['a6300_fw201']['golfshot_token_count'], 5)

    def test_shutter_line_negative(self):
        self.assertEqual(self.data['shutter_line'], "NEGATIVO ACOTADO")

    def test_logger_dual(self):
        vs = self.data.get('verification_status', {})
        ld = vs.get('logger_dual', {})
        self.assertEqual(ld.get('status'), 'VERIFICADO_ESTATICO')
        self.assertTrue(ld.get('verified'))

    def test_global_logger(self):
        self.assertEqual(self.data['global_logger'], "0x43902718")

    def test_trace_addresses_sorted(self):
        addrs = [int(ts['vaddr'], 16) for ts in self.data['trace_strings']]
        self.assertEqual(addrs, sorted(addrs), "Trace addresses not sorted")

    def test_key_functions_present(self):
        texts = [ts['text'] for ts in self.data['trace_strings']]
        cores = [ts['core_text'] for ts in self.data['trace_strings']]
        all_texts = texts + cores
        self.assertTrue(any('SA_LPF' in t for t in all_texts))
        self.assertTrue(any('SA_BGEST' in t for t in all_texts))
        self.assertTrue(any('SA_SSP' in t for t in all_texts))
        self.assertTrue(any('correctSndDetResult' in t for t in all_texts))
        self.assertTrue(any('vfc2indx' in t for t in all_texts))
        self.assertTrue(any('Shot Timing Transform Error' in t for t in all_texts))
        self.assertTrue(any('SoundDetBuff' in t for t in all_texts))


if __name__ == "__main__":
    unittest.main()
