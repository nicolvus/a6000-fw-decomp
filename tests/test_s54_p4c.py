"""S54: P4C (CA_1ST_CURTAIN_START), mecanismo tipo 0 y primitivas GPIO de BIONZ (solo lectura de binarios originales).

Direcciones Darwin con base ROM 0x4200. Informes: docs/capture/s54-*.md. Matriz: analysis/s54-evidence-matrix.json.
Ejecutar: python3 -m unittest tests.test_s54_p4c
"""
import difflib
import hashlib
import re
import struct
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'analysis/s54'))
import p4c_scan as P  # noqa: E402

FW = ROOT / 'firmware/extracted'
AVCAM = FW / 'fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin'
SHA = {
    'a6000': '5f2be06d9885d154e8e0df46a611d6830d29754b4353f6e82cecfe66dd6a0bf4',
    'a7s': '241f5d311991e8b4e0246b2edab4039517cab55daf431d4ad21670a8866174cf',
}
SHA_AVCAM = 'b60c845ccb90c0ff86b7f62f1f3f2ecda714aa20c37805959ebee2b429e56bb9'
BASE, AV_BASE = 0x4200, 0x43541000

ROMS = {}
for n in ('a6000', 'a7s'):
    d, ins = P.load(n)
    assert hashlib.sha256(d).hexdigest() == SHA[n], f'ROM {n} alterada'
    ROMS[n] = (d, {i.address: i for i in ins}, ins)

# Escritores de bit-band y direcciones de las funciones de exposición por modelo
WR = {'a6000': 0x51c0, 'a7s': 0x5200}
TYPE_FN = {'a6000': 0x20c74, 'a7s': 0x216e8}
EXPO = {'a6000': (0x20d26, 0x20e0e, 0x20e98, 0x20f5e), 'a7s': (0x217b2, 0x218a0, 0x2192e, 0x219f8)}
# Escrituras P4C←0 (offset 0x230) reconstruidas por lectura de instrucciones (ver s54-p4c-signal-trace.md §3)
P4C_SITES = {
    'a6000': [0x20d8a, 0x20dba, 0x20df6, 0x20e30, 0x20e64, 0x20e96, 0x20ece, 0x20f14, 0x20f34],
    'a7s': [0x2181c, 0x2184c, 0x21888, 0x218c6, 0x218fa, 0x2192c, 0x21968, 0x219ae, 0x219ce],
}


def u32(d, a):
    return struct.unpack_from('<I', d, a - BASE)[0]


def seq(ins, a, b):
    return [i for i in ins if a <= i.address < b]


