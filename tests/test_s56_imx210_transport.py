"""S56: transporte de registros del IMX210 (registro sombra -> trama P2S -> MMIO), CISIF, ShutMode, A7S diferencial y candidatos SENS_B.

Solo lectura de binarios originales; la emulación (Unicorn) corre en memoria y nunca toca cámara. Informes: docs/capture/s56-*.md.
Matriz: analysis/s56-evidence-matrix.json. Ejecutar: python3 -m unittest tests.test_s56_imx210_transport  (≈2 min la primera vez: desensamblado lineal)
"""
import hashlib
import json
import re
import struct
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'analysis/s56'))
sys.path.insert(0, str(ROOT / 'analysis/s55'))
import gpio_calls_diff as G
import rec_users as R
from xr import index
from p2s_emu import P2S, frames
from setexp_emu import SetExp

B = 0x43541000
SHA = {
    'A6000': 'b60c845ccb90c0ff86b7f62f1f3f2ecda714aa20c37805959ebee2b429e56bb9',
    'A7S': 'b857d33879d610abd185148d676de7ea0f753af3a08389994e788d617925103e',
}
IMG = {m: G.MODELS[m]['path'].read_bytes() for m in G.MODELS}
_, IDX = index('A6000')
_, IDX7 = index('A7S')


def u32(m, a):
    return struct.unpack_from('<I', IMG[m], a - B)[0]


def callers(idx, t):
    return sorted(a for a, _ in idx['calls'].get(t, []))


def trim(b):
    out, i = b'', 0
    while i < len(b) and b[i] == 0x81 and b[i + 1]:
        out += b[i:i + 2 + b[i + 1]]
        i += 2 + b[i + 1]
    return out


def wire(e, mode, recs):
    return [p for t in e.tx(mode, recs)[0] for p in frames(trim(t))]


class Integrity(unittest.TestCase):
    def test_sha(self):
        for m, d in IMG.items():
            self.assertEqual(hashlib.sha256(d).hexdigest(), SHA[m], m)


class SetExposureChain(unittest.TestCase):
    """S56-A: SetExposure solo escribe registros sombra; los envía el consumidor 0x436d75f8 vía Execute."""

    def test_callers_of_setexposure_wrapper(self):
        self.assertEqual(callers(IDX, 0x436d6320), [0x438c79fc, 0x438c830c, 0x438c8824, 0x438cc894, 0x43ae937c])

    def test_setexposure_is_vtable_slot_28(self):
        vt = u32('A6000', 0x4401eee4 + 0x7e38) + 8
        self.assertEqual(u32('A6000', vt + 0x28) & ~1, 0x436d6f6c)
        self.assertEqual(u32('A6000', vt + 0x38) & ~1, 0x436d839c)   # Execute (envía las listas)
        self.assertEqual(u32('A6000', vt + 0x3c) & ~1, 0x436d6a34)   # Execute(0): sin datos

    def test_consumer_callers_and_lists(self):
        self.assertEqual(callers(IDX, 0x436d75f8), [0x436d7bf2, 0x436d8586, 0x436d859a])
        e = P2S()
        self.assertEqual(len(e.records(0x43fe995c)), 119)
        self.assertEqual(len(e.records(0x43fe9b50)), 8)
        self.assertEqual(len(e.records(0x43fe9b3c)), 4)

    def test_no_gpio_read_in_register_chain(self):
        for t in (0x43b5e2bc, 0x43b5e22e):   # gpio_get / gpio_cfg
            self.assertEqual([a for a in callers(IDX, t) if 0x436d5800 <= a < 0x436d9400 or 0x43ad8c00 <= a < 0x43ad9a00], [])
        self.assertEqual([a for a in callers(IDX, 0x43b5e29a) if 0x436d5800 <= a < 0x436d9400], [0x436d670a])   # solo (15,5) en el constructor

    def test_trigger_bit_setter_callers(self):
        self.assertEqual(callers(IDX, 0x43ad9116), [0x438c7a0a, 0x438c8326, 0x438c883c, 0x438cc5ce, 0x43ae936c])


