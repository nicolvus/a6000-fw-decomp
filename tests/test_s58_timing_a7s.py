"""S58: productor de svd/shd/spl del IMX210 (A6000 3.21) y emulación del C_Imager de la A7S 3.20 (IMX235).

Solo lectura de binarios originales; emulación Unicorn en memoria (nunca toca cámara). Informes: docs/capture/s58-*.md.
Matriz: analysis/s58-evidence-matrix.json. Ejecutar: python3 -m unittest tests.test_s58_timing_a7s  (usa analysis/s58, s57, s55)
"""
import hashlib
import json
import random
import struct
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for sub in ('s58', 's57', 's56', 's55'):
    sys.path.insert(0, str(ROOT / 'analysis' / sub))
import gpio_calls_diff as G
from wtrace import W
import timing_model as TM
import a6_verify as V1
import a7_verify as V2
import a10_true_matrix as TX
import a7s_emu as AE
import a7s_p2s as PP
from a9_a7s_scenarios import scenario

SHA = {
    'A6000': 'b60c845ccb90c0ff86b7f62f1f3f2ecda714aa20c37805959ebee2b429e56bb9',
    'A7S': 'b857d33879d610abd185148d676de7ea0f753af3a08389994e788d617925103e',
}
B = 0x43541000


class Integrity(unittest.TestCase):
    def test_sha(self):
        for name, sha in SHA.items():
            self.assertEqual(hashlib.sha256(G.MODELS[name]['path'].read_bytes()).hexdigest(), sha)
        self.assertEqual(hashlib.sha256((ROOT / 'analysis/rea-independent/input/av-cam.bin').read_bytes()).hexdigest(), SHA['A6000'])

    def test_vtable_a7s_identity(self):
        """El SetExposure de la A7S es 0x436f4168 (vtable+0x28); 0x436f4a94 (vtable+0x30) es SetRead (corrige S57)."""
        d = G.MODELS['A7S']['path'].read_bytes()
        v = lambda off: struct.unpack_from('<I', d, 0x43fce050 + off - B)[0]
        self.assertEqual((v(0x20), v(0x28), v(0x30), v(0x38)), (0x436f3b45, 0x436f4169, 0x436f4a95, 0x436f5a15))


class Itstate(unittest.TestCase):
    def test_it_block_regression(self):
        """Unicorn 2.1.4 deja ITSTATE activo tras saltar instrucciones condicionales; wtrace lo limpia (caso 598/600 -> 600/600)."""
        T = 4205312738
        M = dict(s0=63524817, lt=70535, fb=597187, F=66796875, vmax=4176, shmin=23, hmax=3763, svr=1)
        w = W(ambito=V1.AMB, fill=0)
        self.assertEqual(V1.real(w, T, M, 54_000_000), TM.time_split(T, M, 54_000_000)[:3])
        self.assertEqual(TM.time_split(T, M, 54_000_000)[2], 0)


