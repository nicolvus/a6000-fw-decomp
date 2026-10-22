"""S156 — tests del módulo `[TP_R]` (18 trazas) de la A6000 fw3.21.

Todos los tests leen **bytes reales** de los tres `av-cam.bin` y comprueban
direcciones exactas: si una dirección o un texto cambia, el test falla.

Regla de referencias: estricta (canónica del repo,
`analysis/s106_imaging_cap/scan_pic_refs_strict.py`): cada `add rX,pc` se empareja
con el `ldr rX,[pc,#imm]` más cercano por detrás del mismo registro.
"""
import bisect
import json
import struct
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "analysis" / "s156_tp_r"))

from diffscan import BASE, FILES, Img  # noqa: E402

U16 = struct.Struct("<H").unpack_from
U32 = struct.Struct("<I").unpack_from

# --------------------------------------------------------------- expectativas
# Las 18 cadenas con el token [TP_R] de la A6000 fw3.21: (addr, texto, [sitios PIC])
TP_R_STRINGS = [
    (0x43c80f23, "[TP_R]: ERR. osal_try_valloc_msg. err=0x%x, L=%d",
     ["0x4366c3b0", "0x4366c5a0", "0x4366c65c"]),
    (0x43c80f54, "[TP_R]: ERR. osal_snd_msg. err=0x%x, L=%d",
     ["0x4366c3e2", "0x4366c5f4", "0x4366c698"]),
    (0x43c80f7e, "[TP_R]: debug_num=0x%02x", []),
    (0x43c80faf, "[TP_R]: ERR. osal_free_msg. err=0x%x, L=%d",
     ["0x4366c6cc", "0x4366c8bc"]),
    (0x43c80fda, "[TP_R]: boot_exit_tp come", ["0x4366c704"]),
    (0x43c80ff4, "[TP_R]: ERR. osal_unreg_msg_queue_cb. err=0x%x, L=%d",
     ["0x4366c7ba"]),
    (0x43c81029, "[TP_R]: ERR. osal_free_timer. err=0x%x, L=%d", ["0x4366c802"]),
    (0x43c81056, "[TP_R]: ERR. osal_rcv_msg. err=0x%x, L=%d", ["0x4366c88a"]),
    (0x43c81080, "[TP_R]: ERR. osal_set_timer. err=%x, L=%d", ["0x4366ca22"]),
    (0x43c810aa, "[TP_R]: ERR. unkown tp_type. tp_type=0x%x, L=%d", ["0x4366ca50"]),
    (0x43c810da, "[TP_R]: ERR. unknown cmd. cmd=0x%x, L=%d", ["0x4366cad2"]),
    (0x43c81103, "[TP_R]: ERR. osal_valloc_msg. err=0x%x, L=%d", []),
    (0x43c81130,
     "[TP_R]: <Water> key_code=0x%08x, xy=0x%08x, status=0x%08x, "
     "ex_status=0x%08x, ex_info=0x%08x", []),
    (0x43c811dd,
     "[TP_R]: key_code=0x%08x, xy=0x%08x, status=0x%08x, "
     "ex_status=0x%08x, ex_info=0x%08x", []),
    (0x43c8127d, "[TP_R]: boot_init_tp come", ["0x4366cb14"]),
    (0x43c81297, "[TP_R]: ERR. read size error. size=0x%x, L=%d",
     ["0x4366cb56", "0x4366cc9e"]),
    (0x43c812c5, "[TP_R]: ERR. osal_alloc_timer. err=0x%x, L=%d", ["0x4366cc1c"]),
    (0x43c812f3, "[TP_R]: ERR. osal_reg_sync_msg_queue_cb. err=0x%x, L=%d",
     ["0x4366cc56"]),
]

# Las 3 cadenas con la etiqueta antigua [TP R] (también muertas)
TP_R_OLD = [
    (0x43c80f97, "[TP R] debug_num = %02x"),
    (0x43c8118c,
     "[TP R] <Water> key_code=%08x, xy=%08x, status=%08x, "
     "ex_status=%08x, ex_info=%08x"),
    (0x43c81231,
     "[TP R] key_code=%08x, xy=%08x, status=%08x, ex_status=%08x, ex_info=%08x"),
]

