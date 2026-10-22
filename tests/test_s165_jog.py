"""S165 — tests del módulo [JOG] contra los BYTES REALES del firmware.

Cada test comprueba direcciones concretas: si una dirección cambia en el firmware
(o en el mapa de referencias), el test falla.
"""
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
JOG_JSON = ROOT / "analysis/s165_jog/jog.json"

B = BIN.read_bytes()
A7 = A7S.read_bytes()
A63 = A6300.read_bytes()


def u16(a):
    return struct.unpack_from("<H", B, a - BASE)[0]


def u32(a):
    return struct.unpack_from("<I", B, a - BASE)[0]


def cstr(a, blob=None):
    blob = B if blob is None else blob
    o = a - BASE
    e = blob.find(b"\x00", o)
    return blob[o:e].decode("ascii", "replace")


# Las 14 trazas [JOG]: (vaddr, texto)
JOG_STRINGS = [
    (0x43c40eb4, "[JOG]JogMain::%s:%d"),
    (0x43c40ef2, "[JOG]ERR. osal_try_valloc_msg. err=0x%x, line=%d"),
    (0x43c40f23, "[JOG]<Send Event> key_code = 0x%x, deg/sec = %d"),
    (0x43c40f53, "[JOG]ERR. osal_snd_msg. err=0x%x, line=%d"),
    (0x43c40f85, "[JOG]ERR. osal_free_timer. err=0x%x, line=%d"),
    (0x43c40fb2, "[JOG]JogFg::%s:%d"),
    (0x43c40fc4, "[JOG]ERR. osal_alloc_timer. err=0x%x, line=%d"),
    (0x43c40ff2, "[JOG]ERR. osal_set_timer. err=0x%x, line=%d"),
    (0x43c410a2, "[JOG]JogTpu::%s:%d"),
    (0x43c410fe, "[JOG]JogVGrip::%s:%d"),
    (0x43c41113, "[JOG]UpdateDataFromVgrip SndErr, line=%d"),
    (0x43c41184, "[JOG]JogKey::%s:%d:0x%x,%d"),
    (0x43c4119f, "[JOG]JogKey::%s:%d,pos:%d->%d"),
    (0x43c411bd, "[JOG]JogKey::%s:%d,Deg=0,Not Send"),
]

# Los 24 sitios que referencian una traza [JOG] (regla PIC estricta), verificados a mano.
JOG_SITES = {
    0x435ae5d4: 0x43c40eb4,
    0x435ae6ce: 0x43c40eb4,
    0x435aeb42: 0x43c40ef2,
    0x435aeb74: 0x43c40f23,
    0x435aebb4: 0x43c40f53,
    0x435aeda6: 0x43c40f85,
    0x435aee00: 0x43c40fb2,
    0x435aeeac: 0x43c40fc4,
    0x435aeee6: 0x43c40ff2,
    0x435aef18: 0x43c40fb2,
    0x435af1da: 0x43c40f85,
    0x435af234: 0x43c410a2,
    0x435af2e0: 0x43c40fc4,
    0x435af31a: 0x43c40ff2,
    0x435af34c: 0x43c410a2,
    0x435af5f6: 0x43c40f85,
    0x435af650: 0x43c410fe,
    0x435af6fc: 0x43c40fc4,
    0x435af736: 0x43c40ff2,
    0x435af768: 0x43c410fe,
    0x435af890: 0x43c41113,
    0x435af990: 0x43c41184,
    0x435afa0c: 0x43c4119f,
    0x435afa66: 0x43c411bd,
}

# 10 sitios que referencian cadenas __PRETTY_FUNCTION__ del módulo.
PRETTY_SITES = {
    0x435ae5c2: 0x43c40ec8,   # 'void JogMain::Exit()'
    0x435ae6ba: 0x43c40edd,   # 'void JogMain::Init()'
    0x435aedf2: 0x43c4101e,   # virtual void JogFg::Start(...)
    0x435aef0e: 0x43c4101e,
    0x435af226: 0x43c41063,   # virtual void JogTpu::Start(...)
    0x435af342: 0x43c41063,
    0x435af642: 0x43c410bd,   # virtual void JogVGrip::Start(...)
    0x435af75e: 0x43c410bd,
    0x435af978: 0x43c411df,   # void JogKey::SetDev(JogDev*, ...)
    0x435afa0e: 0x43c41146,   # bool JogKey::SendKeyEvent(...)
}


