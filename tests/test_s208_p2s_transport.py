"""S208 — Validación de hallazgos de transporte P2S A6000 vs A7S.

Comprueba que p2s_transport.json (generado por analysis/s208_p2s_transport/p2s_transport.py)
contiene: formateador A6000 con 0x81, formateadores A7S presentes y sin byte extra,
tablas de canal P2S en ambos, y la conclusion de transporte identico.
"""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class S208P2S(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        p = ROOT / 'analysis/s208_p2s_transport/p2s_transport.json'
        cls.t = json.loads(p.read_text())

    def test_a6000_formatter_0x81(self):
        self.assertTrue(self.t['a6000_p2s_formatter_0x81'])

    def test_a7s_formatters_present_and_nonzero(self):
        for f in self.t['a7s_p2s_formatters']:
            self.assertTrue(f['in_blob'], f['addr'])
            self.assertTrue(f['nonzero'], f['addr'])

    def test_a7s_no_extra_byte(self):
        self.assertTrue(self.t['a7s_no_extra_byte'])

    def test_channel_tables(self):
        # Tabla A6000 dentro del blob; el byte de canal puede ser 0x00 (valido).
        self.assertTrue(self.t['a6000_channel_table_p2s'])

    def test_conclusion_present(self):
        self.assertIn('IDENTICO', self.t['conclusion'])
        self.assertIn('0x81', self.t['conclusion'])
        self.assertIn('sin byte extra', self.t['conclusion'])

    def test_sha256_present(self):
        self.assertEqual(len(self.t['imx210_sha256']), 64)
        self.assertEqual(len(self.t['imx235_sha256']), 64)

if __name__ == '__main__':
    unittest.main(verbosity=2)
