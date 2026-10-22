"""S206 — Test que falla: tabla completa de registros IMX210 vs IMX235.

Hipótesis (una falla documenta la brecha; las otras confirman hechos de bytes):
  H1: Existe un mapeo 1:1 de direcciones de registro IMX210 -> IMX235.
      -> FALLA (S57-D.5: no hay correspondencia por dirección).
  H2: rec_map IMX210 tiene 119 registros sombra (hecho de bytes, S56/S57).
  H3: Matriz IMX235 tiene 35 registros x 34 modos (hecho de bytes, S57).
"""
import json
import struct
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
A6000 = ROOT / 'firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin'
A7S   = ROOT / 'firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin'
B = 0x43541000

def u16(d, a): return struct.unpack_from('<H', d, a - B)[0]
def u32(d, a): return struct.unpack_from('<I', d, a - B)[0]

class ImxRegisterTable(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d6 = A6000.read_bytes()
        cls.d7 = A7S.read_bytes()
        # rec_map IMX210 (S56/S57, vigente)
        rm = json.loads((ROOT / 'analysis/s56/rec_map.json').read_text())
        cls.imx210 = {e['rec']: e for e in rm}
        # matriz IMX235 (S57)
        mt = [u32(cls.d7, 0x43fee370 + 4 * i) for i in range(34)]
        cls.imx235_modes = mt
        rows = []
        a = 0x43fee598
        while True:
            p = u32(cls.d7, a)
            if not p or not (B < p < B + len(cls.d7)):
                break
            raw = cls.d7[p - 4 - B:p + 1 - B].hex()
            if raw[:2] in ('81', '83'):
                rows.append({'ptr': p, 'dev': raw[:2], 'dir': u16(cls.d7, p - 2),
                                 'init': cls.d7[p - B],
                                 'vals': list(cls.d7[a + 4 - B:a + 4 + 34 - B])})
            a += 40
        cls.imx235_rows = rows

    def test_imx210_has_119_registers(self):
        self.assertEqual(len(self.imx210), 119)

    def test_imx235_has_35_registers_34_modes(self):
        self.assertEqual(len(self.imx235_modes), 34)
        self.assertEqual(len(self.imx235_rows), 35)

    def test_no_address_1to1_mapping(self):
        """H1 (brecha): no hay mapeo 1:1 de direcciones IMX210 -> IMX235."""
        addrs210 = {int(r, 0) for r in self.imx210}
        addrs235 = {r['ptr'] for r in self.imx235_rows}
        overlap = addrs210 & addrs235
        # Esperado: solapamiento vacio (esquemas de direccion distinto)
        self.assertEqual(overlap, set(), overlap)

if __name__ == '__main__':
    unittest.main(verbosity=2)