class IdTable(unittest.TestCase):
    """S56-A.1: los 'IDs' son direcciones de registro de 16 bits de un mapa 0..0x155 con dato u8."""

    def test_records(self):
        ids = [R.recs[p] for p in R.tab]
        self.assertEqual(len(ids), 119)
        self.assertEqual(len(set(ids)), 118)
        self.assertEqual(max(ids), 0x155)
        self.assertEqual([i for i in set(ids) if ids.count(i) > 1], [1])
        self.assertEqual([hex(p) for p in R.tab if R.recs[p] == 1], ['0x4401ca2c', '0x4401c734'])
        self.assertTrue(all(IMG['A6000'][p - B + 3] == 0 for p in R.tab))

    def test_id_semantics_from_setexposure_slots(self):
        G_ = R.G
        rid = lambda off: R.recs[R.u(G_ + off)]
        self.assertEqual([rid(o) for o in (0x6a34, 0x584, 0x77a4, 0x3de8, 0x48f8, 0x70d0)], [3, 4, 5, 6, 7, 8])
        self.assertEqual([rid(o) for o in (0x2828, 0x5ba4, 0x56e8, 0x568c, 0x2690, 0x3d94)], [0x144, 0x145, 0x146, 0x147, 0x148, 0x149])


class P2STransport(unittest.TestCase):
    """S56-A.2/A.3 por emulación del código real: lista de registros -> trama FIFO."""

    def test_formatter_object_constants(self):
        e = P2S(channel=1)
        self.assertEqual([e.u8(e.P + i) for i in range(4)], [0, 0x10, 8, 0x81])   # sin byte extra, dir 16 bit, dato 8 bit, cabecera 0x81

    def test_channel_table(self):
        t = u32('A6000', 0x4401eee4 + 0x13cc)
        rows = [[u32('A6000', t + 12 * i + 4 * k) for k in range(3)] for i in range(3)]
        self.assertEqual(rows, [[0xf3c00300, 0xf3c00800, 0xf3c00900], [0xfc088300, 0xfc088800, 0xfc088900], [0xfc089300, 0xfc089800, 0xfc089900]])
        sel = u32('A6000', 0x43bc16d4)   # tabla instancia -> canal
        self.assertEqual([u32('A6000', 0x43bc16d4 + 4 * i) for i in range(3)], [1, 2, 0])
        self.assertEqual(sel, 1)   # instancia 0 (única llamada de C_Imager) -> canal 1 = P2S(DFE0)

    def test_single_register_frame(self):
        e = P2S()
        txs, regs = e.tx(2, [(1, 0x40)])
        self.assertEqual(trim(txs[0]).hex(' '), '81 04 81 00 01 40')
        self.assertIn(('0xfc088800', 2), regs)           # SyncMode 2

    def test_burst_and_new_frame(self):
        e = P2S()
        t = trim(e.tx(2, [(0x100, 0), (0x101, 0x38), (0x102, 0)])[0][0])
        self.assertEqual(t.hex(' '), '81 06 81 01 00 00 38 00')                        # consecutivos: una sola trama, dirección autoincremental
        t = trim(P2S().tx(2, [(1, 0x40), (0x65, 0xcc)])[0][0])
        self.assertEqual(t.hex(' '), '81 04 81 00 01 40 81 04 81 00 65 cc')            # no consecutivo: trama nueva

    def test_full_register_file_roundtrip(self):
        e = P2S()
        recs = e.records(0x43fe995c)
        txs, _ = e.tx(2, recs)
        self.assertEqual([len(trim(t)) for t in txs], [127, 87])                      # RAM de datos de 128 B -> dos transmisiones
        self.assertEqual(wire(P2S(), 2, recs), recs)                                    # ID lógico == dirección; dato == byte transmitido

    def test_immediate_list_has_no_start_pulse(self):
        e = P2S()
        recs = e.records(0x43fe9b50)
        txs, regs = e.tx(0, recs)
        self.assertEqual(len(txs), 1)
        self.assertEqual(frames(trim(txs[0])), recs)
        self.assertIn(('0xfc088800', 0), regs)           # SyncMode 0 y sin pulso 1,0,1 en 0xfc088808
        self.assertEqual([v for a, v in regs if a == '0xfc088808'], [1])