def pic_dest(site, reg=None):
    """Reproduce la regla estricta: `add rX,pc` + `ldr rX,[pc,#imm]` más cercano."""
    h = u16(site)
    assert (h & 0xFF00) == 0x4400, f"{site:#x} no es 'add rX,pc'"
    assert ((h >> 3) & 0xF) == 15, f"{site:#x} no usa PC"
    r = reg if reg is not None else (((h >> 7) & 1) << 3) | (h & 7)
    # buscar el ldr del mismo registro más cercano hacia atrás (ventana 4 KB)
    a = site - 2
    while a > site - 4096:
        lh = u16(a)
        if (lh & 0xF800) == 0x4800 and ((lh >> 8) & 7) == r:
            lit = ((a + 4) & ~3) + (lh & 0xFF) * 4
            return (u32(lit) + site + 4) & 0xFFFFFFFF
        a -= 2
    raise AssertionError(f"sin ldr previo para r{r} en {site:#x}")


class TestJogStrings(unittest.TestCase):
    def test_the_14_strings_are_at_their_exact_address(self):
        self.assertEqual(len(JOG_STRINGS), 14)
        for addr, text in JOG_STRINGS:
            self.assertEqual(cstr(addr), text, f"cadena distinta en {addr:#x}")

    def test_token_occurs_exactly_14_times_in_a6000(self):
        self.assertEqual(B.count(b"[JOG]"), 14)

    def test_token_absent_in_a7s_and_a6300(self):
        self.assertEqual(A7.count(b"[JOG]"), 0)
        self.assertEqual(A63.count(b"[JOG]"), 0)

    def test_jog_strings_absent_in_a7s_and_a6300(self):
        for _, text in JOG_STRINGS:
            self.assertNotIn(text.encode(), A7)
            self.assertNotIn(text.encode(), A63)

    def test_rtti_class_names_exist_only_as_expected(self):
        # A6000 y A7S: JogDev/JogFg/JogTpu/JogVGrip ; A6300: JogDev/JogCaif/JogFg/JogTpu
        for blob, classes in ((B, [b"6JogDev", b"5JogFg", b"6JogTpu", b"8JogVGrip"]),
                               (A7, [b"6JogDev", b"5JogFg", b"6JogTpu", b"8JogVGrip"]),
                               (A63, [b"6JogDev", b"7JogCaif", b"5JogFg", b"6JogTpu"])):
            for c in classes:
                self.assertIn(c, blob, f"falta {c!r}")
        self.assertNotIn(b"8JogVGrip", A63)
        self.assertNotIn(b"7JogCaif", B)
        self.assertNotIn(b"7JogCaif", A7)
        # la cadena de texto 'JogKey' solo aparece en la A6000
        self.assertIn(b"JogKey", B)
        self.assertNotIn(b"JogKey", A7)
        self.assertNotIn(b"JogKey", A63)


