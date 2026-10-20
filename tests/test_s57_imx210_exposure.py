"""S57: semántica de ID1, pulso SSB, origen/mapeo de svd/shd/spl, diferencial IMX235 (Silent), sincronía P2S.

Solo lectura de binarios originales; emulación Unicorn en memoria (nunca toca cámara). Informes: docs/capture/s57-*.md.
Matriz: analysis/s57-evidence-matrix.json. Ejecutar: python3 -m unittest tests.test_s57_imx210_exposure  (usa analysis/s56 y analysis/s57)
"""
import hashlib
import json
import random
import re
import struct
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'analysis/s57'))
sys.path.insert(0, str(ROOT / 'analysis/s56'))
sys.path.insert(0, str(ROOT / 'analysis/s55'))
import gpio_calls_diff as G
from xr import index
from emu57 import scenario, trim
import id1_grid
import c_timing
import bitops
import imx235_matrix as M7

B = 0x43541000
SHA = {
    'A6000': 'b60c845ccb90c0ff86b7f62f1f3f2ecda714aa20c37805959ebee2b429e56bb9',
    'A7S': 'b857d33879d610abd185148d676de7ea0f753af3a08389994e788d617925103e',
}
IMG = {m: G.MODELS[m]['path'].read_bytes() for m in G.MODELS}
_, IDX = index('A6000')
SET_EXPOSURE, SET_READ, SSB, EXECUTE_FACADE, SET_MODE = 0x436d6320, 0x436d6398, 0x43ad9116, 0x43ad911c, 0x436d62e4


def calls_in(model, lo, hi):
    """Llamadas bl/b.w con destino directo dentro de [lo,hi), en orden de dirección."""
    ins = [i for i in G.disasm(IMG[model]) if lo <= i.address < hi and i.mnemonic in ('bl', 'b.w') and i.op_str.startswith('#')]
    return [(i.address, int(i.op_str[1:], 0)) for i in ins]


class Integrity(unittest.TestCase):
    def test_sha(self):
        for m, d in IMG.items():
            self.assertEqual(hashlib.sha256(d).hexdigest(), SHA[m], m)


class Id1Writers(unittest.TestCase):
    """S57-A.1/A.2: todas las escrituras de bits de ID1 (dos registros sombra) por función y dirección."""
    @classmethod
    def setUpClass(cls):
        cls.ops = bitops.scan()

    def test_id1_writers_confined(self):
        fns = {o['fn'] for o in self.ops[1]}
        self.assertEqual(fns, {'0x436d6f70', '0x436d7bc8'})           # SetExposure y región trigger/ajuste (hojas sin push lr)

    def test_setexposure_bit_set(self):
        # SetExposure sólo toca los bits 2,4,6,7 de ID1 (nunca 0,1,3,5)
        bits = set()
        for o in self.ops[1]:
            if o['fn'] != '0x436d6f70': continue
            if o['op'] == 'orr': v = int(o['arg'], 0); bits |= {b for b in range(8) if v >> b & 1}
            if o['op'] == 'bfc':
                m = re.match(r'bit(\d+) w(\d+)', o['arg']); bits |= set(range(int(m.group(1)), int(m.group(1)) + int(m.group(2))))
        self.assertEqual(bits, {2, 4, 6, 7})

    def test_only_ssb_writes_bit3(self):
        b3 = [o for o in self.ops[1] if (o['op'] == 'orr' and int(o['arg'], 0) & 8) or (o['op'] == 'bfc' and o['arg'].startswith('bit3'))]
        self.assertTrue(b3)
        for o in b3:
            self.assertTrue(0x436d7c08 <= int(o['addr'], 16) < 0x436d7c4a, o)

    def test_table_order(self):
        self.assertEqual([hex(u) for u in (struct.unpack_from('<I', IMG['A6000'], 0x43fe995c + 4 * i - B)[0] for i in (1, 2))], ['0x4401ca2c', '0x4401c734'])


