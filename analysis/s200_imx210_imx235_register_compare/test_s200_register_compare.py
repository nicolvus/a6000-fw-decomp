"""S200/S201/S203 — Reproducción que falla: comparación funcional de registros y
la vía de obturador silencioso IMX210 (A6000) vs IMX235 (A7S).

Hipótesis (cada una verificada contra bytes de av-cam.bin de ambos modelos):
  H1: la A7S declara modos de lectura dedicados a Silent (columnas 0x4e/0x4f de
      su matriz 0x43fee598); el IMX210 de la A6000 tiene 13 modos y sin 0x4e/0x4f
      (S57-D vigente: SetMode devuelve error 2 para ellos).
  H2: la A7S selecciona Silent mediante drive mode / selector `tipo` (tipo==2 ->
      0x4e/0x4f en 0x43826d58) y su tabla de timings, NO mediante CheckSet* de
      LiroSeq (S169: 0/0 en A6000 y A7S).
  H3: no hay mensaje a Liro que active el obturador electrónico en A7S (S174:
      los …ForLiro de A6000/A7S están en lista de rechazo).
"""
import struct
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
A6000 = ROOT / 'firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin'
A7S   = ROOT / 'firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin'
B = 0x43541000

def u16(d, a): return struct.unpack_from('<H', d, a - B)[0]
def u32(d, a): return struct.unpack_from('<I', d, a - B)[0]

class ImxComparison(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d_a6000 = A6000.read_bytes()
        cls.d_a7s = A7S.read_bytes()
        tab = [u32(cls.d_a6000, 0x43fe995c + 4 * i) for i in range(119)]
        cls.imx210 = {p: struct.unpack_from('<H', cls.d_a6000, p - B)[0] for p in tab}
        mt = [u32(cls.d_a7s, 0x43fee370 + 4 * i) for i in range(34)]
        cls.imx235_modes = mt
        rows = []
        a = 0x43fee598
        while True:
            p = u32(cls.d_a7s, a)
            if not p or not (B < p < B + len(cls.d_a7s)):
                break
            raw = cls.d_a7s[p - 4 - B:p + 1 - B].hex()
            if raw[:2] in ('81', '83'):
                rows.append({'ptr': p, 'dev': raw[:2], 'dir': u16(cls.d_a7s, p - 2),
                                 'vals': list(cls.d_a7s[a + 4 - B:a + 4 + 34 - B])})
            a += 40
        cls.imx235_rows = rows
        # Selector A7S 0x43826d58 (tipo==2 -> silent 0x4e/0x4f)
        sel = cls.d_a7s[0x43826d58 - B : 0x43826db0 - B]
        cls.sel_bytes = sel

    # ---- H1: modos de lectura ----
    def test_imx235_has_silent_modes_0x4e_0x4f(self):
        self.assertEqual(len(self.imx235_modes), 34)
        self.assertIn(0x4e, self.imx235_modes)
        self.assertIn(0x4f, self.imx235_modes)

    def test_imx235_silent_column_indices(self):
        # 0x4e en índice 29, 0x4f en índice 30 de la tabla de 34 modos (columnas)
        self.assertEqual(self.imx235_modes.index(0x4e), 29)
        self.assertEqual(self.imx235_modes.index(0x4f), 30)

    # ---- H2: selector de drive mode A7S (bytes) ----
    def test_a7s_selector_encodes_silent_tipo2(self):
        sel = self.sel_bytes
        # tipo==2: cmp r2,#2 (Thumb: 0x02 0x2a) en 0x43826d64 => drive mode 2 = Silent
        self.assertIn(b'\x02\x2a', sel, 'falta cmp r2,#2 (tipo==2 -> silent)')
        # retornos inmediatos de modo 0x4e / 0x4f / 0x0b / 0x35 / 0x17 / 0x0c
        for v in (0x4e, 0x4f, 0x0b, 0x35, 0x17, 0x0c):
            self.assertIn(bytes([v, 0x20]), sel, f'falta movs r0,#0x{v:02x} en el selector')

    # ---- H2 / H3: ausencia de CheckSet* y ForLiro obturador ----
    def test_no_checkset_shutter(self):
        for name, d in (('A6000', self.d_a6000), ('A7S', self.d_a7s)):
            self.assertNotIn(b'CheckSetSilentShutterMode', d, name)
            self.assertNotIn(b'CheckSetShutDrive', d, name)
            self.assertNotIn(b'SilentShutterMode', d, name)
            self.assertNotIn(b'shutterType', d, name)

    def test_no_shutter_forliro_message(self):
        for name, d in (('A6000', self.d_a6000), ('A7S', self.d_a7s)):
            self.assertNotIn(b'SetShutterTypeForLiro', d, name)

    # ---- Estructura de registros ----
    def test_imx210_register_vector(self):
        self.assertEqual(len(self.imx210), 119)
        self.assertEqual(self.imx210[0x4401ca2c], 1)  # ID1 A
        self.assertEqual(self.imx210[0x4401c734], 1)  # ID1 B

    def test_imx235_register_range_and_devices(self):
        self.assertGreaterEqual(len(self.imx235_rows), 30)
        devs = {r['dev'] for r in self.imx235_rows}
        self.assertTrue(devs <= {'81', '83'}, devs)
        dirs = {r['dir'] for r in self.imx235_rows}
        self.assertTrue(all(0 <= d <= 0x00cf for d in dirs), dirs)

if __name__ == '__main__':
    unittest.main(verbosity=2)
