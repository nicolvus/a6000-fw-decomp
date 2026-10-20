"""S60-Claude (A7S 3.20): mensajes 0x1000/0x1001 = registros de traza a la cola 0x8f013a; contenido = eco de parámetros de exposición; sin receptor en la imagen."""
import sys, json, hashlib, unittest
from pathlib import Path
R = Path(__file__).resolve().parents[1]
for p in ('analysis/s60/claude', 'analysis/s59/claude'): sys.path.insert(0, str(R / p))
import a7dis, trace_emu, real_scen as rs
SHA = 'b857d33879d610abd185148d676de7ea0f753af3a08389994e788d617925103e'

class Identity(unittest.TestCase):
    def test_sha(self): self.assertEqual(hashlib.sha256(a7dis.D).hexdigest(), SHA)

class TraceRecord(unittest.TestCase):
    def test_record_layout(self):
        sent, log = trace_emu.run(0x43ada07a, (0, 0x11223344, 0x55667788, 0x99aabbcc))
        (q, m), = sent
        self.assertEqual(q, 0x8f013a)
        self.assertEqual((m[0], m[2], m[8]), (2, 3, 0xc))                 # tipo 2, clase 3, longitud de carga 12
        self.assertEqual(m[0x18:0x1c], bytes([1, 0, 0x00, 0x10]))         # unidad 1, id 0x1000
        self.assertEqual([x[0] for x in log], ['alloc', 'send'])
    def test_id_1001(self):
        (q, m), = trace_emu.run(0x43ada0b4, (0, 1, 2, 3))[0]
        self.assertEqual(m[0x1a:0x1c], bytes([1, 0x10]))
    def test_unit_mask_filters(self):
        sent, log = trace_emu.run(0x438f6864, (1, 0x1000, 0, 0), unit_ok=0)
        self.assertEqual((sent, log), ([], []))
    def test_send_failure_is_nonblocking_loss_marker(self):
        sent, log = trace_emu.run(0x438f6864, (1, 0x1000, 0, 0), send_rc=1)
        self.assertEqual([x[0] for x in log], ['alloc', 'send', 'alloc', 'force', 'free'])
        self.assertEqual(log[2][1:], (0x8f0313, 0x20))                     # marcador de pérdida (tipo 0xf) en el pool 0x8f0313

class NoReceiver(unittest.TestCase):
    def test_handle_literals_only_in_emitters(self):
        roles = json.loads((R / 'analysis/s60/claude/handle_roles.json').read_text())['roles']
        self.assertEqual(set(roles), {'0x8f0313', '0x8f013a', '0x8f0139'})
        for h, c in roles.items(): self.assertTrue(set(c) <= {'0x1f0', '0x1d4', '0x1d8', '0x1f4'}, (h, c))
    def test_api_counts(self):
        t = json.loads((R / 'analysis/s60/claude/trace_api.json').read_text())
        self.assertEqual(t['emit_callers'], {'emit1000': ['0x436f5ba6'], 'emit1001': ['0x436f5bb2'], 'm3_fields': ['0x43ada4be']})
        self.assertGreater(t['callers']['trace_evt'], 300)                 # 381: 0x1000/0x1001 son 2 de cientos de eventos
    def test_emitter_result_discarded(self):
        ins = [i.mnemonic + ' ' + i.op_str for i in a7dis.Cs(a7dis.CS_ARCH_ARM, a7dis.CS_MODE_THUMB).disasm(a7dis.D[0x436f5baa - a7dis.BASE:][:6], 0x436f5baa)]
        self.assertTrue(ins[1].startswith('mov r0, r5'))                   # r0 se sobrescribe: sin lectura del retorno

class MessageContent(unittest.TestCase):
    def test_echo_of_exposure_parameters(self):
        base = dict(shd=0x123, svd=0x456, spl=0x78, agc=0x100)
        def m(**o):
            k = dict(base); k.update(o); return rs.scenario(0x0b, 0, **k)['msgs']
        b = m()
        self.assertEqual(b[0][2:], [0x4560123, 0x78000000])               # svd<<16|shd ; spl<<24
        for f, v, idx in (('shd', 0x321, 0), ('svd', 0x654, 0), ('spl', 0x87, 0), ('agc', 0x200, 1)):
            with self.subTest(f=f): self.assertNotEqual(m(**{f: v})[idx], b[idx])
    def test_silent_modes_emit_nothing(self):
        for mode in (0x4c, 0x4d, 0x4e, 0x4f): self.assertEqual(rs.scenario(mode, 0)['msgs'], [])

if __name__ == '__main__': unittest.main()

class A6000Block(unittest.TestCase):
    """Productores del bloque de 24 B obj+0xe20 (A6000, SHA b60c845c…): hallazgo S60-Claude, verificación independiente de Sol."""
    def test_e20_producers(self):
        t = json.loads((R / 'analysis/s60/claude/e20_producers.json').read_text())
        self.assertEqual(t['producer_A_dst_offsets'], [hex(x) for x in range(0, 0x18, 2)])    # 12 u16 = 6 pares
        self.assertEqual(t['producer_B_dst_offsets'], [hex(x) for x in range(0, 0x14, 2)])    # 5 pares; el sexto sale de 0x437a5a6c
        self.assertEqual(t['producer_B_src_offsets'], ['0x48', '0x4a', '0x4c', '0x4e', '0x50', '0x52', '0x54', '0x56', '0x5c', '0x5e'])
    def test_sol_dispatch_table(self):
        v = json.loads((R / 'analysis/s60/claude/verify_sol.json').read_text())
        self.assertEqual(v['sha'], 'b60c845ccb90c0ff86b7f62f1f3f2ecda714aa20c37805959ebee2b429e56bb9')
        self.assertTrue(all(v[k] for k in ('recv_0x43806e38_calls_dispatcher', 'case4_calls_0x43b00d94', 'case3_calls_0x43b00fe6', 'case9_calls_0x43b00f62')))
        self.assertEqual(v['tbh_targets']['4'], '0x43806c28')                               # Sol: 0x43806c24 (base TBH -4); el cuerpo coincide