# función → trazas (mapa del informe)
FUNC_MAP = {
    "0x4366c388": ["0x43c80f23", "0x43c80f54"],
    "0x4366c568": ["0x43c80f23", "0x43c80f54"],
    "0x4366c624": ["0x43c80f23", "0x43c80f54", "0x43c80faf"],
    "0x4366c6e8": ["0x43c80fda", "0x43c80ff4", "0x43c81029"],
    "0x4366c840": ["0x43c80faf", "0x43c81056"],
    "0x4366c978": ["0x43c81080", "0x43c810aa"],
    "0x4366ca92": ["0x43c810da"],
    "0x4366caf4": ["0x43c8127d", "0x43c81297", "0x43c812c5", "0x43c812f3"],
}

MODULE_LO, MODULE_HI = 0x4366c200, 0x4366cd60

# GID de las colas OSAL (pool literal -> valor)
GIDS = {
    0x4366c384: 0x008F0139,   # cola de log del firmware (reporter 0x4366c300)
    0x4366c3f8: 0x005C011C,   # cola de eventos del módulo TP
    0x4366c8e0: 0x01010227,   # cola de control del módulo TP (osal_rcv_msg)
    0x4366ccdc: 0x00910040,   # cola usada en boot_init_tp
}

# tabla de comandos de depuración del módulo TP
TP_CMD_TABLE = 0x43FE3F28
TP_CMD_TABLE_WORDS = [
    "start", "start", "handler",
    "set_mode", "Set TP Mode", "handler",
    "print_xy", "print_xy", "handler",
    "dds_on", "DDS On", "handler",
    "dds_off", "DDS Off", "handler",
    None,
]


def strict_map(img, lo, hi):
    """Mapa destino → [add_addr] con la regla estricta canónica."""
    ldrs = img.ldr_sites(lo, hi)
    adds = img.add_sites(lo, hi)
    by_reg = {}
    for a, reg, w, lit in ldrs:
        by_reg.setdefault(reg, []).append((a, w))
    for v in by_reg.values():
        v.sort()
    keys = {r: [x[0] for x in v] for r, v in by_reg.items()}
    out = {}
    for a, reg in adds:
        v = by_reg.get(reg)
        if not v:
            continue
        ks = keys[reg]
        i = bisect.bisect_left(ks, a) - 1
        if i < 0:
            continue
        la, w = v[i]
        if a - la > 4096:
            continue
        out.setdefault((w + (a + 4)) & 0xFFFFFFFF, []).append(a)
    return {k: sorted(set(v)) for k, v in out.items()}


