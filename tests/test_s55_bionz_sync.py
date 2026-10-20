"""S55: origen de los pares (canal, bit) GPIO de BIONZ (base de backup BK4), consumidores de pines y eventos de exposición.

Solo lectura de binarios originales. Informes: docs/capture/s55-*.md. Matriz: analysis/s55-evidence-matrix.json.
Ejecutar: python3 -m unittest tests.test_s55_bionz_sync   (≈3 min: desensamblado lineal de dos blobs)
"""
import hashlib
import re
import struct
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'analysis/s55'))
import gpio_calls_diff as G
import pin_init as PI
from bk4 import BK4
from var_users import users

FW = ROOT / 'firmware/extracted'
SHA = {
    'A6000': 'b60c845ccb90c0ff86b7f62f1f3f2ecda714aa20c37805959ebee2b429e56bb9',
    'A7S': 'b857d33879d610abd185148d676de7ea0f753af3a08389994e788d617925103e',
}
LIRO = FW / 'fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha15_unpacked_unpacked/kmod/liro.ko'
NFC = LIRO.with_name('nfc.ko')
BASE = 0x43541000
BK = {m: BK4(ROOT / p) for m, p in PI.BKF.items()}
IMG = {m: G.MODELS[m]['path'].read_bytes() for m in G.MODELS}


def pin(model, id_):
    b = BK[model]
    return None if b.entry(id_) is None or b.u32(b.ptr(id_)) == 0xffffffff else b.u32(b.ptr(id_))


class Integrity(unittest.TestCase):
    def test_sha(self):
        for m, d in IMG.items():
            self.assertEqual(hashlib.sha256(d).hexdigest(), SHA[m])

    def test_bk4_structure(self):
        # coherencia interna del formato inferido de backup.ko: suma de cuentas == nº de entradas de cabecera
        for m, b in BK.items():
            self.assertEqual(sum(c for c, _ in b.sids), b.u32(0x14), m)
            self.assertEqual(max(base + c for c, base in b.sids), b.u32(0x14), m)


class GpioPrimitivesA7S(unittest.TestCase):
    """Equivalencia A7S/A6000: mismos bytes de las primitivas (salvo destinos de BL/literales) y mismos llamadores."""

    def fn(self, m, key, n):
        a = G.MODELS[m][key]
        return IMG[m][a - BASE:a - BASE + n]

    def test_get_identical_shape(self):
        # gpio_get: 16 B iniciales (cmp r0,#0x11; push; mov; mov; bhi; bl) idénticos salvo el BL al lector DIR
        a, b = self.fn('A6000', 'get', 16), self.fn('A7S', 'get', 16)
        self.assertEqual(a[:10], b[:10])

    def test_cfg_identical_shape(self):
        self.assertEqual(self.fn('A6000', 'cfg', 24)[:12], self.fn('A7S', 'cfg', 24)[:12])

    def test_gpio_base_literal(self):
        for m, d in IMG.items():
            self.assertIn(struct.pack('<I', 0xf2910000), d, m)

    def test_call_site_counts(self):
        r = {m: G.scan(m)['sites'] for m in G.MODELS}
        cnt = lambda s, k: sum(1 for x in s if x['kind'] == k)
        self.assertEqual((cnt(r['A6000'], 'get'), cnt(r['A6000'], 'cfg'), cnt(r['A6000'], 'set')), (50, 43, 4))
        self.assertEqual((cnt(r['A7S'], 'get'), cnt(r['A7S'], 'cfg'), cnt(r['A7S'], 'set')), (50, 43, 5))


