"""S53: hechos estáticos del parser CAIF ev1 en Darwin A7S 3.20 vs A6000 3.21 (solo lectura de ROM originales).

Direcciones ROM con base 0x4200 (offset de archivo = dirección - 0x4200). Ver docs/capture/s53-darwin-caif-reconstruction.md.
"""
import hashlib
import struct
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FW = ROOT / 'firmware/extracted'
BASE = 0x4200
ROMS = {
    'a6000': (FW / 'fw321/firmware.tar_unpacked/0640_darwin/darwin_core.bin',
              '5f2be06d9885d154e8e0df46a611d6830d29754b4353f6e82cecfe66dd6a0bf4'),
    'a7s': (FW / 'a7s-fw320/payload/firmware.tar_unpacked/0640_darwin/darwin_core.bin',
            '241f5d311991e8b4e0246b2edab4039517cab55daf431d4ad21670a8866174cf'),
}


def rom(name):
    path, sha = ROMS[name]
    data = path.read_bytes()
    if hashlib.sha256(data).hexdigest() != sha:
        raise AssertionError(f'ROM {name} alterada o distinta')
    return data


def span(d, addr, size):
    return d[addr - BASE:addr - BASE + size]


def u32(d, addr):
    return struct.unpack_from('<I', d, addr - BASE)[0]


A6000, A7S = rom('a6000'), rom('a7s')


class DispatchAndTransport(unittest.TestCase):
    def test_irq_dispatch_table(self):
        # Manejador común lee ICSR (0xe000ed04) e indexa la tabla ROM 0x4300 por número de excepción.
        for d, h in ((A6000, 0x6808), (A7S, 0x67fa)):
            lits = {u32(d, a) for a in range(h + 4 & ~3, h + 0x400, 4)}
            self.assertIn(0xe000ed04, lits)
            self.assertIn(0x4300, lits)
            self.assertEqual(u32(d, 0x4300), u32(d, BASE + 4))  # entrada 1 = Reset

    def test_mss_async_table_entry_0c_is_22_byte_rx(self):
        # Entrada {tx, rx, len, código}: ID 0x0c = recepción de 22 B, código 03 01 02 (≙ CAIF 0x10300).
        for d, entry, rx in ((A6000, 0x27c78, 0x2000344c), (A7S, 0x28bc8, 0x2000321c)):
            tx, rxp, ln, code = struct.unpack_from('<4I', d, entry - BASE)
            self.assertEqual((tx, rxp, ln), (0, rx, 0x16))
            self.assertEqual(code & 0xffffff, 0x020103)

    def test_mss_link_is_mfs5(self):
        # Descriptores serie A6000 (0x4c B): 1 = mss-sync, 3 = mss-async; ambos MFS5 (0x40038500, pines P36-P38).
        for k in (1, 3):
            a = 0x279e8 + k * 0x4c
            self.assertEqual(u32(A6000, a) & 7, 5)
            self.assertEqual(u32(A6000, a + 0x14), 0x40038500)
            self.assertEqual([u32(A6000, a + 0x2c + 4 * i) & 0xfff for i in range(3)], [0x1a0, 0x198, 0x19c])


class ParserSilentBit(unittest.TestCase):
    A7S_BIT5 = bytes.fromhex(  # ubfx r1,r0,#5,#1; bfi en S+0xd0 bit5; si activo S+0x31=(S+0x31&~3)+2
        'c0f3401194f8a00061f3451084f8a000c0b2a4f13004800606d594f8310020f00300801c84f83100')

    def test_a7s_parser_stores_pkt12_bit5(self):
        self.assertEqual(span(A7S, 0x18460, len(self.A7S_BIT5)), self.A7S_BIT5)

    def test_a6000_parser_lacks_bit5(self):
        # Tras guardar pkt[+0x13] en S+0xd3 la A6000 pasa directo a 0x5c88; sin ubfx #5 ni prueba lsl #0x1a.
        self.assertEqual(span(A6000, 0x18052, 8), bytes.fromhex('84f8a300edf717fe'))
        body = span(A6000, 0x17f8c, 0x18120 - 0x17f8c)
        self.assertNotIn(bytes.fromhex('c0f34011'), body)
        self.assertNotIn(bytes.fromhex('61f34510'), body)

    def test_a7s_not_silent_predicate(self):
        # 0x19a86: return !(S+0xd0 & 0x20), S = 0x200034a0.
        self.assertEqual(span(A7S, 0x19a86, 16), bytes.fromhex('5f49012091f8d010890600d500207047'))
        self.assertEqual(u32(A7S, (0x19a86 + 4 & ~3) + 0x17c), 0x200034a0)


class CoilGating(unittest.TestCase):
    def test_bitband_writer(self):
        # str r1,[r0, 0x42668000]: PDOR bit-band (FM3); +0x234 = P4D, +0x238 = P4E.
        for d, a in ((A6000, 0x51c0), (A7S, 0x5200)):
            self.assertEqual(span(d, a, 6), bytes.fromhex('f74a81507047'))
            self.assertEqual(u32(d, (a + 4 & ~3) + 0x3dc), 0x42668000)

    def test_a7s_coil_writers_take_not_silent_argument(self):
        # 0x2172c / 0x21786 guardan r0 (mov r4,r0) y saltan sin escribir si r4 == 0 (cmp r4,#0 = 002c).
        p4d = span(A7S, 0x2172c, 0x26)
        p4e = span(A7S, 0x21786, 0x2c)
        for b in (p4d, p4e):
            self.assertEqual(b[2:4], bytes.fromhex('0446'))
            self.assertIn(bytes.fromhex('002c'), b)
        self.assertIn(bytes.fromhex('00214ff40d70'), p4d)  # movs r1,#0; mov.w r0,#0x234
        self.assertIn(bytes.fromhex('01214ff40e70'), p4e)  # movs r1,#1; mov.w r0,#0x238

    def test_a6000_coil_writers_unconditional(self):
        p4d = span(A6000, 0x20cb2, 0x22)
        p4e = span(A6000, 0x20d00, 0x26)
        for b in (p4d, p4e):
            self.assertNotIn(bytes.fromhex('0446'), b)
            self.assertNotIn(bytes.fromhex('002c'), b)
        self.assertIn(bytes.fromhex('00214ff40d70'), p4d)
        self.assertIn(bytes.fromhex('01214ff40e70'), p4e)

    def test_deferred_handler_passes_predicate(self):
        # A7S 0x214dc: bl 0x216c2 (S+0x154 bit 4) -> bl 0x2172c; A6000 0x20a8a: bl 0x20cb2 sin argumento.
        self.assertEqual(span(A7S, 0x214dc, 0x0c), bytes.fromhex('10b5044600f0eff800f022f9'))
        self.assertEqual(span(A6000, 0x20a8a, 0x08), bytes.fromhex('10b5044600f010f9'))


if __name__ == '__main__':
    unittest.main()
