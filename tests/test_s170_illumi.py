"""S170 — tests del módulo [ILLUMI] contra los BYTES REALES del firmware.

Cada test comprueba direcciones concretas: si una dirección cambia en el firmware
(o en el mapa de referencias), el test falla.

Método de referencias: regla PIC **estricta** (canónica del repo,
`analysis/s106_imaging_cap/pic_xref_methodology.md`):
    ldr rX,[pc,#imm]  ->  W = literal del pool
    add rX,pc         ->  destino = W + (dirección_del_add + 4)
El par se empareja con el `ldr` más cercano del mismo registro (ventana 4 KB).
"""
import bisect
import json
import struct
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = 0x43541000
BIN = ROOT / "analysis/rea-independent/input/av-cam.bin"
A7S = (ROOT / "firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/"
       "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin")
A6300 = (ROOT / "firmware/extracted/a6300-fw201/payload/firmware.tar_unpacked/"
         "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin")
ILLUMI_JSON = ROOT / "analysis/s170_illumi/illumi.json"

B = BIN.read_bytes()
A7 = A7S.read_bytes()
A63 = A6300.read_bytes()


def u16(a, blob=None):
    blob = B if blob is None else blob
    return struct.unpack_from("<H", blob, a - BASE)[0]


def u32(a, blob=None):
    blob = B if blob is None else blob
    return struct.unpack_from("<I", blob, a - BASE)[0]


def cstr(a, blob=None):
    blob = B if blob is None else blob
    o = a - BASE
    e = blob.find(b"\x00", o)
    return blob[o:e].decode("ascii", "replace")


# ---------------------------------------------------------------------------
# Las 34 trazas [ILLUMI]: (vaddr, texto exacto)
# ---------------------------------------------------------------------------
STRINGS = [
    (0x43c40570, "[ILLUMI]ADJ BLOCK ERROR"),
    (0x43c40588, "[ILLUMI]IllumiDiag::%s:%d,GetRawData Success=%ld"),
    (0x43c405b9, "[ILLUMI]IllumiDiag::%s:%d,GetIllumiData Success=%ld"),
    (0x43c405ed, "[ILLUMI]IllumiDiag::%s:%d,GetRawData Error=%ld"),
    (0x43c4061c, "[ILLUMI]ADJ COMMAND ERROR"),
    (0x43c40636, "[ILLUMI]IllumiDiag::%s:%d,reg_sync_msg_queue Err=0x%x"),
    (0x43c4066c, "[ILLUMI]IllumiDiag::%s:%d,unreg_sync_msg_queue Err=0x%x"),
    (0x43c406e6, "[ILLUMI]Parameter Err: gainMode = 0x%X"),
    (0x43c4070d, "[ILLUMI]gain = 0x%02X, gain_pre = 0x%02X"),
    (0x43c40736, "[ILLUMI]IllumiGain::%s:%d--Gain:%d, AD:0x%04X"),
    (0x43c40764, "[ILLUMI]ERR. osal_try_valloc_msg. err=0x%x, line=%d"),
    (0x43c40798, "[ILLUMI]<Send Event> key_code = 0x%x,Level:%d"),
    (0x43c407c6, "[ILLUMI]ERR. osal_snd_msg. err=0x%x, line=%d"),
    (0x43c407f3, "[ILLUMI]IllumiLevel::%s:%d--Level:%d,Data:(0x%04x)%x"),
    (0x43c4089d, "[ILLUMI]IllumiAd::%s:%d"),
    (0x43c408b5, "[ILLUMI]ERR. osal_set_timer. err=0x%x, line=%d"),
    (0x43c408e4, "[ILLUMI]ERR. osal_free_timer. err=0x%x, line=%d"),
    (0x43c40914, "[ILLUMI]ERR. osal_alloc_timer. err=0x%x, line=%d"),
    (0x43c40945, "[ILLUMI]AD MAXOVER. ADwork=0x%x, line=%d"),
    (0x43c4096e, "[ILLUMI]C_AD. ADcor=0x%x, line=%d"),
    (0x43c40990, "[ILLUMI]Gain Change Complete!"),
    (0x43c40a4a, "[ILLUMI]IllumiCam::%s:%d"),
    (0x43c40a63, "[ILLUMI]ERR. osal_unreg_sync_msg_queue_cb. err=0x%x, line=%d"),
    (0x43c40aa0, "[ILLUMI]ERR. osal_reg_sync_msg_queue_cb. err=0x%x, line=%d"),
    (0x43c40c10, "[ILLUMI]IllumiRPR0400::%s:%d"),
    (0x43c40c2d, "[ILLUMI]IllumiRPR0400::%s. osal_try_valloc_msg. err=0x%x:%d"),
    (0x43c40c69, "[ILLUMI]IllumiRPR0400::%s. osal_snd_sync_msg. err=0x%x:%d"),
    (0x43c40ca3, "[ILLUMI]IllumiRPR0400::%s. osal_free_msg. err=0x%x:%d"),
    (0x43c40cd9, "[ILLUMI]IllumiRPR0400::%s. hdr->err=0x%x:%d"),
    (0x43c40d05, "[ILLUMI]IllumiRPR0400::%s:%d. ReadDevice err=0x%x"),
    (0x43c40d37, "[ILLUMI]IllumiRPR0400::%s. osal_valloc_msg. err=0x%x:%d"),
    (0x43c40d6f, "[ILLUMI]IllumiRPR0400::%s. osal_snd_msg. err=0x%x:%d"),
    (0x43c40da4, "[ILLUMI]IllumiRPR0400::%s:%d. Backup_read ret_size=0x%x"),
    (0x43c40ddc, "[ILLUMI]IllumiRPR0400::%s:%d. WriteDevice err=0x%x"),
]