class AETimingA6000(unittest.TestCase):
    def test_time_split_matches_firmware(self):
        """0x4383d4d0 real == modelo Python (n, shd, spl) con M, T y reloj aleatorios."""
        rnd = random.Random(580); ok = tot = 0
        for _ in range(60):
            M = dict(s0=rnd.choice([0, 1_000_000, rnd.randrange(1 << 28)]), lt=rnd.choice([1, 4096, rnd.randrange(1, 1 << 24)]), fb=rnd.randrange(1 << 20),
                     F=rnd.choice([1, 17_100_000, rnd.randrange(1, 1 << 22)]), vmax=rnd.choice([4176, rnd.randrange(1 << 16)]), shmin=rnd.randrange(0, 40),
                     hmax=rnd.choice([0, 864, rnd.randrange(1 << 12)]), svr=rnd.choice([1, 2, 4, rnd.randrange(1, 8)]))
            T = rnd.choice([rnd.randrange(1 << 32), rnd.randrange(1 << 24), rnd.randrange(1 << 20) * 256]); clk = rnd.choice([0, 54_000_000, 72_000_000])
            for fill in (0, 0xa5):
                tot += 1; ok += V1.real(W(ambito=V1.AMB, fill=fill), T, M, clk) == TM.time_split(T, M, clk)[:3]
        self.assertEqual(ok, tot)

    def test_rows_match_firmware(self):
        """0x4383c9dc real == build_rows (shd/svd/spl/+36/+38/+3a por banco)."""
        rnd = random.Random(581); ok = tot = 0
        for _ in range(40):
            Gd = V2.rnd_G(rnd)
            for fill in (0, 0xa5):
                tot += 1; ok += V2.real(W(ambito=V2.AMB, fill=fill), Gd) == TM.build_rows(Gd)
        self.assertEqual(ok, tot)

    def test_tv_to_time_and_scenarios(self):
        """Tv (1/256 EV, 0x1000 <-> 1 s si 1 ud = 1/256 us) -> T con 0x4382fa94 real; descomposición con M SINTÉTICO (etiquetado)."""
        w = W(ambito=[(0x4382f000, 0x43830000), (0x43900000, 0x43930000), (0x439c0000, 0x439d0000)], fill=0)
        self.assertEqual(w.call(0x4382fa94, 0x1000), 256_000_000)
        self.assertEqual(w.call(0x4382fa94, 0x1100), 128_000_000)
        self.assertEqual(w.call(0x4382fa94, 0x1800), 1_000_000)
        self.assertEqual(w.call(0x4382fa94, 0x0c00), 0xffffffff)          # <= 0xc00: satura (T máx. 2^32 ud = 16,78 s)
        self.assertEqual(w.call(0x4382fa94, 0x0c01), 4_084_937_500)
        M = dict(s0=0, lt=4096, fb=0, F=4176 * 4096, vmax=4176, shmin=4, hmax=864, svr=1)
        got = {tv: TM.time_split(w.call(0x4382fa94, tv), M, 54_000_000)[:3] for tv in (0x1bf7, 0x1000)}
        self.assertEqual(got[0x1bf7], (0, 4161, 316)); self.assertEqual(got[0x1000], (14, 140, 864))

    def test_row_to_exposure_arg(self):
        """0x43b0893c copia la fila del banco activo a S+0xc4; 0x43849fb8 la deja en arg[0..0xf] (shd=arg+0, svd=arg+4, spl=arg+6)."""
        S, ARG, P3 = 0x45100000, 0x45200000, 0x45300000
        w = W(ambito=[(0x43849fb8, 0x4384a070), (0x43b08000, 0x43b0b000)], fill=0)
        w.u.mem_write(S, bytes(0x200)); w.u.mem_write(S, bytes([2]))
        for b in range(4):
            for k in range(4): w.w32(S + 4 + 16 * b + 4 * k, 0x11110000 * (b + 1) + k)
        w.call(0x43b0893c, S)
        self.assertEqual([w.r32(S + 0xc4 + 4 * k) for k in range(4)], [0x33330000 + k for k in range(4)])
        w.u.mem_write(P3, bytes([1, 0, 0, 0]) + struct.pack('<II', 0xaaaa, 0xbbbb)); w.u.mem_write(ARG, bytes(0x40)); w.w32(S + 0xd4, 0xdead0001)
        w.call(0x43849fb8, S, 0, P3, ARG, stack=(0, 0))
        self.assertEqual(w.rd(ARG, 0x10), struct.pack('<4I', 0x33330000, 0x33330001, 0x33330002, 0x33330003))
        self.assertEqual(w.r32(ARG + 0x10), 0xdead0001)

    def test_row_formula_is_not_unconditionally_host_formula(self):
        """El productor usa N*svr/VdNum; el host N/VdNum cuando VdNum>1: no son idénticos para todo estado sintético."""
        Gd = V2.rnd_G(random.Random(1)); Gd.update({'34': 0, '16': 4, '30': 6, '38': 3, '163': 0, '164': 0, '24': 0, '3a': 0})
        Gd['d0'] = [0, 0, 0, 0]
        got = V2.real(W(ambito=V2.AMB), Gd)[0]['svd']
        self.assertEqual(got, 4 * 6 // 3 - 1)
        self.assertNotEqual(got, 6 // 3 - 1)


class A7SMatrix(unittest.TestCase):
    def test_true_matrix_structure(self):
        """CORRECCIÓN S57-D: filas de 0x14 B {ptr + 16 columnas}, 69 filas, 15 columnas usadas, col = maptab[idx_modo]."""
        self.assertEqual(len(TX.R), 69); self.assertEqual(sorted(set(TX.mapcol)), list(range(15)))
        col = lambda m: TX.mapcol[TX.modes.index(m)]
        self.assertEqual([col(m) for m in (0x0b, 0x35, 0x4c, 0x4d, 0x4e, 0x4f, 0x50, 0x51)], [0, 1, 5, 5, 12, 13, 12, 13])
        cmp_ = lambda a, b: [r['addr'] for r in TX.R if TX.value(r, a) != TX.value(r, b)]
        self.assertEqual((len(cmp_(0x4c, 0x4e)), len(cmp_(0x4d, 0x4f)), len(cmp_(0x4e, 0x4f)), len(cmp_(0x4c, 0x4d)), len(cmp_(0x0b, 0x4e))), (14, 11, 4, 0, 45))
        self.assertEqual(sorted(cmp_(0x4e, 0x4f)), [1, 9, 10, 11])
        self.assertEqual(sorted(cmp_(0x0b, 0x35)), [1, 9, 10, 11])                    # mismo conjunto de sub-modo en foto normal

    def test_setmode_loads_columns(self):
        """SetMode real (0x436f3b44) deja en el banco sombra exactamente la columna estática (69/69) para cada modo."""
        for m in (0x0b, 0x35, 0x4c, 0x4d, 0x4e, 0x4f):
            e = AE.A7S(); self.assertEqual(e.setmode(m), 0)
            self.assertTrue(all(e.rd(r['ptr'], 1)[0] == TX.value(r, m) for r in TX.R), hex(m))


class A7SExposure(unittest.TestCase):
    def test_timing_register_map(self):
        """SetExposure real (0x436f4168): svd 12 b -> 0x02/0x03, spl 12 b -> 0x04/0x05, shd 14 b -> 0x06/0x07; bits altos preservados."""
        rnd = random.Random(582); ok = tot = 0
        for _ in range(30):
            svd, shd, spl = rnd.randrange(0x10000), rnd.randrange(0x10000), rnd.randrange(0x10000); mode = rnd.choice([0x0b, 0x4e, 0x4f, 0x4c]); shut = rnd.choice([0, 1, 3, 4])
            for fill in (0, 0xa5):
                e = AE.A7S(fill=fill); e.setmode(mode); b = AE.shadow(e); r = e.setexposure(shd=shd, svd=svd, spl=spl, shut=shut); a = AE.shadow(e)
                exp = {2: (svd & 0xff, 255), 3: ((svd >> 8) & 15, 15), 4: (spl & 0xff, 255), 5: ((spl >> 8) & 15, 15), 6: (shd & 0xff, 255), 7: ((shd >> 8) & 63, 63)}
                tot += 1; ok += r == 0 and all((a[(0x81, k)][1] & m) == v and (a[(0x81, k)][1] & ~m & 255) == (b[(0x81, k)][1] & ~m & 255) for k, (v, m) in exp.items())
        self.assertEqual(ok, tot)

    def test_shutmode_support(self):
        """ShutMode 0,1,3,4 válidos; 2 y >=5 -> error 1 (sin tocar registros de temporización). reg 0x01 = 0/0x04/0x14/0x40 (modo 0x4e)."""
        want = {0: 0x00, 1: 0x04, 3: 0x14, 4: 0x40}
        for shut in range(6):
            e = AE.A7S(); e.setmode(0x4e); r = e.setexposure(shd=0x123, svd=0x456, spl=0x78, shut=shut); s = AE.shadow(e)
            self.assertEqual(r, 0 if shut in want else 1)
            if shut in want:
                self.assertEqual(s[(0x81, 1)][1], want[shut]); self.assertEqual(s[(0x81, 0)][1] & 8, 8)   # bit 3 (tipo SSB) del reg 0x00
            else:
                self.assertEqual(s[(0x81, 0)][1] & 8, 0)

    def test_setread_gain_flag_not_exposure(self):
        """El 'pulso arg+2 > 0x1000' de S57 está en SetRead (0x436f4a94, código de ganancia), no en SetExposure."""
        for agc, flag in ((0x1000, 0), (0x1001, 1), (0x2000, 1)):
            e = AE.A7S(); e.setmode(0x0b); e.setread(agc=agc); self.assertEqual(e.rd(AE.O + 0x3d7, 1)[0], flag)
        e = AE.A7S(); e.setmode(0x0b); e.setexposure(shd=0x123, svd=0x456, spl=0x78, shut=1); self.assertEqual(e.rd(AE.O + 0x3d7, 1)[0], 0)

    def test_gain_request_consumer_sets_then_clears_register_5f(self):
        for mode in (0x0b, 0x4c, 0x4d, 0x4e, 0x4f):
            e = AE.A7S(); e.setmode(mode); e.setread(agc=0x1001)
            before = AE.shadow(e)[(0x81, 0x5f)][1]
            e.call(0x436f459c, AE.O)
            self.assertEqual(AE.shadow(e)[(0x81, 0x5f)][1], before | 0x10)
            self.assertEqual(e.rd(AE.O + 0x3d7, 1), b'\x00')
            e.call(0x436f459c, AE.O)
            self.assertEqual(AE.shadow(e)[(0x81, 0x5f)][1], before & ~0x10)


class A7SExecute(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sc = {(m, s): scenario(m, shut=s) for m in (0x0b, 0x35, 0x4c, 0x4d, 0x4e, 0x4f) for s in (0, 1)}

    def test_second_device_is_not_dropped(self):
        for result in self.sc.values():
            decoded = PP.device_regs([bytes.fromhex(t) for t in result['tx']])
            self.assertEqual(len(decoded), 100)
            self.assertIn((0x83, 0x17, 0x4a), decoded)
            self.assertEqual(sum(dev == 0x81 for dev, _, _ in decoded), 99)

    def test_decoder_rejects_truncated_payload(self):
        with self.assertRaises(ValueError):
            PP.device_regs([bytes.fromhex('81038117')])

    def test_ordered_snapshots_preserve_records(self):
        result = self.sc[(0x4e, 0)]
        self.assertEqual(len(result['records']['init']), 98)
        self.assertEqual(result['records']['pre_exec'], result['records']['setread'])
        self.assertEqual(result['err'], None)


    def test_p2s_frames(self):
        """Execute real: 5 transacciones P2S (FIFO 0xf3c00340+4i), 99 escrituras [81|03|81|ADDR|DATO]; mismas direcciones en todos los modos."""
        for k, o in self.sc.items():
            self.assertEqual(o['ret']['exec'], 0); self.assertEqual(len(o['tx']), 5); self.assertEqual(len(o['seq']), 99)
            self.assertTrue(all(bytes.fromhex(t)[0] == 0x81 for t in o['tx']))
            self.assertEqual([a for a, v in o['seq']], [a for a, v in self.sc[(0x0b, 0)]['seq']])
        self.assertEqual(bytes.fromhex(self.sc[(0x4e, 0)]['tx'][0])[:10].hex(' '), '81 03 81 00 0c 81 03 81 01 00')

    def test_effective_state_differences(self):
        """Estado efectivo transmitido: ShutMode solo cambia reg 0x01; 0x4c vs 0x4e: 14 regs; 0x4e vs 0x4f: 4 regs (mismas que 0x0b vs 0x35)."""
        fin = lambda o: {a: v for a, v in o['seq']}
        df = lambda a, b: sorted(k for k in set(fin(a)) | set(fin(b)) if fin(a).get(k) != fin(b).get(k))
        self.assertEqual(df(self.sc[(0x4e, 0)], self.sc[(0x4e, 1)]), [1])
        self.assertEqual(len(df(self.sc[(0x4c, 0)], self.sc[(0x4e, 0)])), 14)
        self.assertEqual(df(self.sc[(0x4e, 0)], self.sc[(0x4f, 0)]), [1, 9, 10, 11])
        self.assertEqual(df(self.sc[(0x4e, 0)], self.sc[(0x4e, 0)]), [])

    def test_execute_messages_only_photo_modes(self):
        """Execute envía los mensajes 0x438f6864 (ids 0x1000/0x1001) incondicionalmente solo en 0x0b/0x35/0x37/0x38; no en 0x4c/0x4d/0x4e/0x4f (estado de driver a cero)."""
        self.assertEqual(self.sc[(0x0b, 0)]['nmsg']['exec'], 2)
        self.assertEqual([m[1] for m in self.sc[(0x0b, 0)]['msgs']], [0x1000, 0x1001])
        for m in (0x4c, 0x4e, 0x4f): self.assertEqual(self.sc[(m, 0)]['nmsg']['exec'], 0)


class HarnessLimits(unittest.TestCase):
    def test_unmapped_instruction_is_not_success(self):
        with self.assertRaises(RuntimeError):
            W().call(0xdead0000)

    def test_instruction_budget_is_not_success(self):
        w = W(ambito=V1.AMB)
        with self.assertRaises(RuntimeError):
            w.call(0x4383d4d0, count=1)


class Evidence(unittest.TestCase):
    def test_matrix(self):
        m = json.loads((ROOT / 'analysis/s58-evidence-matrix.json').read_text())
        self.assertGreaterEqual(len(m['entries']), 20)
        ids = [e['id'] for e in m['entries']]; self.assertEqual(len(ids), len(set(ids)))
        for e in m['entries']:
            for k in ('id', 'claim', 'model', 'firmware', 'sha256', 'address', 'function', 'data', 'interpretation', 'status', 'validation_method', 'references', 'test', 'limitations'):
                self.assertIn(k, e)
            self.assertIn(e['status'], {'VERIFICADO', 'PARCIAL', 'INFERENCIA', 'HIPOTESIS', 'NO_VERIFICADO', 'DESCARTADO'})
        self.assertEqual(sorted(m['hypotheses']), sorted('H58-%d' % i for i in range(1, 13)))
        for hypothesis in m['hypotheses'].values():
            for key in ('support', 'against', 'address', 'function', 'binary', 'instructions', 'dependencies', 'test', 'limitations', 'next_experiment'):
                self.assertIn(key, hypothesis)


if __name__ == '__main__':
    unittest.main()
