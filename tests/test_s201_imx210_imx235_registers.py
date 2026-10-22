"""S201 — Validación de la tabla de comparación de registros IMX210 vs IMX235.

Comprueba que compare.json (generado por analysis/s201_imx210_imx235_registers/compare.py)
contiene las 11 filas de subsistema con las clasificaciones esperadas y que las
evidencias de bytes (selector tipo==2, modos 0x4e/0x4f) coinciden con el blob.
"""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
A7S = ROOT / 'firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin'
B = 0x43541000

class S201CompareTable(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        p = ROOT / 'analysis/s201_imx210_imx235_registers/compare.json'
        cls.t = json.loads(p.read_text())
        cls.sub = {s['subsistema'] + '||' + s['campo']: s for s in cls.t['subsystems']}

    def test_eleven_subsystem_rows(self):
        self.assertEqual(len(self.t['subsystems']), 11)

    def test_classifications(self):
        self.assertEqual(sum(1 for s in self.t['subsystems'] if s['clasificacion'] == 'IDENTICO'), 4)
        self.assertEqual(sum(1 for s in self.t['subsystems'] if s['clasificacion'] == 'DISTINTO'), 7)
        self.assertEqual(sum(1 for s in self.t['subsystems'] if s['clasificacion'] == 'AUSENTE_EN_A6000'), 0)

    def test_imx235_silent_modes_in_matrix(self):
        mt = self.t['imx235_modes']
        self.assertIn(0x4e, mt)
        self.assertIn(0x4f, mt)
        self.assertEqual(mt.index(0x4e), 29)
        self.assertEqual(mt.index(0x4f), 30)

    def test_selector_has_tipo2_and_mode_bytes(self):
        d = A7S.read_bytes()
        sel = d[0x43826d58 - B : 0x43826db0 - B]
        self.assertIn(b'\x02\x2a', sel)          # cmp r2,#2 (tipo==2 -> silent)
        for v in (0x4e, 0x4f):
            self.assertIn(bytes([v, 0x20]), sel)  # movs r0,#0x4e / #0x4f

    def test_no_checkset_in_either_blob(self):
        d_a6000 = (ROOT / 'firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin').read_bytes()
        d_a7s = A7S.read_bytes()
        for name, dd in (('A6000', d_a6000), ('A7S', d_a7s)):
            self.assertNotIn(b'CheckSetSilentShutterMode', dd, name)
            self.assertNotIn(b'SetShutterTypeForLiro', dd, name)

    def test_imx210_register_count(self):
        self.assertEqual(self.t['imx210_registers'], 119)

    def test_sha256_present(self):
        self.assertEqual(len(self.t['imx210_sha256']), 64)
        self.assertEqual(len(self.t['imx235_sha256']), 64)

if __name__ == '__main__':
    unittest.main(verbosity=2)