# Los 52 sitios de emisión (regla PIC estricta): sitio -> dirección de la cadena
SITES = {
    0x435abf90: 0x43c40570, 0x435ac038: 0x43c40588, 0x435ac056: 0x43c405b9,
    0x435ac08c: 0x43c405ed, 0x435ac0c2: 0x43c4061c, 0x435ac164: 0x43c40636,
    0x435ac1a8: 0x43c4066c, 0x435acb32: 0x43c406e6, 0x435acb50: 0x43c4070d,
    0x435acc0a: 0x43c40736, 0x435acc58: 0x43c40736, 0x435acdf6: 0x43c40764,
    0x435ace10: 0x43c40798, 0x435ace3c: 0x43c407c6, 0x435acf56: 0x43c407f3,
    0x435acf94: 0x43c407f3, 0x435ad138: 0x43c4089d, 0x435ad19a: 0x43c4089d,
    0x435ad238: 0x43c4089d, 0x435ad182: 0x43c408b5, 0x435adbc2: 0x43c408b5,
    0x435ad25a: 0x43c408e4, 0x435adcc8: 0x43c408e4, 0x435ad344: 0x43c40914,
    0x435ae422: 0x43c40914, 0x435ad530: 0x43c40945, 0x435ad54a: 0x43c4096e,
    0x435ad6aa: 0x43c40990, 0x435ad7ca: 0x43c40a4a, 0x435ad814: 0x43c40a4a,
    0x435ad878: 0x43c40a4a, 0x435ad7fe: 0x43c40a63, 0x435ad862: 0x43c40aa0,
    0x435adb30: 0x43c40c10, 0x435adbda: 0x43c40c10, 0x435adcb4: 0x43c40c10,
    0x435ade7e: 0x43c40c2d, 0x435adf18: 0x43c40c69, 0x435adf48: 0x43c40ca3,
    0x435adfc2: 0x43c40ca3, 0x435ae190: 0x43c40ca3, 0x435ae1ec: 0x43c40ca3,
    0x435adf98: 0x43c40cd9, 0x435ae1c2: 0x43c40cd9, 0x435ae024: 0x43c40d05,
    0x435ae088: 0x43c40d05, 0x435ae0f0: 0x43c40d37, 0x435ae160: 0x43c40d6f,
    0x435ae252: 0x43c40da4, 0x435ae27c: 0x43c40da4, 0x435ae360: 0x43c40da4,
    0x435ae2a6: 0x43c40ddc,
}

# RTTI: clase -> (nombre_addr, typeinfo, vptr, vtable_address_point, base_o_ninguno)
RTTI = {
    "IllumiDev": (0x43c4084c, 0x43fdaa74, 0x43fd04f8, 0x43fbb5c0, None),
    "IllumiAd": (0x43c40893, 0x43fdaa7c, 0x43fd03d8, 0x43fbb5e0, 0x43fdaa74),
    "IllumiCam": (0x43c40a20, 0x43fdaa8c, 0x43fd03d8, 0x43fbb600, 0x43fdaa74),
    "IllumiRPR0400": (0x43c40baf, 0x43fdaa98, 0x43fd03d8, 0x43fbb620, 0x43fdaa74),
}

