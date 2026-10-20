"""S59-Claude: constructor real de C_Imager (A7S 3.20), escenarios con objeto real, lista blanca de mensajes 0x1000/0x1001, único llamador del consumidor de ganancia."""
import sys, unittest, struct
from pathlib import Path
R = Path(__file__).resolve().parents[1]
for p in ('analysis/s59/claude', 'analysis/s58', 'analysis/s57', 'analysis/s55'): sys.path.insert(0, str(R / p))
import real_scen as rs
from a7s_emu import A7S, O, VT
from tdis import data, B
from capstone import Cs, CS_ARCH_ARM, CS_MODE_THUMB

def thumb(a, n): return list(Cs(CS_ARCH_ARM, CS_MODE_THUMB).disasm(data('A7S')[a - B:a - B + n], a))

class RealCtor(unittest.TestCase):
    def test_ctor_sets_vtable_without_stubs(self):
        e = A7S(ambito=rs.AMB); e.u.mem_write(O, bytes(0x500)); e.call(rs.CTOR, O, 0)
        self.assertEqual(e.r32(O), VT); self.assertEqual(e.stubbed, {})
        self.assertEqual((e.rd(O + 0x3d6, 1)[0], e.r32(O + 0x1d0)), (0xff, 0x1000))   # +0x3d6=0xff: antes 0 en el objeto sintético

    def test_wire_stream_same_as_synthetic(self):
        for mode in (0x0b, 0x4c, 0x4e, 0x4f):
            with self.subTest(mode=mode):
                a = rs.scenario(mode, 0, real=True); b = rs.scenario(mode, 0, real=False)
                self.assertEqual(len(a['dev']), 100); self.assertEqual(a['dev'], b['dev']); self.assertEqual(a['shadow'], b['shadow'])

    def test_p2s_base_is_real_not_artifact(self):
        a = rs.scenario(0x0b, 0, real=True); b = rs.scenario(0x0b, 0, real=False)
        self.assertEqual([len(bytes.fromhex(t)) for t in a['tx']], [127, 94, 26])
        self.assertEqual([len(bytes.fromhex(t)) for t in b['tx']], [126, 126, 126, 101, 26])   # fragmentación del objeto sintético

class MessageWhitelist(unittest.TestCase):
    def test_static_compares(self):
        ins = thumb(0x436f5b84, 0x16)
        cmps = [int(i.op_str.split('#')[1], 0) for i in ins if i.mnemonic == 'cmp']
        self.assertEqual(cmps, [0xb, 0x35, 0x37, 0x38])
        senders = {i.op_str for i in thumb(0x436f5b98, 0x20) if i.mnemonic == 'bl'}
        self.assertEqual(senders, {'#0x43ada07a', '#0x43ada0b4'})

    def test_dynamic_messages_only_whitelist(self):
        for mode, n in ((0x0b, 2), (0x35, 2), (0x4c, 0), (0x4d, 0), (0x4e, 0), (0x4f, 0)):
            with self.subTest(mode=mode):
                self.assertEqual(len(rs.scenario(mode, 0, real=True)['msgs']), n)

    def test_message_ids(self):
        ids = lambda a: [i.op_str for i in thumb(a, 0x40) if 'mov' in i.mnemonic and '#0x100' in i.op_str]
        self.assertIn('r1, #0x1000', ids(0x43ada07c)); self.assertIn('r1, #0x1001', ids(0x43ada0b4))

class ModeDifferences(unittest.TestCase):
    def test_non_message_differences_are_debug_override_readers(self):
        import blockdiff
        ok = lambda r: (0x436f4650 <= int(r[0], 16) and int(r[1], 16) <= 0x436f4716) or (0x436f5770 <= int(r[0], 16) and int(r[1], 16) <= 0x436f5980)
        msg = lambda r: int(r[0], 16) in (0x438f6864,) or 0x43ada07a <= int(r[0], 16) <= 0x43ada0e2 or 0x436f5b8c <= int(r[0], 16) <= 0x436f5bb2
        for a, b in ((0x0b, 0x4e), (0x4c, 0x4e)):
            d = blockdiff.diff(a, b)
            for r in d['only_a'] + d['only_b']: self.assertTrue(ok(r) or msg(r), r)
            self.assertNotEqual(d['n_a'], d['n_b'])
        self.assertTrue(any(msg(r) and int(r[0], 16) == 0x438f6864 for r in blockdiff.diff(0x0b, 0x4e)['only_a']))

    def test_debug_byte_ff_means_disabled(self):
        ins = thumb(0x436f5d98, 0x8); self.assertEqual([i.op_str for i in ins][:2], ['r0, [r3, #0xc]', 'r0, #0xff'])

class GainConsumer(unittest.TestCase):
    def test_single_caller_is_execute(self):
        d = data('A7S'); calls = []
        for off in range(0, len(d) - 4, 2):
            h1, h2 = struct.unpack_from('<HH', d, off)
            if (h1 & 0xf800) == 0xf000 and (h2 & 0xd000) == 0xd000:
                s = ((h1 >> 10) & 1); i1 = 1 - (((h2 >> 13) & 1) ^ s); i2 = 1 - (((h2 >> 11) & 1) ^ s)
                imm = (s << 24) | (i1 << 23) | (i2 << 22) | ((h1 & 0x3ff) << 12) | ((h2 & 0x7ff) << 1)
                if s: imm -= 1 << 25
                if B + off + 4 + imm == 0x436f459c and (h2 & 0x1000): calls.append(B + off)
        self.assertEqual(calls, [0x436f5b40])

if __name__ == '__main__': unittest.main()