class ShutModeRegisters(unittest.TestCase):
    """S56-C.2: efecto de SetExposure sobre el mapa de registros (emulación del código real)."""

    def test_timing_words_to_registers(self):
        rc, ch = SetExp().run(0x0b, 0, 0x1234, 0x0abc, 0x0567)
        self.assertEqual(rc, 0)
        got = {k: v[1] for k, v in ch.items()}
        for bank in (0, 0x141):   # banco A: 3..8; espejo condicional: 0x144..0x149
            base = 3 if bank == 0 else 0x144
            self.assertEqual([got[hex(base + i)] for i in range(6)], [0xbc, 0x0a, 0x34, 0x12, 0x67, 0x05])   # svd lo/hi, shd lo/hi, spl lo/hi

    def test_shut_selector_register1(self):
        vals = {}
        for s in range(5):
            _, ch = SetExp().run(0x0b, s, 0x1234, 0x0abc, 0x0567, b8=0x11, b14=0x22)
            vals[s] = {k: v[1] for k, v in ch.items() if k.startswith(('0x1@', '0x100', '0x101'))}
        self.assertEqual({s: v.get('0x1@4401ca2c', 0x40) for s, v in vals.items()}, {0: 0x40, 1: 0xc4, 2: 0x94, 3: 0xd4, 4: 0xc0})
        self.assertEqual({s for s, v in vals.items() if '0x100' in v}, {2})              # solo ShutMode 2 carga 0x100/0x101 desde el argumento
        self.assertEqual(vals[2]['0x100'], 0x11)
        self.assertEqual(vals[2]['0x101'], 0x22)

    def test_ssb_pulse_is_register1_bit3_written_twice(self):
        for shut, base in {0: 0x40, 1: 0xc4, 4: 0xc0}.items():
            e = SetExp()
            e.run(0x0b, shut, 0x1234, 0x0abc, 0x0567)
            e.u.mem_write(e.O + 0x268, bytes([1]))
            e.call(0x436d7c08, e.O)
            self.assertEqual(e.u8(e.O + 0x268), 0)                                      # petición consumida
            w = wire(e, 2, e.records(0x43fe995c))
            self.assertEqual([v for i, v in w if i == 1], [base | 8, base])             # 1.ª con bit3=1, 2.ª con bit3=0


class CisifIsReceiveSide(unittest.TestCase):
    """S56-B: CISIF = mapa de carriles/códigos de sincronía del receptor; el bus de configuración es P2S."""

    def test_cisif_strings_and_p2s_callers_are_disjoint(self):
        s = IMG['A6000']
        for t in (b'ImagerCommon::SetCISIFRequest Unknown index number', b'ImagerCommon::GetCISIFSyncCodeRequest Unknown index number',
                  b'ImagerCommon::Update_CISIFConnectParam Unknown index number'):
            self.assertIn(t, s)
        self.assertEqual(callers(IDX, 0x436d5e04), [0x436d761c, 0x43ad92b6])          # formateador P2S: solo consumidor y tabla de arranque
        refs = [a for a, v, r in IDX['lits'] if r == 0x43c9450d]
        self.assertEqual(refs, [0x436d8cb0])
        self.assertFalse([a for a in callers(IDX, 0x436d5e04) if 0x436d8c00 <= a < 0x436d8f00])

    def test_cisif_request_is_12_lane_pairs(self):
        # 0x43ad9478 recorre 0x18 B = 12 pares (carril, bit) con máscaras de 16 bits y entrega a 0x436daf88
        self.assertIn(0x436daf88, [t for t in IDX['calls'] if any(0x43ad9478 <= a < 0x43ad94d8 for a, _ in IDX['calls'][t])])