class Id1Emulation(unittest.TestCase):
    """S57-A.3: rejilla modo x ShutMode x SSB con código real (SetMode/SetExposure/Execute)."""
    MASK = {0: (0, 0, 0, 1), 1: (1, 1, 0, 1), 2: (1, 1, 1, 0), 3: (1, 1, 1, 1), 4: (0, 1, 0, 1)}      # (bit2, bit7, bit4, bit6)

    def test_matrix_base(self):
        base = {m: id1_grid.run(m, 0)['base'][0] for m in (0xb, 0x2f, 1, 5, 0x1a)}
        self.assertEqual(base, {0xb: 0x44, 0x2f: 0x44, 1: 0x40, 5: 0x41, 0x1a: 0x41})

    def test_shutmode_bits(self):
        for mode in (0xb, 5):
            for s, (b2, b7, b4, b6) in self.MASK.items():
                r = id1_grid.run(mode, s)
                v = r['after_setexp'][0]
                self.assertEqual((v >> 2 & 1, v >> 7 & 1, v >> 4 & 1, v >> 6 & 1), (b2, b7, b4, b6), (mode, s))
                self.assertEqual(v & 0x2b, r['base'][0] & 0x2b)                                # bits 0,1,3,5 conservan lo de SetMode

    def test_ssb_pulse_wire(self):
        for s in range(5):
            quiet = id1_grid.run(0xb, s, 0)['wire_id1']; pulse = id1_grid.run(0xb, s, 1)
            self.assertEqual(quiet[0], quiet[1])
            self.assertEqual(pulse['wire_id1'], [quiet[0] | 8, quiet[0] & ~8 & 0xff])
            self.assertTrue(pulse['ssb_cleared'])

    def test_pulse_blocks_adjacent(self):
        r = scenario(0xb, 1, True); t = trim(r['e'].split()[0][0])
        self.assertEqual(t[:7].hex(), '810581' + '0000' + '0c' + 'cc')      # bloque 1: dir 0 -> 0x0c, dir 1 -> 0xCC (ID1 con bit3)
        self.assertEqual(t[7:12].hex(), '812f810001')                       # bloque 2: cabecera y dir 1 -> 0xC4 (ID1 sin bit3)
        self.assertEqual(t[12], 0xc4)

    def test_dirty_memory_independence(self):
        for m, s, ssb in ((0xb, 1, 1), (0x2f, 2, 0), (5, 4, 1)):
            self.assertEqual(id1_grid.run(m, s, ssb, fill=0), id1_grid.run(m, s, ssb, fill=0xa5))

    def test_adjustcmd_flag_279(self):
        # +0x279 (categoría 8 de AdjustCmd 0x91) con drive 0x0b: Execute borra bits 2,7,4 de ID1 (0x436d7cf0), también en ShutMode 2 -> 0x00
        wires = [id1_grid.run(0xb, s, 0, f279=1)['wire_id1'] for s in range(5)]
        self.assertEqual(wires, [[0x40, 0x40], [0x40, 0x40], [0x00, 0x00], [0x40, 0x40], [0x40, 0x40]])
        self.assertEqual(id1_grid.run(0x2f, 1, 0, f279=1)['wire_id1'], [0xc4, 0xc4])        # sólo con drive == 0x0b


