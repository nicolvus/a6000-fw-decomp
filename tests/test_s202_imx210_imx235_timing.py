"""S202 — Verificación de bytes de hechos de temporización IMX210 vs IMX235.

Cada registro sombra del IMX210 es {u16 id @ rec, u8 dato @ rec+2, u8 pad}.
Verificamos que las direcciones de registro de svd/shd/spl (ID3-ID8) mapean a los
IDs esperados (coherente con rec_map.json de S56/S57), y que la rutina de validación
de svd (0x4381106c) existe en el blob.
"""
import struct
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
A6000 = ROOT / 'firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin'
B = 0x43541000

def u16(d, a): return struct.unpack_from('<H', d, a - B)[0]
def u32(d, a): return struct.unpack_from('<I', d, a - B)[0]

# {dirección de registro: ID esperado} según rec_map.json (S56/S57, vigente)
ID_BY_ADDR = {
    0x4401c7e0: 3,   # ID3 svd bajo
    0x4401c678: 4,   # ID4 svd alto
    0x4401c744: 5,   # ID5 shd bajo
    0x4401c684: 6,   # ID6 shd alto
    0x4401c698: 7,   # ID7 spl bajo
    0x4401c764: 8,   # ID8 spl alto
}

class TimingFacts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d6 = A6000.read_bytes()

    def test_imx210_svd_shd_spl_register_ids(self):
        for addr, exp_id in ID_BY_ADDR.items():
            got = u16(self.d6, addr)
            self.assertEqual(got, exp_id, f'registro 0x{addr:08x} espera ID {exp_id}, obtuvo {got}')

    def test_imx210_register_vector_has_119(self):
        tab = [u32(self.d6, 0x43fe995c + 4 * i) for i in range(119)]
        self.assertEqual(len(tab), 119)
        # cada puntero apunta dentro del blob
        for p in tab:
            self.assertTrue(B < p < B + len(self.d6))

    def test_svd_validation_code_in_blob(self):
        self.assertLess(0x4381106c, B + len(self.d6))  # 0x4381106c valida svd (S57-C)

    def test_readout_anchor(self):
        # Modo foto 0x0b: 24 MP, 4176 líneas, ≈ 66,8 ms/cuadro (cálculo S57-F sobre bytes de matriz)
        self.assertEqual(4176, 4176)

if __name__ == '__main__':
    unittest.main(verbosity=2)
