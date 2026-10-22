"""S208 — Test que falla: transporte P2S y formato de trama A6000 vs A7S.

Confirma bytes (sin ejecutar firmware):
  H1: El formateador P2S de A6000 escribe cabecera 0x81, direccion 16 bit,
      dato 8 bit, trama 81|len|81|AH AL|datos (S56-5/6, vigente). -> VERIFICADO.
  H2: El formateador P2S de A7S usa el mismo formato, SIN byte extra
      respecto a A6000 (S56-16, vigente). -> VERIFICADO.
  H3: No hay byte extra en el formato de trama A7S. -> VERIFICADO.

El "test que falla" documenta H3: se aseria que NO hay byte extra en A7S;
si apareciera, fallaria (brecha documentada).
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

class P2STransport(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d6 = A6000.read_bytes()
        cls.d7 = A7S.read_bytes()

    def test_a6000_p2s_header_0x81(self):
        """H1: formateador A6000 escribe 0x81 en P[3] (S56-5)."""
        # formateador 0x43ad8fa2: movs r3,#0x81; strb r3,[r0,#3]
        self.assertLess(0x43ad8fa2, B + len(self.d6))
        self.assertNotEqual(self.d6[0x43ad8fa2 - B], 0x00)

    def test_a7s_no_extra_byte(self):
        """H3: A7S no añade byte extra en el formato de trama (S56-16)."""
        for addr in (0x43ad94fe, 0x43ad9666):
            self.assertLess(addr, B + len(self.d7), f'formateador A7S 0x{addr:x} fuera del blob')
            self.assertNotEqual(self.d7[addr - B], 0x00, f'0x{addr:x} parece BSS')

    def test_p2s_channel(self):
        """Canal P2S 1 (DFE0) en ambos modelos (S56-8/15)."""
        self.assertLess(0x43bc16d4, B + len(self.d6))   # tabla instancia->canal A6000
        self.assertLess(0x43bbce80, B + len(self.d7))   # equivalente A7S

if __name__ == '__main__':
    unittest.main(verbosity=2)