class SsbProducers(unittest.TestCase):
    """S57-B.1/B.2: orden SetExposure -> SSB -> Execute en los productores."""
    def seq(self, lo, hi):
        names = {SET_EXPOSURE: 'SetExposure', SET_READ: 'SetRead', SSB: 'SSB', EXECUTE_FACADE: 'Execute', SET_MODE: 'SetMode'}
        return [names[t] for a, t in calls_in('A6000', lo, hi) if t in names]

    def test_start_exposure(self):
        self.assertEqual(self.seq(0x438c828c, 0x438c8344), ['SetExposure', 'SetRead', 'SSB', 'Execute', 'Execute'])   # Execute(1) / Execute(0) ramas

    def test_exposure_timer_start(self):
        self.assertEqual(self.seq(0x438c86b0, 0x438c8890), ['SetExposure', 'SetRead', 'SSB', 'Execute'])

    def test_capture_start(self):
        s = self.seq(0x438c7800, 0x438c7a60)
        self.assertEqual(s, ['SetMode', 'Execute', 'SetExposure', 'SSB', 'SetRead', 'Execute'])

    def test_helper_ssb_then_setexposure(self):
        self.assertEqual(self.seq(0x43ae935a, 0x43ae9380), ['SSB', 'SetExposure'])

    def test_five_callers(self):
        self.assertEqual(sorted(a for a, _ in IDX['calls'][SSB]), [0x438c7a0a, 0x438c8326, 0x438c883c, 0x438cc5ce, 0x43ae936c])

    def test_shutmode_byte_writers(self):
        # cap+0x655 (ShutMode): 0 en inicio de captura y StartExposure, 1 en ExposureTimerStart
        ins = G.disasm(IMG['A6000'])
        st = {hex(i.address) for i in ins if i.mnemonic.startswith('strb') and re.search(r'\[r4, #0x655\]', i.op_str)}
        self.assertEqual(st, {'0x438c79e2', '0x438c82bc', '0x438c87f0'})


class TimingMapping(unittest.TestCase):
    """S57-C: mapeo exacto (svd,shd,spl) -> registros 3..8 y 0x100/0x101 con SetExposure real."""
    def test_slicing_random(self):
        rnd = random.Random(57)
        for _ in range(40):
            shd, svd, spl, shut = rnd.randrange(0x10000), rnd.randrange(0x10000), rnd.randrange(0x10000), rnd.randrange(5)
            for fill in (0, 0xa5):
                b, a, e = c_timing.run(shd, svd, spl, shut, fill, mirror_flag=0xff)
                m = c_timing.model(shd, svd, spl)
                for i, msk in ((3, 255), (4, 15), (5, 255), (6, 63), (7, 255), (8, 15)):
                    self.assertEqual(a[i] & msk, m[i] & msk)
                    self.assertEqual(a[i] & ~msk & 255, b[i] & ~msk & 255)

    def test_arg_layout_from_log_call(self):
        # el log SetExps (0x436d723a) imprime svd=r6, shd=r5, spl=r7, shut=sb; r6/r5/r7/sb se cargan de arg+4, +0, +6, +9
        d = IMG['A6000']
        code = d[0x436d6faa - B:0x436d6fb8 - B]
        self.assertEqual(code[:2].hex(), '8e88')       # ldrh r6,[r1,#4]
        self.assertEqual(code[4:6].hex(), '0d88')      # ldrh r5,[r1]
        self.assertEqual(code[6:8].hex(), 'cf88')      # ldrh r7,[r1,#6]

    def test_mirror_registers_conditional(self):
        _, a, _ = c_timing.run(0x1234, 0xabc, 0x567, 1, 0, mirror_flag=0x00)
        self.assertEqual([a[i] for i in range(0x144, 0x14a)], [0xbc, 0x0a, 0x34, 0x12, 0x67, 0x05])
        _, a, _ = c_timing.run(0x1234, 0xabc, 0x567, 1, 0, mirror_flag=0xff)
        self.assertNotEqual([a[i] for i in range(0x144, 0x14a)], [0xbc, 0x0a, 0x34, 0x12, 0x67, 0x05])

    def test_shutmode2_loads_100_101(self):
        for s, exp in ((1, (0x00, 0x38)), (2, (7, 9))):
            for fill in (0, 0xa5):
                _, a, _ = c_timing.run(0x1234, 0xabc, 0x567, s, fill, w10=0x5aa5, w12=0x33cc, b8=7, b14=9)
                self.assertEqual((a[0x100], a[0x101]), exp)

    def test_producer_strings(self):
        d = IMG['A6000']
        for s in (b'[CAMERA_MAIN_SYNC]: Imager svd error. shut:%d, svd:%d -> %d', b'[CAMERA_MAIN_SYNC]: Imager param error shut:%d, svr_num:%d, VdNum:%d',
                  b'[CAMERA_MAIN_SYNC]: shut:%d, svd:%d, shd:%d, spl:%d, sint:%d, gs:%d', b'[CAM_IMAGER]: Execute : [PrevDrv:%2d] [NowDrv:%2d] [NextDrv:%2d] [SSBRK_ON:%01x] [SLEEP_ON:%01x]'):
            self.assertIn(s, d)

    def test_svd_formula_code(self):
        # 0x4381106c: r0 = (VdNum<=1) ? svr_num*n : n/VdNum ; r0 -= 1 ; error si bit15 (tst #0x8000)
        d = IMG['A6000']
        ins = {i.address: i for i in G.disasm(d)}
        self.assertEqual((ins[0x438110da].mnemonic, ins[0x438110da].op_str), ('cmp.w', 'sb, #1'))
        self.assertEqual(ins[0x438110e4].mnemonic, 'muls')
        self.assertEqual((ins[0x438110ec].mnemonic, ins[0x438110ec].op_str), ('bl', '#0x4355faf0'))          # división
        self.assertEqual((ins[0x438110f0].mnemonic, ins[0x438110f0].op_str), ('subs', 'r0, #1'))
        self.assertEqual((ins[0x438110f4].mnemonic, ins[0x438110f4].op_str), ('tst.w', 'r0, #0x8000'))
        self.assertEqual(ins[0x43811214].op_str, '#0x43ae935a')                                              # -> helper SSB+SetExposure

    def test_main_sync_shutmode(self):
        # 0x4381118e..: arg+9 (ShutMode) = (cap[0x1fc] == 9) ? 1 : 0
        ins = {i.address: i for i in G.disasm(IMG['A6000'])}
        self.assertEqual((ins[0x43811192].mnemonic, ins[0x43811192].op_str), ('cmp', 'r3, #9'))
        self.assertEqual((ins[0x43811196].mnemonic, ins[0x43811196].op_str), ('subs', 'r3, #8'))
        self.assertEqual((ins[0x4381119c].mnemonic, ins[0x4381119c].op_str), ('strb.w', 'r3, [sp, #0x21]'))