class WritersAndP4C(unittest.TestCase):
    def test_writer_bytes_and_literals(self):
        for n, w in WR.items():
            d = ROMS[n][0]
            self.assertEqual(d[w - BASE:w - BASE + 6], bytes.fromhex('f74a81507047')[:6])
            self.assertEqual(P.writers(d)[0], w)
            lit = ((w + 4) & ~3) + 0x3dc
            self.assertEqual(u32(d, lit), 0x42668000)      # PDOR bit-band
            self.assertEqual(u32(d, lit + 4), 0x42666000)  # PDIR bit-band (lector w+6)

    def test_p4c_written_only_with_zero(self):
        # En cada sitio P4C: `movs r1,#0` + `mov r0,rX` (rX=0x230) justo antes de un bl al escritor
        # (los sitios 0x20e96/0x2192c son saltos a la llamada ya preparada de 0x20e6e/0x21904).
        for n, sites in P4C_SITES.items():
            _, by, _ = ROMS[n]
            w = WR[n]
            for s in sites:
                i = by[s]
                if s in (0x20e96, 0x2192c):
                    self.assertEqual(i.mnemonic, 'b')
                    self.assertEqual((by[s - 4].mnemonic, by[s - 4].op_str), ('movs', 'r1, #0'))
                    self.assertEqual(by[s - 2].mnemonic, 'mov')
                    continue
                self.assertEqual((i.mnemonic, int(i.op_str.lstrip('#'), 16)), ('bl', w), hex(s))
                self.assertEqual((by[s - 4].mnemonic, by[s - 4].op_str), ('movs', 'r1, #0'), hex(s))
                self.assertEqual(by[s - 2].mnemonic, 'mov')

    def test_p4c_register_constant(self):
        for n, fns in {'a6000': (0x20d26, 0x20e0e, 0x20e98), 'a7s': (0x217b2, 0x218a0, 0x2192e)}.items():
            _, _, ins = ROMS[n]
            for f in fns:
                nxt = min(a for a in (i.address for i in ins if i.mnemonic in ('push', 'push.w') and 'lr' in i.op_str) if a > f)
                body = seq(ins, f, nxt)
                self.assertRegex(' ; '.join(i.op_str for i in body if i.mnemonic == 'mov.w'), r'r\d, #0x230')

    def test_no_p4c_set_high_in_runtime_writers(self):
        # Ninguna llamada de escritor con r0=0x230 y r1!=0 (propagación aproximada: ver limitaciones del informe)
        for n in ('a6000', 'a7s'):
            for e in P.track(n):
                if e['kind'] == 'W' and e['r0'] == 0x230:
                    self.assertEqual(e['r1'], 0, (n, hex(e['addr'])))

    def test_pdor4_direct_writers_are_init_and_masked(self):
        # 0x584c (init DDR4=0x7e3f, PDOR4=0) y 0x51f2 (máscara 0x9fff conserva b12=P4C; único llamador 0x20e3e)
        d, by, ins = ROMS['a6000']
        self.assertEqual(by[0x58f6].op_str, 'r1, [r4, #0x210]')
        self.assertEqual(by[0x58fa].op_str, 'r5, [r4, #0x410]')
        self.assertEqual(by[0x58f2].op_str, 'r1, #0x7e3f')
        callers = [i.address for i in ins if i.mnemonic in ('bl', 'b.w') and int(i.op_str.lstrip('#'), 16) == 0x51f2]
        self.assertEqual(callers, [0x20e3e])
        self.assertEqual(0x9fff & 0x1000, 0x1000)

    def test_p4c_reader_in_status_word(self):
        # 0x1ecfe lee PDIR b12 y 0x16390 lo coloca en el bit 0x80 de una palabra de estado
        d, by, ins = ROMS['a6000']
        self.assertEqual((by[0x1ed02].mnemonic, by[0x1ed02].op_str), ('mov.w', 'r0, #0x230'))
        self.assertEqual(int(by[0x1ed06].op_str.lstrip('#'), 16), 0x51c6)
        self.assertEqual(int(by[0x164e2].op_str.lstrip('#'), 16), 0x1ecfe)
        self.assertEqual(by[0x164e8].op_str, 'r4, r4, #0x80')

    def test_profile_p4c_initial_level(self):
        # perfiles de pines (0x25bfc + n*0x98), entradas {byte0=puerto|modo<<3, byte1 nivel<<2, máscara u16}
        d = ROMS['a6000'][0]
        lvl = {}
        for k in range(6):
            a = 0x25bfc + k * 0x98
            level = None
            for e in range(0, 0x98, 4):
                b = d[a - BASE + e:a - BASE + e + 4]
                if (b[0] & 7) == 4 and (b[0] >> 3) == 1 and (b[2] | b[3] << 8) & 0x1000:
                    level = (b[1] >> 2) & 3
            lvl[k] = level
        self.assertEqual(lvl, {0: 0, 1: 0, 2: 0, 3: 1, 4: 0, 5: 0})


