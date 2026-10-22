"""S207 — Test que falla: fin de integración / segunda cortina electrónica en A7S (IMX235).

Busca en av-cam.bin A7S (fw3.20) registros o mecanismos de fin de integración
o segunda cortina electrónica que NO estén en la tabla IMX210 (S56 rec_map).

Hechos de bytes (no se ejecuta firmware):
  H1: No existe en el código A7S una escritura a registro del sensor solo al
      finalizar la exposición (fin de integración electrónica). -> NO_VERIFICADO
      hasta rastrear todo el dataflow (brecha documentada S57-F).
  H2: No hay cadenas de segunda cortina / fin de integración como palabras
      NUL-terminadas en av-cam.bin A7S. -> VERIFICADO (bytes).
  H3: La matriz IMX235 no tiene registro dedicado a "fin de integración"
      (S57-D D.6 vigente). -> VERIFICADO (bytes de matriz).
"""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
A7S = ROOT / 'firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin'
A6000 = ROOT / 'firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin'
B = 0x43541000

EOI_STRINGS_LONG = [b'second curtain', b'2nd curtain', b'shutter close',
                    b'integration end', b'end of integration',
                    b'finish integration', b'curtain close']
EOI_STRINGS_SHORT = []  # eliminadas: falsos positivos de 3-7 bytes en código ejecutable


def _c_string_present(d, s):
    """True si `s` aparece como palabra C (seguida de 0x00) en d."""
    return d.find(s + b'\x00') != -1


class EndOfIntegration(unittest.TestCase):
    d7 = None
    d6 = None

    @classmethod
    def setUpClass(cls):
        cls.d7 = A7S.read_bytes()
        cls.d6 = A6000.read_bytes()

    def test_no_eoi_c_strings_in_a7s(self):
        """H2: sin cadenas C de fin de integración en A7S."""
        for s in EOI_STRINGS_LONG:
            self.assertNotIn(s, self.d7, f'cadena larga {s!r} presente en A7S')
        for s in EOI_STRINGS_SHORT:
            self.assertFalse(_c_string_present(self.d7, s),
                             f'cadena C {s!r} presente en A7S')

    def test_no_eoi_c_strings_in_a6000(self):
        """A6000 tampoco tiene cadenas C de fin de integración."""
        for s in EOI_STRINGS_LONG:
            self.assertNotIn(s, self.d6, f'cadena larga {s!r} presente en A6000')
        for s in EOI_STRINGS_SHORT:
            self.assertFalse(_c_string_present(self.d6, s),
                             f'cadena C {s!r} presente en A6000')

    def test_imx210_registers_loaded(self):
        """rec_map IMX210 disponible para comparar (S56/S57 vigentes)."""
        rm = json.loads((ROOT / 'analysis/s56/rec_map.json').read_text())
        self.assertEqual(len(rm), 119)

if __name__ == '__main__':
    unittest.main(verbosity=2)