class TestPicReferences(unittest.TestCase):
    def test_24_sites_resolve_to_their_jog_string(self):
        self.assertEqual(len(JOG_SITES), 24)
        for site, dest in JOG_SITES.items():
            self.assertEqual(pic_dest(site), dest, f"sitio {site:#x}")

    def test_10_pretty_function_sites_resolve(self):
        self.assertEqual(len(PRETTY_SITES), 10)
        for site, dest in PRETTY_SITES.items():
            self.assertEqual(pic_dest(site), dest, f"sitio {site:#x}")

    def test_site_instructions_are_the_expected_encodings(self):
        # 'add r3,pc' = 0x447b ; 'add r6,pc' = 0x447e
        for site in JOG_SITES:
            h = u16(site)
            self.assertEqual((h & 0xFF00, (h >> 3) & 0xF), (0x4400, 15),
                             f"{site:#x} no es add rX,pc")
        self.assertEqual(u16(0x435afa0e), 0x447e)   # add r6,pc
        self.assertEqual(u16(0x435aeb74), 0x447b)   # add r3,pc

    def test_all_sites_fall_in_the_expected_functions(self):
        bounds = [(0x435ae5bc, 0x435ae616), (0x435ae6b6, 0x435ae846),
                  (0x435aeb18, 0x435aebd2), (0x435aed30, 0x435aedc6),
                  (0x435aedd0, 0x435aef24), (0x435af166, 0x435af1fa),
                  (0x435af204, 0x435af358), (0x435af582, 0x435af616),
                  (0x435af620, 0x435af774), (0x435af848, 0x435af8b2),
                  (0x435af968, 0x435af9ae), (0x435af9d0, 0x435afa76)]
        for site in JOG_SITES:
            self.assertTrue(any(lo <= site < hi for lo, hi in bounds),
                            f"sitio {site:#x} fuera de las 12 funciones")

    def test_function_prologues(self):
        # push {r0,r1,r4,lr} = 0xb513 ; push.w {r0,...,lr} = 0xe92d
        self.assertEqual(u16(0x435ae5c0), 0xB513)
        self.assertEqual(u32(0x435ae6b6), 0x43F7E92D)   # push.w {r0,r1,r2,r4..r8,sb,lr}
        self.assertEqual(u32(0x435aeb18), 0x41FFE92D)
        self.assertEqual(u32(0x435af9d0), 0x43F0E92D)


class TestRtti(unittest.TestCase):
    def test_typeinfo_names_and_bases(self):
        self.assertEqual(cstr(u32(0x43fdaaf8)), "6JogDev")       # JogDev.typeinfo @0x43fdaaf4
        self.assertEqual(cstr(u32(0x43fdab00)), "5JogFg")        # JogFg.typeinfo  @0x43fdaafc
        self.assertEqual(cstr(u32(0x43fdab0c)), "6JogTpu")       # JogTpu.typeinfo @0x43fdab08
        self.assertEqual(cstr(u32(0x43fdab18)), "8JogVGrip")     # JogVGrip.typeinfo @0x43fdab14
        self.assertEqual(u32(0x43fdab04), 0x43fdaaf4)            # JogFg.base  == JogDev
        self.assertEqual(u32(0x43fdab10), 0x43fdaaf4)            # JogTpu.base == JogDev
        self.assertEqual(u32(0x43fdab1c), 0x43fdaaf4)            # JogVGrip.base == JogDev

    def test_jogdev_is_abstract(self):
        for i in range(6):
            self.assertEqual(u32(0x43fbb640 + 4 * i), 0x439B4145,
                             "ranura %d de JogDev" % i)

    def test_pure_virtual_stub_message(self):
        # 0x439b4144 = __cxa_pure_virtual -> 'pure virtual method called\n'
        self.assertEqual(cstr(0x43BD4DE4), "pure virtual method called\n")

    def test_vtable_slots(self):
        self.assertEqual(u32(0x43fbb65c), 0x43fdaafc)   # typeinfo JogFg en su vtable
        self.assertEqual(u32(0x43fbb664), 0x435AEDD1)   # JogFg::Start
        self.assertEqual(u32(0x43fbb668), 0x435AED31)   # JogFg slot2
        self.assertEqual(u32(0x43fbb67c), 0x43fdab08)   # typeinfo JogTpu
        self.assertEqual(u32(0x43fbb684), 0x435AF205)   # JogTpu::Start
        self.assertEqual(u32(0x43fbb69c), 0x43fdab14)   # typeinfo JogVGrip
        self.assertEqual(u32(0x43fbb6a4), 0x435AF621)   # JogVGrip::Start

    def test_start_overrides_reference_their_pretty_function(self):
        for site, dest in ((0x435aedf2, 0x43c4101e), (0x435af226, 0x43c41063),
                           (0x435af642, 0x43c410bd)):
            self.assertEqual(pic_dest(site), dest)