class MechanismTypeZero(unittest.TestCase):
    def test_type_selector(self):
        # 0x20c74 = 0x1b080(0)&7 ∈ {1,2,3} else 0; A7S 0x216e8 idéntica
        for n in ('a6000', 'a7s'):
            d, by, ins = ROMS[n]
            f = TYPE_FN[n]
            body = seq(ins, f, f + 0x1c)
            self.assertEqual([i.mnemonic + ' ' + i.op_str for i in body][2:4], ['bl #' + hex(0x1b080 if n == 'a6000' else 0x1b5e8), 'and r0, r0, #7'])

    def test_config_byte_getter(self):
        # 0x1b080(ch): ch + [0x200002c0] válido? ch->[0x20000000+0x50+ch] : 0
        d, by, ins = ROMS['a6000']
        self.assertEqual(u32(d, 0x1b0e0), 0x200002c0)
        self.assertEqual(u32(d, 0x1b0e4), 0x20000000)
        self.assertEqual(by[0x1b090].op_str, 'r0, [r0, #0x50]')

    def test_expo_functions_identical_but_silent_gate(self):
        callmap, ndiff = {}, 0
        for fa, fs in zip(EXPO['a6000'][:3], EXPO['a7s'][:3]):
            def end(ins, f):
                return min(a for a in (i.address for i in ins if i.mnemonic in ('push', 'push.w') and 'lr' in i.op_str) if a > f)
            A = seq(ROMS['a6000'][2], fa, end(ROMS['a6000'][2], fa))
            S = seq(ROMS['a7s'][2], fs, end(ROMS['a7s'][2], fs))
            key = lambda x: (x.mnemonic, re.sub(r'#0x[0-9a-f]{3,}', '#K', x.op_str) if x.mnemonic != 'bl' else '')
            sm = difflib.SequenceMatcher(None, [key(x) for x in A], [key(x) for x in S], autojunk=False)
            for tag, i1, i2, j1, j2 in sm.get_opcodes():
                if tag == 'equal':
                    for x, y in zip(A[i1:i2], S[j1:j2]):
                        if x.mnemonic == 'bl':
                            callmap.setdefault(int(x.op_str[1:], 16), set()).add(int(y.op_str[1:], 16))
                else:
                    ndiff += 1
                    self.assertEqual(i1, i2 if tag == 'insert' else i1)  # sólo hay inserciones o la cabecera 0x20e0e
        self.assertEqual({k: v for k, v in callmap.items()}, {
            0x51c0: {0x5200}, 0x51f2: {0x5232}, 0x5c88: {0x5cca}, 0x5c9e: {0x5ce0}, 0x93e6: {0x8ad2},
            0x202c2: {0x20c98}, 0x20408: {0x20dfa}, 0x20c74: {0x216e8}, 0x210c0: {0x21b5a}})
        self.assertLessEqual(ndiff, 8)

    def test_silent_branch_is_type_zero_branch(self):
        # A7S 0x217b2: type==0 o no_silent==0 -> 0x2186c; A6000 0x20d26: type==0 -> 0x20dda (mismo cuerpo)
        a = [(i.mnemonic, i.op_str) for i in seq(ROMS['a6000'][2], 0x20dda, 0x20e0e)]
        s = [(i.mnemonic, i.op_str) for i in seq(ROMS['a7s'][2], 0x2186c, 0x218a0)]
        norm = lambda L: [(m, re.sub(r'#0x[0-9a-f]{3,}', '#K', o)) for m, o in L]
        self.assertEqual(norm(a)[:5], norm(s)[:5])
        by = ROMS['a7s'][1]
        self.assertEqual(by[0x217cc].op_str, '#0x216e8')
        self.assertEqual((by[0x217d6].mnemonic, by[0x217d6].op_str), ('beq', '#0x2186c'))
        self.assertEqual((by[0x217da].mnemonic, by[0x217da].op_str), ('beq', '#0x2186c'))
        self.assertEqual(ROMS['a6000'][1][0x20d48].op_str, '#0x20dda')

    def test_adc_tracking_gated_by_type_in_a6000(self):
        # 0x20734 y 0x2083c consultan 0x20c74 antes de armar S+0x153; A7S añade además 0x216c2 (no_silent)
        by = ROMS['a6000'][1]
        self.assertEqual(by[0x2077c].op_str, '#0x20c74')
        self.assertEqual(by[0x20780].mnemonic, 'cbz')
        self.assertEqual(by[0x20840].op_str, '#0x20c74')
        self.assertEqual(by[0x2078a].op_str, 'r0, [r4, #0x153]')
        a7 = ROMS['a7s'][1]
        self.assertEqual(a7[0x211c2].op_str, '#0x216c2')
        self.assertEqual(a7[0x21286].op_str, '#0x216e8')

    def test_coil_writers_gate(self):
        # A6000: sólo tipo; A7S: tipo y argumento no_silent (cmp r4,#0)
        for n, fns in {'a6000': (0x20c90, 0x20cb2, 0x20cd4, 0x20d00), 'a7s': (0x21704, 0x2172c, 0x21754, 0x21786)}.items():
            _, _, ins = ROMS[n]
            for f in fns:
                body = seq(ins, f, f + 0x24)
                txt = ' ; '.join(f'{i.mnemonic} {i.op_str}' for i in body)
                self.assertEqual('cmp r4, #0' in txt, n == 'a7s')

    def test_a7s_reset_paths_force_coils_but_type_zero_never_acts(self):
        # A7S 0x20da2 (≙A6000 0x203b2) y 0x21122 (≙0x206ec) llaman a los escritores de bobina con no_silent=1 (actúan aun en Silent);
        # en A6000 todas las rutas pasan por el filtro de tipo (0x20c74), así que tipo 0 las suprime todas.
        a7 = ROMS['a7s'][1]
        for call, tgt in ((0x20db4, 0x21786), (0x2112a, 0x2172c), (0x21130, 0x21754)):
            self.assertEqual(a7[call - 2].op_str, 'r0, #1')
            self.assertEqual(int(a7[call].op_str.lstrip('#'), 16), tgt)
        a6 = ROMS['a6000'][1]
        for call, tgt in ((0x203c2, 0x20d00), (0x206f2, 0x20cb2), (0x206f6, 0x20cd4)):
            self.assertEqual(int(a6[call].op_str.lstrip('#'), 16), tgt)
            prev = max(a for a in a6 if a < call)
            self.assertNotEqual(a6[prev].op_str, 'r0, #1')

    def test_type_config_valid_flag_handler(self):
        # entrada 33 de la tabla 0x2a1a0 -> 0x1b0b3 (marca [0x200002c0+idx] si valor!=0); sin llamadores directos
        d = ROMS['a6000'][0]
        self.assertEqual((u32(d, 0x2a2a8) >> 16, u32(d, 0x2a2ac)), (0x2d, 0x1b0b3))
        self.assertEqual((0x2a2a8 - 0x2a1a0) // 8, 33)


class BionzSide(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d = AVCAM.read_bytes()
        assert hashlib.sha256(cls.d).hexdigest() == SHA_AVCAM

    def u(self, a):
        return struct.unpack_from('<I', self.d, a - AV_BASE)[0]

    def cstr(self, a):
        o = a - AV_BASE
        return self.d[o:self.d.index(b'\0', o)].decode('latin1')

    def test_caif_trace_table(self):
        for a, name, code, size in ((0x43fe83b4, 'ExpStartComp', 0x4000136, 0), (0x43fe8324, '>ExposureEndNotify', 0x301012a, 2),
                                    (0x43fe8318, '(ExposureReady', 0x3010129, 2), (0x43fe83e4, 'S2REQ HI', 0x301013a, 0)):
            self.assertEqual(self.cstr(self.u(a)), name)
            self.assertEqual((self.u(a + 4), self.u(a + 8)), (code, size))

    def test_gpio_primitives_and_base(self):
        # literales de la zona GPIO en av-cam: base 0xf2910000 y offsets 0x20/0x30/0x40
        lits = {a for a in range(0x4398f900, 0x4398fa40, 4)}
        vals = {self.u(a) for a in lits}
        self.assertTrue({0xf2910000, 0xf2910020, 0xf2910030, 0xf2910040} <= vals)

    def test_gpio_get_callers_in_ca_task(self):
        sys.path.insert(0, str(ROOT / 'analysis/s54'))
        import bionz_gpio_calls as G
        gets = [a for a, k, *_ in G.calls() if k == 'get']
        for a in (0x436b946e, 0x436ba68e, 0x436bb09c, 0x436bb9ec, 0x436bc0d2, 0x436bcc2c):
            self.assertIn(a, gets)

    def test_pin_variables_not_initialised_in_image(self):
        for a in range(0x43e77298, 0x43e772d0, 4):
            self.assertEqual(self.u(a), 0)


class SchematicColumns(unittest.TestCase):
    """Emparejamiento por columna de texto vectorial (manual Level 3 de A7S en docs/references; verificación visual de A6000 en el informe)."""

    def test_a7s_p4_pins_align_with_nets(self):
        lines = (ROOT / 'docs/references/sony-ilce-7s-level3-sm.txt').read_text(encoding='utf8', errors='replace').split('\n')
        col = lambda n, t: next(m.start() for m in re.finditer(r'\S+', lines[n - 1]) if m.group() == t)
        self.assertEqual(col(5780, 'CA_1ST_CURTAIN_START'), col(5877, 'P4C/SOT2_1'))
        self.assertEqual(col(5780, 'CA_RELEASE_LOCK_MSS'), col(5871, 'P4B/SIN2_1'))
        self.assertEqual(col(5788, '2ND_CURTAIN_MG'), col(5882, 'P4E/SOT2_2'))
        self.assertEqual(col(5788, '1ST_CURTAIN_MG'), col(5860, 'P4D/SIN2_2'))

    def test_a7s_bionz_side_pins(self):
        lines = (ROOT / 'docs/references/sony-ilce-7s-level3-sm.txt').read_text(encoding='utf8', errors='replace').split('\n')
        self.assertIn('SENS_B', lines[3505])
        self.assertIn('AA13', lines[3506])
        self.assertIn('CA_1ST_CURTAIN_START', lines[3507])
        self.assertIn('GPIO_9', lines[3958])
        self.assertIn('CA_1ST_CURTAIN_START', lines[3960])


if __name__ == '__main__':
    unittest.main()