class TpR(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.a6 = Img(FILES["A6000"])
        cls.module_map = strict_map(cls.a6, MODULE_LO, MODULE_HI)
        cls.global_map = strict_map(cls.a6, BASE, BASE + cls.a6.N)
        cls.json = json.loads((ROOT / "analysis/s156_tp_r/tp_r.json").read_text())

    # ------------------------------------------------------------- cadenas
    def test_las_18_cadenas_TP_R_estan_en_su_direccion_exacta(self):
        self.assertEqual(len(TP_R_STRINGS), 18)
        for addr, text, _ in TP_R_STRINGS:
            self.assertEqual(self.a6.cstr(addr), text, f"cadena en {addr:#x}")

    def test_las_3_cadenas_TP_R_antiguas(self):
        for addr, text in TP_R_OLD:
            self.assertEqual(self.a6.cstr(addr), text, f"cadena en {addr:#x}")

    def test_solo_21_cadenas_con_el_token_TP(self):
        got = [a for a, s in self.a6.strings()
               if "[TP_R]" in s or "[TP R]" in s]
        self.assertEqual(len(got), 21)
        self.assertEqual(sorted(got),
                         sorted([a for a, _, _ in TP_R_STRINGS]
                                + [a for a, _ in TP_R_OLD]))

    # ------------------------------------------------------- referencias
    def test_sitios_pic_de_cada_traza_viva(self):
        for addr, text, sites in TP_R_STRINGS:
            got = [f"0x{a:x}" for a in self.module_map.get(addr, [])]
            self.assertEqual(got, sites, f"referencias de {text!r}")

    def test_las_7_cadenas_muertas_no_tienen_referencia_ni_puntero(self):
        for addr, text, sites in TP_R_STRINGS:
            if sites:
                continue
            self.assertEqual(self.global_map.get(addr, []), [],
                             f"{text!r} tiene referencia")
            self.assertEqual(self.a6.abs_ptrs(addr), [],
                             f"{text!r} tiene puntero absoluto")
        for addr, text in TP_R_OLD:
            self.assertEqual(self.global_map.get(addr, []), [],
                             f"{text!r} tiene referencia")
            self.assertEqual(self.a6.abs_ptrs(addr), [],
                             f"{text!r} tiene puntero absoluto")

    def test_mapa_funcion_traza(self):
        got = {}
        for addr, text, sites in TP_R_STRINGS:
            for site in sites:
                fs = self.a6.func_start(int(site, 16))
                got.setdefault(f"0x{fs:x}", set()).add(addr)
        self.assertEqual({k: sorted(f"0x{x:x}" for x in v)
                          for k, v in got.items()},
                         {k: sorted(v) for k, v in FUNC_MAP.items()})

    def test_los_sitios_de_referencia_son_adder_pc(self):
        """Cada sitio es un `add rX,pc` de 16 bits (bytes 0x44xx con Rm=PC)."""
        for addr, text, sites in TP_R_STRINGS:
            for site in sites:
                a = int(site, 16)
                h = U16(self.a6.B, a - BASE)[0]
                self.assertEqual(h & 0xFF00, 0x4400, f"{site} no es add rX,pc")
                self.assertEqual((h >> 3) & 0xF, 15, f"{site} no usa PC")

    # ----------------------------------------------------------- reporter
    def test_reporter_0x4366c300_es_miembro_de_la_familia_s151(self):
        b = self.a6.B
        # push {r3} ; movs r3,#0 ; ... ; movs r2,#0x9a
        self.assertEqual(b[0x4366c300 - BASE:0x4366c302 - BASE], b"\x08\xb4")
        self.assertEqual(b[0x4366c302 - BASE:0x4366c304 - BASE], b"\x00\x23")
        self.assertEqual(b[0x4366c318 - BASE:0x4366c31a - BASE], b"\x9a\x22")
        # llamadas: osal_try_valloc_msg / vsnprintf / osal_snd_msg
        for site, target in ((0x4366c31c, 0x435612d0),
                             (0x4366c346, 0x439c5004),
                             (0x4366c376, 0x4356120c)):
            h1 = U16(b, site - BASE)[0]
            h2 = U16(b, site - BASE + 2)[0]
            self.assertEqual((h1 & 0xF800), 0xF000, f"{site:#x} no es BL")
            self.assertEqual((h2 & 0xD000), 0xD000, f"{site:#x} no es BL")
            s = (h1 >> 10) & 1
            i1 = (h2 >> 13) & 1
            i2 = (h2 >> 11) & 1
            j1 = (~(i1 ^ s)) & 1
            j2 = (~(i2 ^ s)) & 1
            imm = ((s << 24) | (j1 << 23) | (j2 << 22)
                   | ((h1 & 0x3FF) << 12) | ((h2 & 0x7FF) << 1))
            if s:
                imm -= 1 << 25
            self.assertEqual((site + 4 + imm) & 0xFFFFFFFF, target,
                             f"BL en {site:#x}")

    def test_gid_de_log_del_firmware(self):
        for pool, value in GIDS.items():
            self.assertEqual(U32(self.a6.B, pool - BASE)[0], value,
                             f"GID en {pool:#x}")

    def test_contadores_de_la_familia_de_loggers(self):
        def fam(B, estricto):
            n = len(B)
            out = []
            for a in range(0, n - 8, 2):
                if B[a] != 0x08 or B[a + 1] != 0xB4:
                    continue
                if estricto:
                    if B[a + 2] == 0x9A and B[a + 3] == 0x22:
                        out.append(BASE + a)
                else:
                    for k in range(a + 4, min(a + 40, n - 2), 2):
                        if B[k] == 0x9A and B[k + 1] == 0x22:
                            out.append(BASE + a)
                            break
            return out

        for which, est, lax in (("A6000", 43, 561), ("A7S", 0, 0),
                                 ("A6300", 0, 2)):
            B = open(FILES[which], "rb").read()
            self.assertEqual(len(fam(B, True)), est, f"{which} estricta")
            self.assertEqual(len(fam(B, False)), lax, f"{which} laxa")
        # el reporter del TP está en la familia laxa, no en la estricta
        B = self.a6.B
        self.assertIn(0x4366c300, fam(B, False))
        self.assertNotIn(0x4366c300, fam(B, True))

    # ------------------------------------------------- tabla de comandos DDL
    def test_tabla_de_comandos_del_modulo_tp(self):
        b = self.a6.B
        for i, expect in enumerate(TP_CMD_TABLE_WORDS):
            w = U32(b, TP_CMD_TABLE + 4 * i - BASE)[0]
            if expect is None:
                self.assertEqual(w, 0, f"terminador en +{4 * i}")
            elif expect == "handler":
                self.assertTrue(0x43541000 <= w < 0x44017000,
                                f"handler fuera de código en +{4 * i}: {w:#x}")
            else:
                self.assertEqual(self.a6.cstr(w), expect,
                                 f"entrada +{4 * i} del módulo TP")

    def test_registro_del_nombre_tp(self):
        # ldr r0,[pc,#8] -> "tp" ; ldr r1,[pc,#0xc] -> tabla ; add rX,pc
        self.assertEqual(self.a6.cstr(0x43c8127a), "tp")
        for add, reg, expect in ((0x4366cae4, 0, 0x43c8127a),
                                 (0x4366cae6, 1, 0x43fe3f28)):
            h = U16(self.a6.B, add - BASE)[0]
            self.assertEqual(h & 0xFF00, 0x4400)
            self.assertEqual(((h >> 7) & 1) << 3 | (h & 7), reg,
                             f"registro del add en {add:#x}")
            lit = None
            a = add - 2
            while a > add - 16:
                hh = U16(self.a6.B, a - BASE)[0]
                if (hh & 0xF800) == 0x4800 and ((hh >> 8) & 7) == reg:
                    lit = ((a + 4) & ~3) + ((hh & 0xFF) * 4)
                    break
                a -= 2
            self.assertIsNotNone(lit)
            w = U32(self.a6.B, lit - BASE)[0]
            self.assertEqual((w + add + 4) & 0xFFFFFFFF, expect,
                             f"add en {add:#x}")

    # ------------------------------------------------------------- arranque
    def test_ids_de_arranque_y_parada(self):
        b = self.a6.B
        # init: movw r3,#0x118 ; subs r3,#0x91  -> 135
        self.assertEqual(b[0x43a464d6 - BASE:0x43a464d8 - BASE], b"\x91\x3b")
        self.assertEqual(0x118 - 0x91, 135)
        # exit: subs r3,#0x92 -> 134
        self.assertEqual(b[0x43a46706 - BASE:0x43a46708 - BASE], b"\x92\x3b")
        self.assertEqual(0x118 - 0x92, 134)

    # ------------------------------------------------------------ diferencial
    def test_a7s_tiene_3_cadenas_TP_R_antiguas_muertas(self):
        img = Img(FILES["A7S"])
        for addr, text in ((0x43c838e4, "[TP R] debug_num = %02x"),
                           (0x43c838fc,
                            "[TP R] <Water> key_code=%08x, xy=%08x, status=%08x, "
                            "ex_status=%08x, ex_info=%08x"),
                           (0x43c8394d,
                            "[TP R] key_code=%08x, xy=%08x, status=%08x, "
                            "ex_status=%08x, ex_info=%08x")):
            self.assertEqual(img.cstr(addr), text, f"cadena en {addr:#x}")
            self.assertEqual(img.abs_ptrs(addr), [])
        smap = strict_map(img, BASE, BASE + img.N)
        for addr in (0x43c838e4, 0x43c838fc, 0x43c8394d):
            self.assertEqual(smap.get(addr, []), [],
                             f"la A7S referencia {addr:#x}")

    def test_a6300_tiene_4_cadenas_TP_R_antiguas_muertas(self):
        img = Img(FILES["A6300"])
        for addr, text in ((0x43d8337f, "[TP R] debug_num = %02x"),
                           (0x43d83397,
                            "[TP R] <Water> key_code=%08x, xy=%08x, status=%08x, "
                            "ex_status=%08x, ex_info=%08x"),
                           (0x43d833e8,
                            "[TP R] key_code=%08x, xy=%08x, status=%08x, "
                            "ex_info=%08x"),
                           (0x43d83421,
                            "[TP R] key_code=%08x, xy=%08x, status=%08x, "
                            "ex_status=%08x, ex_info=%08x")):
            self.assertEqual(img.cstr(addr), text, f"cadena en {addr:#x}")
            self.assertEqual(img.abs_ptrs(addr), [])

    def test_modulo_DMMYSIOCOM_presente_en_los_tres_firmwares(self):
        esperados = {
            "A6000": (0x43c72e7d, 0x43c72eab),
            "A7S": (0x43c73764, 0x43c73792),
            "A6300": (0x43d7296b, 0x43d72999),
        }
        for which, (a1, a2) in esperados.items():
            img = Img(FILES[which])
            self.assertEqual(img.cstr(a1),
                             "[DMMYSIOCOM]ERR. osal_snd_msg. err=0x%x, L=%d")
            self.assertEqual(img.cstr(a2),
                             "[DMMYSIOCOM]ERR. osal_free_msg. err=0x%x, L=%d")
            n = sum(1 for _, s in img.strings() if "DMMYSIOCOM" in s)
            self.assertEqual(n, 2, f"{which} número de cadenas DMMYSIOCOM")

    def test_DMMYSIOCOM_no_es_el_mismo_codigo_que_TP_R(self):
        """Las 2 trazas [DMMYSIOCOM] se emiten desde otra zona de código."""
        smap = strict_map(self.a6, BASE, BASE + self.a6.N)
        sites = smap[0x43c72e7d] + smap[0x43c72eab]
        self.assertEqual(sorted(f"0x{s:x}" for s in sites),
                         ["0x43628a5e", "0x43628a80"])
        for s in sites:
            self.assertFalse(MODULE_LO <= s < MODULE_HI,
                             "DMMYSIOCOM no debe vivir en el módulo TP")
            self.assertNotEqual(self.a6.func_start(s),
                                0x4366c388)   # mini-reporter del módulo TP

    # ------------------------------------------------- ruido / obturador
    def test_ninguna_traza_habla_de_obturador_ni_de_sensor(self):
        banned = ("shut", "silent", "electro", "mech", "sensor", "exposure",
                  "readout", "imager", "bracket", "sweep", "curtain",
                  "fps", "jpeg", "movie")
        for addr, text, _ in TP_R_STRINGS:
            low = text.lower()
            for w in banned:
                self.assertNotIn(w, low, f"{text!r} contiene {w!r}")

    # ------------------------------------------------------------- json
    def test_json_consistente_con_los_bytes(self):
        j = self.json
        self.assertEqual(j["hito"], "S156")
        self.assertEqual(j["contadores"]["n_cadenas_TP_R"], 18)
        self.assertEqual(j["contadores"]["n_cadenas_TP_espacio"], 3)
        self.assertEqual(j["contadores"]["n_cadenas_totales"], 21)
        self.assertEqual(j["contadores"]["n_vivas"], 14)
        self.assertEqual(j["contadores"]["n_muertas"], 7)
        self.assertEqual(j["contadores"]["n_sitios_pic"], 20)
        self.assertEqual(j["contadores"]["n_funciones"], 8)
        self.assertEqual(j["colas_osal_gid"]["cola_de_log_del_firmware_0x4366c300"],
                         "0x008f0139")
        self.assertEqual(j["diferencial"]["A7S"]["n_cadenas"], 3)
        self.assertEqual(j["diferencial"]["A6300"]["n_cadenas"], 4)


if __name__ == "__main__":
    unittest.main()