# vtable (address point) -> 5 ranuras virtuales
VTABLES = {
    0x43fbb5c0: [0x439b4145] * 5,
    0x43fbb5e0: [0x435ad271, 0x435ad151, 0x435ad0fd, 0x435ad1b9, 0x435ad5e9],
    0x43fbb600: [0x43a4a1c5, 0x435ad82d, 0x435ad7dd, 0x435ad7ad, 0x435ad9f9],
    0x43fbb620: [0x435ae329, 0x435adb91, 0x435adaf5, 0x435adc39, 0x435ade21],
}

# constantes verificadas por bytes: (direccion del pool, valor)
CONSTS = [
    (0x435ace44, 0x7a0020),    # cola de eventos de camara
    (0x435ad4c4, 0x720018),    # servicio LIRO ADC
    (0x435adfd0, 0x520250),    # bus del dispositivo RPR0400
    (0x435abe38, 0x17000001),  # key_code de nivel (1)
    (0x435abe34, 0x17000002),  # key_code de nivel (2)
    (0x435ae2b0, 0x133003d),   # backup id (initialize device)
    (0x435ae2b4, 0x133003c),   # backup id (initialize device)
    (0x435ad880, 0x13303be),   # cola sync de IllumiCam
    (0x435ac170, 0x13303ba),   # cola sync de IllumiDiag
    (0x435ad4cc, 0x3ca0),      # offset GOT del canal del ADC
    (0x435ad4d4, 0xba8),       # offset GOT del codigo de correccion
]


def pic_ldr_sites(lo, hi):
    """[(addr, reg, valor_del_pool, pool_addr)] de los `ldr rX,[pc,#imm]`."""
    out = []
    a = lo
    while a < hi:
        o = a - BASE
        if o < 0 or o > len(B) - 8:
            a += 2
            continue
        h = u16(a)
        reg = lit = None
        if (h & 0xF800) == 0x4800:
            reg = (h >> 8) & 7
            lit = ((a + 4) & ~3) + ((h & 0xFF) * 4)
        elif (h & 0xFF7F) == 0xF85F:
            h2 = u16(a + 2)
            reg = (h2 >> 12) & 0xF
            lit = ((a + 4) & ~3) + ((((h2 >> 8) & 0xF) << 8) | (h2 & 0xFF))
        if reg is not None and 0 <= lit - BASE <= len(B) - 4:
            out.append((a, reg, u32(lit), lit))
        a += 2
    return out


def pic_add_sites(lo, hi):
    out = []
    a = lo
    while a < hi:
        o = a - BASE
        if o < 0 or o > len(B) - 4:
            a += 2
            continue
        h = u16(a)
        if (h & 0xFF00) == 0x4400 and ((h >> 3) & 0xF) == 15:
            out.append((a, (((h >> 7) & 1) << 3) | (h & 7)))
        a += 2
    return out


def strict_dest(site):
    """Destino de un `add rX,pc` según la regla estricta, o None."""
    by_reg = {}
    for a, reg, w, lit in pic_ldr_sites(site - 4096, site + 16):
        by_reg.setdefault(reg, []).append((a, w, lit))
    for v in by_reg.values():
        v.sort()
    h = u16(site)
    if not ((h & 0xFF00) == 0x4400 and ((h >> 3) & 0xF) == 15):
        return None
    reg = (((h >> 7) & 1) << 3) | (h & 7)
    v = by_reg.get(reg)
    if not v:
        return None
    keys = [x[0] for x in v]
    i = bisect.bisect_left(keys, site) - 1
    if i < 0:
        return None
    la, w, lit = v[i]
    if site - la > 4096:
        return None
    return (w + site + 4) & 0xFFFFFFFF