class AdjustCmdFlags(unittest.TestCase):
    """S57-A: los indicadores +0x277/+0x278/+0x279/+0x27c los fija el manejador AdjustCmd 0x91 (0x43a12d9c) por categoría de tabla."""
    def test_facade_setters(self):
        want = {0x43ad9194: 0x43a12f72, 0x43ad91a0: 0x43a12f86, 0x43ad91b8: 0x43a12f9c, 0x43ad91ac: 0x43a12fb0}
        for t, c in want.items():
            self.assertIn(c, [a for a, _ in IDX['calls'][t]], hex(t))

    def test_predicates(self):
        # categoría == 4 -> +0x278, == 7 -> +0x27c, == 8 -> +0x279 (sub #4/#7/#8 + rsbs/adc)
        ins = {i.address: i for i in G.disasm(IMG['A6000'])}
        for a, k in ((0x43b7a87a, 4), (0x43b7a89a, 7), (0x43b7a8ba, 8)):
            self.assertEqual(ins[a].op_str.endswith('#%d' % k), True, hex(a))



class P2SSync(unittest.TestCase):
    """S57-F: SyncMode se escribe tal cual en 0xfc088800; sólo el modo 2 usa banderas OSAL y el disparo 1,0,1."""
    def test_modes(self):
        sys.path.insert(0, str(ROOT / 'analysis/s57'))
        import sync_modes
        out = sync_modes.out
        for mode in (0, 1, 3):
            ctl, flags = out[mode]
            self.assertEqual(flags, [])
            self.assertIn(('0xfc088800', 4, hex(mode)), ctl)
        ctl, flags = out[2]
        self.assertEqual([f[0] for f in flags], ['clrflg', 'setflg', 'waitflg', 'clrflg', 'setflg'])
        self.assertEqual([c for c in ctl if c[0] == '0xfc088808'][-3:], [('0xfc088808', 4, '0x1'), ('0xfc088808', 4, '0x0'), ('0xfc088808', 4, '0x1')])

    def test_execute_order(self):
        # Execute: lista 119 (modo 2) -> espera de bandera P2S (0x436d5bcc) -> lista de 8 inmediatos (modo 0)
        c = [t for a, t in calls_in('A6000', 0x436d8568, 0x436d85a0)]
        self.assertEqual(c, [0x436d79b0, 0x436d75f8, 0x436d5bcc, 0x436d75f8])


