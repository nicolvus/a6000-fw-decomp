"""S207 — Validación de hallazgos de fin de integración / segunda cortina IMX235 vs IMX210.

Comprueba que full_eoi.json (generado por analysis/s207_imx235_end_of_integration/full_eoi.py)
contiene: sin cadenas largas de fin de integración en A7S/A6000, 35 registros IMX235,
y la conclusión de que ambos carecen de operación de fin de integración identificada.
"""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class S207EOI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        p = ROOT / 'analysis/s207_imx235_end_of_integration/full_eoi.json'
        cls.t = json.loads(p.read_text())

    def test_no_long_eoi_strings_in_either_model(self):
        self.assertEqual(self.t['eoi_strings_a7s_long'], [])
        self.assertEqual(self.t['eoi_strings_a6000_long'], [])

    def test_imx235_register_count(self):
        self.assertEqual(self.t['imx235_registers'], 35)

    def test_no_dedicated_eoi_register(self):
        self.assertFalse(self.t['imx235_has_eoi_dedicated_register'])

    def test_exposure_timer_end_no_rewrite(self):
        self.assertTrue(self.t['exposure_timer_end_no_register_rewrite'])

    def test_conclusion_present(self):
        self.assertIn('No hay registro ni mecanismo', self.t['conclusion'])
        self.assertIn('NO_VERIFICADO', self.t['conclusion'])

    def test_sha256_present(self):
        self.assertEqual(len(self.t['imx210_sha256']), 64)
        self.assertEqual(len(self.t['imx235_sha256']), 64)

if __name__ == '__main__':
    unittest.main(verbosity=2)
