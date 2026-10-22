"""S206 — Validación de la tabla completa de registros IMX210 vs IMX235.

Comprueba que full_table.json (generado por analysis/s206_imx210_imx235_full_table/full_table.py)
contiene los 119 registros IMX210, 35 registros IMX235, 34 modos, y la
clasificación esperada (0 idénticos, 119 distintos, 0 ausentes-en-A6000,
sin solapamiento de direcciones).
"""
import json
import struct
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
A7S = ROOT / 'firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin'
B = 0x43541000

def u32(d, a): return struct.unpack_from('<I', d, a - B)[0]

class S206FullTable(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        p = ROOT / 'analysis/s206_imx210_imx235_full_table/full_table.json'
        cls.t = json.loads(p.read_text())
        cls.regs = cls.t['registros']

    def test_119_imx210_registers(self):
        self.assertEqual(self.t['imx210_registers'], 119)
        self.assertEqual(len(self.regs), 119)

    def test_35_imx235_registers_34_modes(self):
        self.assertEqual(self.t['imx235_registers'], 35)
        self.assertEqual(len(self.t['imx235_modes']), 34)

    def test_classification_counts(self):
        self.assertEqual(self.t['resumen']['identicos'], 0)
        self.assertEqual(self.t['resumen']['distintos'], 119)
        self.assertEqual(self.t['resumen']['ausentes_en_a6000'], 0)

    def test_all_distinct(self):
        for r in self.regs:
            self.assertEqual(r['clasificacion'], 'DISTINTO')
            self.assertFalse(r['tiene_equivalente_imx235'])

    def test_subsystem_counts(self):
        n_time = sum(1 for r in self.regs if r['subsistema'] == 'Temporización de exposición')
        n_mode = sum(1 for r in self.regs if r['subsistema'] == 'Selección de modo de lectura')
        self.assertEqual(n_time, 6, 'ID3-ID8 svd/shd/spl')
        self.assertEqual(n_mode, 2, 'ID1 duplicado A (0x4401ca2c) y B (0x4401c734)')

    def test_imx235_silent_modes(self):
        mt = self.t['imx235_modes']
        self.assertIn(0x4e, mt)
        self.assertIn(0x4f, mt)
        self.assertEqual(mt.index(0x4e), 29)
        self.assertEqual(mt.index(0x4f), 30)

    def test_no_address_overlap(self):
        # corroborado contra bytes: direcciones IMX210 (rec_map) vs IMX235 (matriz)
        (ROOT / 'firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin').read_bytes()
        d7 = A7S.read_bytes()
        addrs210 = {int(r['rec'], 0) for r in self.regs}
        addrs235 = set()
        a = 0x43fee598
        while True:
            p = u32(d7, a)
            if not p or not (B < p < B + len(d7)):
                break
            raw = d7[p - 4 - B:p + 1 - B].hex()
            if raw[:2] in ('81', '83'):
                addrs235.add(p)
            a += 40
        self.assertEqual(addrs210 & addrs235, set(), addrs210 & addrs235)

    def test_sha256_present(self):
        self.assertEqual(len(self.t['imx210_sha256']), 64)
        self.assertEqual(len(self.t['imx235_sha256']), 64)

if __name__ == '__main__':
    unittest.main(verbosity=2)