class TestS170IllumiStrings(unittest.TestCase):
    def test_34_strings_exact_text(self):
        self.assertEqual(len(STRINGS), 34)
        for addr, text in STRINGS:
            self.assertEqual(cstr(addr), text, f"cadena en {addr:#x}")

    def test_all_strings_start_with_token(self):
        for addr, text in STRINGS:
            self.assertTrue(text.startswith("[ILLUMI]"), hex(addr))
            self.assertNotIn("[ILLUMI]", text[8:])

    def test_strings_are_ordered_and_inside_block(self):
        addrs = [a for a, _ in STRINGS]
        self.assertEqual(addrs, sorted(addrs))
        self.assertEqual(addrs[0], 0x43c40570)
        self.assertEqual(addrs[-1], 0x43c40ddc)
        # el bloque de cadenas del modulo va de 0x43c4052a (pretty) a 0x43c40e89
        for a in addrs:
            self.assertTrue(0x43c4052a <= a <= 0x43c40e89, hex(a))

    def test_token_count_34_0_0(self):
        self.assertEqual(B.count(b"[ILLUMI]"), 34)
        self.assertEqual(A7.count(b"[ILLUMI]"), 0)
        self.assertEqual(A63.count(b"[ILLUMI]"), 0)

    def test_illumi_substring_counts(self):
        # apariciones de la subcadena 'Illumi': 45 / 4 / 4
        # cadenas distintas que la contienen: 43 / 4 / 4
        import re
        pat = re.compile(rb"[\x20-\x7e]{4,}")
        for blob, exp_occ, exp_ch in ((B, 45, 43), (A7, 4, 4), (A63, 4, 4)):
            self.assertEqual(blob.count(b"Illumi"), exp_occ)
            n = sum(1 for m in pat.finditer(blob) if b"Illumi" in m.group())
            self.assertEqual(n, exp_ch)

    def test_rtti_class_names_in_all_three(self):
        for nm in ("9IllumiDev", "8IllumiAd", "9IllumiCam", "13IllumiRPR0400"):
            self.assertEqual(B.count(nm.encode()), 1, nm)
            self.assertEqual(A7.count(nm.encode()), 1, nm)
            self.assertEqual(A63.count(nm.encode()), 1, nm)

    def test_no_shutter_words_in_traces(self):
        for word in (b"shutter", b"curtain", b"expos", b"iso", b"apert",
                     b"frame", b"capture", b"photo", b"compens"):
            for addr, text in STRINGS:
                self.assertNotIn(word, text.lower().encode(), f"{word} en {addr:#x}")


class TestS170IllumiPicSites(unittest.TestCase):
    def test_52_sites(self):
        self.assertEqual(len(SITES), 52)

    def test_each_site_is_add_pc_and_resolves_to_expected_string(self):
        for site, target in SITES.items():
            h = u16(site)
            self.assertEqual(h & 0xFF00, 0x4400, f"{site:#x} no es add rX,pc")
            self.assertEqual((h >> 3) & 0xF, 15, f"{site:#x} no usa pc")
            dest = strict_dest(site)
            self.assertEqual(dest, target, f"sitio {site:#x}")

    def test_every_string_is_referenced_at_least_once(self):
        refs = set(SITES.values())
        for addr, _ in STRINGS:
            self.assertIn(addr, refs, f"cadena muerta {addr:#x}")

    def test_sites_are_unique_and_in_module_region(self):
        self.assertEqual(len(set(SITES)), 52)
        for site in SITES:
            self.assertTrue(0x435ab000 <= site < 0x435af000, hex(site))

    def test_add_pc_operands_are_register_r3(self):
        # en el modulo todos los `add rX,pc` de referencia a cadena usan r3
        for site in SITES:
            h = u16(site)
            reg = (((h >> 7) & 1) << 3) | (h & 7)
            self.assertEqual(reg, 3, hex(site))


class TestS170IllumiRtti(unittest.TestCase):
    def test_typeinfo_layout(self):
        for cls, (name_addr, ti, vptr, vt, base) in RTTI.items():
            self.assertEqual(u32(ti + 4), name_addr, cls)
            self.assertEqual(u32(ti), vptr, cls)
            if base is None:
                # __class_type_info: 8 bytes (vptr + nombre), sin campo base
                self.assertNotEqual(vptr, 0x43fd03d8, cls)
            else:
                # __si_class_type_info: vptr + nombre + puntero a la clase base
                self.assertEqual(u32(ti + 8), base, cls)

    def test_vtable_slots(self):
        for ap, slots in VTABLES.items():
            for k, s in enumerate(slots):
                self.assertEqual(u32(ap + 4 * k), s, f"{ap:#x}[{k}]")

    def test_illumi_dev_is_abstract(self):
        for s in VTABLES[0x43fbb5c0]:
            self.assertEqual(s, 0x439b4145)

    def test_vtable_address_point_preceded_by_typeinfo(self):
        for cls, (name_addr, ti, vptr, vt, base) in RTTI.items():
            self.assertEqual(u32(vt - 4), ti, cls)

    def test_pure_virtual_marker_is_referenced(self):
        # 0x439b4145 es __cxa_pure_virtual: la cadena 'pure virtual method called'
        # esta en 0x43bd4de4 (referencia de S165)
        self.assertIn(b"pure virtual method called", B[0x43bd4de4 - BASE:
                                                      0x43bd4de4 - BASE + 40])


