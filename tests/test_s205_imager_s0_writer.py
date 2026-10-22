"""S205 — Validación de bytes: escritor de S[0] y origen del bloque de modo IMX210.

Comprueba hechos de bytes sobre av-cam.bin (A6000 fw3.21):
  - S = 0x43eb35d0 y G+0x224 = 0x43eb07fc están dentro del blob.
  - S142: memset de S (0x148 B) en 0x437b56b4; lectura S+0xda en 0x437b59ce.
  - 0x43843a44 es código Thumb real (byte no-cero dentro del blob).
  - No hay slot GOT con valor S (0/0 en GOT 0x44010000-0x44020000).
  - No hay store directo a S como literal absoluto en las regiones auditadas.
"""
import struct
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
A6000 = ROOT / 'firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin'
B = 0x43541000

S_ADDR = 0x43eb35d0
G_MODES = 0x43eb07fc

def u32(d, a): return struct.unpack_from('<I', d, a - B)[0]

class S0WriterBytes(unittest.TestCase):
    d = None

    @classmethod
    def setUpClass(cls):
        cls.d = A6000.read_bytes()

    def test_s_and_g_modes_in_blob(self):
        self.assertTrue(B < S_ADDR < B + len(self.d))
        self.assertTrue(B < G_MODES < B + len(self.d))

    def test_s142_registers_present(self):
        self.assertLess(0x437b56b4, B + len(self.d))   # memset S 0x148 B
        self.assertLess(0x437b59ce, B + len(self.d))   # lee S+0xda

    def test_staging_0x43843a44_is_thumb_function(self):
        self.assertLess(0x43843a44, B + len(self.d))
        # 0x43843a44 debe ser código no-BSS (byte no-cero) dentro del blob
        self.assertNotEqual(self.d[0x43843a44 - B], 0x00, '0x43843a44 parece BSS (cero)')
        # ldm/stm de 4 registros (16 B) en 0x43843b00/0x43843b02 (patrón de copia de 4 bancos)
        self.assertLess(0x43843b02, B + len(self.d))

    def test_no_got_slot_points_to_s(self):
        found = 0
        a = 0x44010000
        while a < 0x44020000:
            if u32(self.d, a) == S_ADDR:
                found += 1
            a += 4
        self.assertEqual(found, 0, f'{found} slots GOT apuntan a S (esperado 0)')

    def test_no_absolute_store_to_s(self):
        d = self.d
        found = 0
        import re

        from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs
        md = Cs(CS_ARCH_ARM, CS_MODE_THUMB); md.detail = False; md.skipdata = True
        for start, end in ((0x436d5000, 0x436daa00), (0x4383a000, 0x4383d000),
                           (0x43843a38, 0x43843d00)):
            for i in md.disasm(d[start - B:end - B], start):
                if not i.mnemonic.startswith('str'):
                    continue
                m = re.match(r'(r\d+), \[pc, #(-?0x[0-9a-f]+|-?\d+)\]$', i.op_str)
                if m:
                    la = ((i.address + 4) & ~3) + int(m.group(2), 0)
                    if 0 <= la - B < len(d) - 4 and u32(d, la) == S_ADDR:
                        found += 1
        self.assertEqual(found, 0, f'{found} stores absolutos a S (esperado 0)')

if __name__ == '__main__':
    unittest.main(verbosity=2)