class PinDatabase(unittest.TestCase):
    def test_service_slot_is_backup_read_4byte(self):
        # wrapper = ldr.w r3,[r3,#0x2e0] en ambos blobs
        for m, w in PI.WRAP.items():
            code = IMG[m][w - BASE:w - BASE + 0x10]
            self.assertIn(struct.pack('<H', 0xf8d3)[:2] + struct.pack('<H', 0x32e0), code, m)
        # tabla API de liro.ko: relocación de .init.data en offset 0x2e0-0x24 → Backup_read_4Byte
        out = subprocess.run(['readelf', '-r', '--wide', str(LIRO)], capture_output=True, text=True).stdout
        sec = out.split("'.rel.init.data'")[1].split('Relocation section')[0]
        slot = {int(m.group(1), 16) + 0x24: m.group(2) for m in re.finditer(r'^([0-9a-f]{8})\s+\w+\s+R_ARM_ABS32\s+[0-9a-f]+\s+(\S+)', sec, re.M)}
        self.assertEqual(slot[0x2e0], 'Backup_read_4Byte')
        self.assertEqual(slot[0x200], 'osal_dynamic_id')        # ancla ya conocida de S49

    def test_known_immediate_matches_database(self):
        # (0xf90343, 0xf90344) → (15, 5) y el código llama gpio_set(15,5,0) con inmediatos (A6000 0x436d6700, A7S usa los mismos IDs)
        for m in BK:
            self.assertEqual((pin(m, 0xf90343), pin(m, 0xf90344)), (15, 5))
        d = IMG['A6000']
        o = 0x436d6700 - BASE
        self.assertEqual(d[o:o + 6], bytes.fromhex('0f20' '0521' '0022'))      # movs r0,#0xf; movs r1,#5; movs r2,#0

    def test_nfc_calibration(self):
        # nfc.ko usa (0xf904da,db) para la IRQ y (0xf904dc,dd) para RFDET; esquema: NFC_IRQ=GPIO_S_4, XNFC_RFDET=GPIO_S_8
        d = NFC.read_bytes()
        for i in (0xf904da, 0xf904db, 0xf904dc, 0xf904dd):
            self.assertIn(struct.pack('<I', i), d)
        for m in BK:
            self.assertEqual((pin(m, 0xf904da), pin(m, 0xf904db)), (0, 4))
            self.assertEqual((pin(m, 0xf904dc), pin(m, 0xf904dd)), (0, 8))

    def test_ca_pin_vars_identical_across_models(self):
        rows = {m: PI.run(m) for m in PI.INIT}
        key = lambda r: (r['id'], r['value'])
        a = [key(r) for r in rows['A6000'] if r['id'] is not None]
        b = [key(r) for r in rows['A7S'] if r['id'] is not None]
        self.assertEqual(a, b)
        self.assertEqual(len(a), 16)
        # las variables de S54 (0x43e77298..0x43e772d4) son exactamente las que escribe el inicializador
        vs = sorted(r['var'] for r in rows['A6000'] if r['id'] is not None)
        self.assertEqual((vs[0], vs[-1]), (0x43e77298, 0x43e772d4))
        self.assertTrue(all(0x43e77298 <= v <= 0x43e772d4 for v in vs))

    def test_variables_unwritten_in_image(self):
        # el valor 0 de la imagen no es el de ejecución: las 16 celdas valen 0 en el blob
        for v in range(0x43e77298, 0x43e772d8, 4):
            self.assertEqual(struct.unpack_from('<I', IMG['A6000'], v - BASE)[0], 0)


class Consumers(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.u = {m: users(m) for m in G.MODELS}

    def test_same_consumer_structure(self):
        sig = lambda m: [sorted({hex(r['id']) for r in self.u[m] if r['func'] == f}) for f in sorted({r['func'] for r in self.u[m]})]
        self.assertEqual(sig('A6000'), sig('A7S'))
        self.assertEqual(len(sig('A6000')), 14)

    def test_all_consumers_in_ca_task_cluster(self):
        fs = sorted({r['func'] for r in self.u['A6000']})
        self.assertTrue(all(0x436b8a00 <= f < 0x436bd000 for f in fs), [hex(f) for f in fs])

    def test_no_reader_has_bit_9_outside_bank0(self):
        # ningún par (canal,bit) usado por el código tiene bit 9 salvo (0,9)=GPIO_S_9: GPIO_9 no se lee por esta vía (INFERENCIA: bit==n)
        b = BK['A6000']
        lits = {struct.unpack_from('<I', IMG['A6000'], o)[0] for o in range(0, len(IMG['A6000']) - 3, 4)}
        pairs = []
        for ix in range(b.sids[0xf9][0] - 1):
            i = 0xf90000 + ix
            if i in lits and pin('A6000', i) is not None and pin('A6000', i + 1) is not None:
                pairs.append((pin('A6000', i), pin('A6000', i + 1)))
        self.assertTrue([p for p in pairs if p[1] == 9 and p[0] != 0] == [])


class ExposureEvents(unittest.TestCase):
    def test_exposure_end_notify_handler_has_no_gpio(self):
        # 0x436b8aec envía el paquete CAIF (op 0x436ba234) y traza 0x12a; no llama a primitivas GPIO
        ins = [i for i in G.disasm(IMG['A6000']) if 0x436b8aec <= i.address < 0x436b8b28]
        tg = {G.MODELS['A6000'][k] for k in ('get', 'cfg', 'set')} | {0x43b5e2a4, 0x43b5e2b0}
        calls = [int(i.op_str[1:], 16) for i in ins if i.mnemonic == 'bl']
        self.assertEqual(calls, [0x436ba234, 0x43acabe8])
        self.assertFalse(set(calls) & tg)

    def test_pin_drivers_at_image_read_events(self):
        # ImageReadStart (0x12d) y 0x128 manejan (7,15); 0x12c/0x12f manejan (7,13): set/clear de pines de salida
        d = G.disasm(IMG['A6000'])
        by = {i.address: i for i in d}
        self.assertEqual(by[0x436b8a9e].op_str, '#0x43b5e2a4')   # set
        self.assertEqual(by[0x436b8ace].op_str, '#0x43b5e2b0')   # clear
        for m_, p in ((0xf9045d, 7), (0xf9045e, 15), (0xf90457, 7), (0xf90458, 13)):
            self.assertEqual(pin('A6000', m_), p)


if __name__ == '__main__':
    unittest.main()