class TestKeyCodeTable(unittest.TestCase):
    def test_table_contents(self):
        self.assertEqual([u32(0x43fdab20 + 4 * i) for i in range(6)],
                         [0x11, 0x12, 0x16, 0x17, 0x14, 0x15])

    def test_table_is_unique_in_the_image(self):
        pat = struct.pack("<6I", 0x11, 0x12, 0x16, 0x17, 0x14, 0x15)
        self.assertEqual(B.count(pat), 1)

    def test_got_resolves_to_the_table(self):
        # 0x435af9b8: ldr r3,[pc,#0xc] ; ldr r2,[pc,#0x10] ; add r3,pc ; ldr r3,[r3,r2]
        w1 = u32(0x435af9c8)
        w2 = u32(0x435af9cc)
        got = (w1 + 0x435af9c0) & 0xFFFFFFFF
        self.assertEqual(got, 0x4401EEE4)
        self.assertEqual(u32(got + w2), 0x43FDAB20)

    def test_index_byte_is_read_from_the_jogkey_object(self):
        # 0x435af9c0: ldr r2,[r0,#0xc] ; 0x435af9c2: ldr.w r0,[r3,r2,lsl #2]
        self.assertEqual(u16(0x435af9c0), 0x68C2)   # ldr r2,[r0,#0xc]
        self.assertEqual(u16(0x435af9c2), 0xF853)


class TestModuleId(unittest.TestCase):
    def test_module_id_0x106(self):
        # mov.w r0,#0x106 en los puntos de log/registro
        for a in (0x435ae5ce, 0x435ae6ca, 0x435aeb3e, 0x435aeb6a):
            self.assertEqual(u16(a), 0xF44F)
            self.assertEqual(u16(a + 2), 0x7083)

    def test_descriptor_id_and_type(self):
        # 0x435aea9c: mov.w r3,#0x106 ; 0x435aea9c+2 strh r3,[r5,#2]
        self.assertEqual(u16(0x435aea98), 0xF44F)
        self.assertEqual(u16(0x435aea9a), 0x7383)   # mov.w r3,#0x106
        # 0x435aea96: movs r2,#2  -> type = 2
        self.assertEqual(u16(0x435aea96), 0x2202)
        # 0x435aea84: movs r2,#0x28 -> descriptor de 40 bytes
        self.assertEqual(u16(0x435aea84), 0x2228)


class TestVgripNaming(unittest.TestCase):
    def test_vgrip_strings_and_their_absolute_pointers(self):
        self.assertEqual(cstr(0x43c8fb2f), "Vgrip_Snd")
        self.assertEqual(cstr(0x43c8fbbe), "V Grip S1")
        self.assertEqual(u32(0x43fe8174), 0x43c8fb2f)
        self.assertEqual(u32(0x43fe8228), 0x43c8fbbe)

    def test_vgrip_strings_also_in_a7s_and_a6300(self):
        self.assertIn(b"Vgrip_Snd", A7)
        self.assertIn(b"Vgrip_Snd", A63)


class TestJsonArtifact(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(JOG_JSON.read_text())

    def test_counters(self):
        c = self.data["counters"]
        self.assertEqual(c["n_jog_strings"], 14)
        self.assertEqual(c["n_ref_sites_total"], 24)
        self.assertEqual(c["n_functions_with_jog_traces"], 12)
        self.assertEqual(c["n_dead_strings"], 0)

    def test_every_string_has_at_least_one_site(self):
        for s in self.data["strings"]:
            self.assertGreaterEqual(s["ref_count"], 1, s["text"])
            for site in s["ref_sites"]:
                self.assertEqual(pic_dest(int(site, 16)), int(s["vaddr"], 16))

    def test_json_matches_the_bytes(self):
        for s in self.data["strings"]:
            self.assertEqual(cstr(int(s["vaddr"], 16)), s["text"])

    def test_differential_recorded(self):
        d = self.data["differential"]
        self.assertEqual(d["A6000_fw321"]["n_jog_token_occurrences"], 14)
        self.assertEqual(d["A7S_fw320"]["n_jog_token_occurrences"], 0)
        self.assertEqual(d["A6300_fw201"]["n_jog_token_occurrences"], 0)


if __name__ == "__main__":
    unittest.main()