class DifferentialA7S(unittest.TestCase):
    """S56-D: IMX235 (A7S) frente a IMX210 (A6000), con evidencia de bytes."""

    def test_same_p2s_hardware_map(self):
        t = u32('A7S', 0x44024540 + 0x1780)
        rows = [[u32('A7S', t + 12 * i + 4 * k) for k in range(3)] for i in range(3)]
        self.assertEqual(rows[1], [0xfc088300, 0xfc088800, 0xfc088900])
        self.assertEqual(rows[0][0], 0xf3c00300)

    def test_a7s_record_format_has_device_byte(self):
        t = u32('A7S', 0x44024540 + 0x8400)
        out = []
        for i in range(2000):
            p = u32('A7S', t + 4 * i)
            if not p:
                break
            out.append((IMG['A7S'][p - B], struct.unpack_from('<H', IMG['A7S'], p - B + 2)[0], IMG['A7S'][p - B + 4]))
        self.assertEqual(len(out), 95)
        self.assertEqual(sorted({o[0] for o in out}), [0x81, 0x83])
        self.assertEqual(sum(1 for o in out if o[0] == 0x83), 1)
        self.assertEqual([o[1] for o in out[:4]], [0, 1, 1, 2])                            # ID 1 también duplicado (pulso)

    def test_shutmode_tables_differ(self):
        pc7, pc6 = 0x436f4246, 0x436d70ca
        a7 = [pc7 + 2 * IMG['A7S'][pc7 - B + i] for i in range(5)]
        a6 = [pc6 + 2 * IMG['A6000'][pc6 - B + i] for i in range(5)]
        self.assertEqual(a7[2], 0x436f42fc)                                                   # A7S: ShutMode 2 cae en 'not supported'
        self.assertIn(b'ShutMode:%d is not supported.', IMG['A7S'])
        self.assertNotEqual(a6[2], 0x436d728e)                                                # A6000: ShutMode 2 soportado
        self.assertEqual(len({*a6}), 5)

    def test_a7s_pulse_flag_is_bit4_of_record_not_register1_bit3(self):
        # A7S 0x436f459c: [O+0x3d7] -> bit 0x10 del byte +4 del registro; A6000 0x436d7c08: [O+0x268] -> bit 0x08 del dato de ID 1
        d7 = IMG['A7S'][0x436f459c - B:0x436f45c4 - B]
        self.assertIn(bytes.fromhex('42f01002'), d7)   # orr r2,r2,#0x10 (Thumb-2)
        d6 = IMG['A6000'][0x436d7c08 - B:0x436d7c4a - B]
        self.assertIn(bytes.fromhex('41f00801'), d6)   # orr r1,r1,#8


class SensBCandidates(unittest.TestCase):
    """S56-E: ningún consumidor de SENS_B / CIS0_SHT_RST; los clústeres MMIO candidatos pertenecen a otros controladores."""

    def test_no_names_in_firmware(self):
        for m in IMG:
            self.assertIsNone(re.search(rb'SENS_B|SHT_RST|SHUTTER_RST|1ST_CURTAIN|CA_1ST', IMG[m]), m)

    def test_candidate_clusters_owned_by_non_imager_functions(self):
        owners = {}
        for a, v, r in IDX['lits']:
            if r is None and v % 4 == 0 and (0xf2a10000 <= v < 0xf2a40000 or 0xf2403000 <= v < 0xf2407000):
                owners.setdefault(v, set()).add(a)
        self.assertTrue(owners)
        lo, hi = min(a for s in owners.values() for a in s), max(a for s in owners.values() for a in s)
        self.assertGreaterEqual(lo, 0x43932000)
        self.assertLess(hi, 0x43992000)                       # fuera de 0x436d5800-0x436d9400 (imager) y de 0x438c.. (captura)


class MatrixConsistency(unittest.TestCase):
    def test_matrix_refs_exist(self):
        m = json.loads((ROOT / 'analysis/s56-evidence-matrix.json').read_text())
        self.assertEqual(m['phase'], 'S56')
        src = Path(__file__).read_text()
        for e in m['entries']:
            cls = e['test'].split('::')[-1]
            self.assertIn(f'class {cls}', src, e['id'])
            self.assertIn(e['status'], {'VERIFICADO', 'INFERENCIA', 'NO VERIFICADO', 'REFUTADA EN RUTA CONCRETA', 'PARCIAL'})
            for k in ('model', 'firmware', 'sha256', 'address', 'interpretation', 'validation_method', 'limitations'):
                self.assertIn(k, e, e['id'])


if __name__ == '__main__':
    unittest.main()