class TestS170IllumiConstants(unittest.TestCase):
    def test_constants_at_exact_addresses(self):
        for addr, val in CONSTS:
            self.assertEqual(u32(addr), val, hex(addr))

    def test_osal_ids_present_in_all_three_firmwares(self):
        for val in (0x7a0020, 0x720018, 0x520250, 0x133003c, 0x133003d):
            pat = struct.pack("<I", val)
            self.assertIn(pat, B, hex(val))
            self.assertIn(pat, A7, hex(val))
            self.assertIn(pat, A63, hex(val))

    def test_key_codes_only_in_a6000_code(self):
        # 0x17000001 / 0x17000002 aparecen como literales solo en el modulo
        for val, addr in ((0x17000001, 0x435abe38), (0x17000002, 0x435abe34)):
            self.assertEqual(u32(addr), val)
            self.assertEqual(B.count(struct.pack("<I", val)), 2 if val == 0x17000001 else 4)

    def test_liro_adc_message_id_get_d(self):
        # 0x435ad486: movw r3, #0xfff0  (id de mensaje ADJ get_d del ADC)
        self.assertEqual(u16(0x435ad486), 0xf64f)
        self.assertEqual(u16(0x435ad488), 0x73f0)

    def test_device_register_and_address(self):
        # IllumiRPR0400::GetAD -> ReadDevice(0x39, 0x46, buf, 4)
        self.assertEqual(u16(0x435adffe), 0x2039)   # movs r0, #0x39
        self.assertEqual(u16(0x435ae000), 0x2146)   # movs r1, #0x46
        self.assertEqual(u16(0x435ae004), 0x2304)   # movs r3, #4
        # PollingDevice -> ReadDevice(0x39, 0x41, ...)
        self.assertEqual(u16(0x435ae060), 0x2039)   # movs r0, #0x39
        self.assertEqual(u16(0x435ae062), 0x2141)   # movs r1, #0x41

    def test_same_device_pattern_in_a7s_and_a6300(self):
        # el codigo equivalente (movs r0,#0x39 ; movs r1,#0x46) existe en las tres fw
        pat = bytes([0x39, 0x20, 0x46, 0x21])
        for blob, name in ((B, "A6000"), (A7, "A7S"), (A63, "A6300")):
            self.assertGreaterEqual(blob.count(pat), 1, name)

    def test_event_message_layout_16_bytes(self):
        # 0x435acdda: movs r2, #0x10  (16 B) ; msg[0]=key_code, msg[2]=Level
        self.assertEqual(u16(0x435acdda), 0x2210)
        self.assertEqual(u16(0x435ace0a), 0x601e)   # str r6, [r3]      -> msg[0]
        self.assertEqual(u16(0x435ace02), 0x609d)   # str r5, [r3,#8]   -> msg[2]

    def test_trace_module_id_0x133(self):
        # movw r0, #0x133 en varias llamadas de log del modulo
        for addr in (0x435acdf2, 0x435ace06, 0x435ace30, 0x435ad52c, 0x435ad542):
            self.assertEqual(u16(addr), 0xf240, hex(addr))
            self.assertEqual(u16(addr + 2), 0x1033, hex(addr))


class TestS170IllumiJsonConsistency(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(ILLUMI_JSON.read_text(encoding="utf-8"))

    def test_json_strings_match_bytes(self):
        got = {c["vaddr"]: c["texto"] for c in self.data["cadenas"]}
        self.assertEqual(got, {a: t for a, t in STRINGS})

    def test_json_sites_match_bytes(self):
        got = {}
        for c in self.data["cadenas"]:
            for s in c["sitios"]:
                got[s] = c["vaddr"]
        self.assertEqual(got, SITES)

    def test_json_counts(self):
        c = self.data["cifras"]
        self.assertEqual(c["cadenas_distintas"], 34)
        self.assertEqual(c["ocurrencias_token_a6000"], 34)
        self.assertEqual(c["sitios_pic"], 52)
        self.assertEqual(c["funciones"], 25)
        self.assertEqual(c["cadenas_muertas"], 0)
        self.assertEqual(c["pares_pic_verificados"], 52)
        self.assertEqual(c["pares_pic_sin_reuso_de_registro"], 52)

    def test_json_function_starts_contain_known_functions(self):
        got = {f["func"] for f in self.data["funciones"]}
        for addr in (0x435abf7a, 0x435acdd0, 0x435acf00, 0x435ad680,
                     0x435ade38, 0x435adffc, 0x435ae328):
            self.assertIn(addr, got, hex(addr))

    def test_json_differential(self):
        d = self.data["diferencial"]
        self.assertEqual(d["A6000_fw321"]["tokens"]["[ILLUMI]"], 34)
        self.assertNotIn("[ILLUMI]", d["A7S_fw320"]["tokens"])
        self.assertNotIn("[ILLUMI]", d["A6300_fw201"]["tokens"])


if __name__ == "__main__":
    unittest.main()