class Imx235Silent(unittest.TestCase):
    """S57-D: matriz efectiva IMX235 (36 filas x 34 modos) y relación de los modos Silent 0x4e/0x4f."""
    def col(self, m):
        i = M7.modes.index(m); return [r['vals'][i] for r in M7.rows]

    def test_shape(self):
        self.assertEqual((len(M7.rows), len(M7.modes)), (35, 34))

    def test_silent_vs_normal_rows_differ(self):
        # 0x4e: 33/35 registros difieren de la foto 0x0b (iguales: dir 0x0008 y 0x000a = 0); 0x4f: 35/35
        self.assertEqual(sum(a != b for a, b in zip(self.col(0xb), self.col(0x4e))), 33)
        self.assertEqual(sum(a != b for a, b in zip(self.col(0xb), self.col(0x4f))), 35)

    def test_silent_is_sibling_of_4c_4d(self):
        d = lambda a, b: [(hex(bytes.fromhex(r['raw'])[2] | bytes.fromhex(r['raw'])[3] << 8), x, y) for r, x, y in zip(M7.rows, self.col(a), self.col(b)) if x != y]
        self.assertEqual(d(0x4e, 0x4c), [('0xc', 0x10, 0x20)])
        self.assertEqual(d(0x4f, 0x4d), [('0xa', 1, 2)])
        self.assertEqual(len(d(0x4e, 0x4f)), 4)

    def test_selector_a7s(self):
        # 0x43826d58: tipo==2 & sub 0 -> 0x4e ; sub 1 -> 0x4f
        d = IMG['A7S']
        self.assertEqual(d[0x43826d7c - B:0x43826d7e - B].hex(), '4e20')
        self.assertEqual(d[0x43826da6 - B:0x43826da8 - B].hex(), '4f20')

    def test_a7s_pulse_in_setexposure(self):
        # A7S: [O+0x3d7]=1 si el parámetro u16 (arg+2) > 0x1000 dentro de SetExposure (0x436f4a94); 0 en caso contrario
        ins = {i.address: i for i in G.disasm(IMG['A7S'])}
        self.assertEqual((ins[0x436f4b10].mnemonic, ins[0x436f4b10].op_str), ('cmp.w', 'r8, #0x1000'))
        self.assertEqual((ins[0x436f4b20].mnemonic, ins[0x436f4b20].op_str), ('strb.w', 'r1, [r4, #0x3d7]'))
        self.assertEqual((ins[0x436f4b48].mnemonic, ins[0x436f4b48].op_str), ('strb.w', 'r3, [r4, #0x3d7]'))
        self.assertEqual((ins[0x436f4aca].mnemonic, ins[0x436f4aca].op_str), ('ldrh', 'r0, [r0, #2]'))


class MatrixConsistency(unittest.TestCase):
    def test_matrix_refs_exist(self):
        m = json.loads((ROOT / 'analysis/s57-evidence-matrix.json').read_text())
        self.assertEqual(m['phase'], 'S57')
        src = Path(__file__).read_text()
        for e in m['entries']:
            cls = e['test'].split('::')[-1]
            self.assertIn(f'class {cls}', src, e['id'])
            self.assertIn(e['status'], {'VERIFICADO', 'INFERENCIA', 'NO VERIFICADO', 'DESCARTADO', 'PARCIAL', 'HIPÓTESIS'})
            for k in ('model', 'firmware', 'sha256', 'address', 'registers', 'bits', 'interpretation', 'validation_method', 'limitations'):
                self.assertIn(k, e, e['id'])


if __name__ == '__main__':
    unittest.main()
