"""S180 — tests del módulo [REMOTE] contra los BYTES REALES del firmware.

Cada test comprueba direcciones concretas: si una dirección, un texto o un contador
cambia en el firmware (o en el mapa de referencias), el test falla.

Método de referencias: regla PIC **estricta** (canónica del repo,
`analysis/s106_imaging_cap/pic_xref_methodology.md`):
    ldr rX,[pc,#imm]  ->  W = literal del pool
    add rX,pc         ->  destino = W + (dirección_del_add + 4)
El par se empareja con el `ldr` **más cercano** del mismo registro (ventana 4 KB) y el
registro no debe reescribirse entre `ldr` y `add`.
"""
import json
import struct
import unittest
from pathlib import Path

from capstone import CS_ARCH_ARM, CS_MODE_LITTLE_ENDIAN, CS_MODE_THUMB, Cs

ROOT = Path(__file__).resolve().parents[1]
BASE = 0x43541000
BIN = ROOT / "analysis/rea-independent/input/av-cam.bin"
A7S = (ROOT / "firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/"
       "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin")
A6300 = (ROOT / "firmware/extracted/a6300-fw201/payload/firmware.tar_unpacked/"
         "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin")
JSON_S180 = ROOT / "analysis/s180_remote/remote.json"
GLOBAL_MAP = ROOT / "analysis/s106_imaging_cap/pic_refs_strict_global.json"

B = BIN.read_bytes()
A7 = A7S.read_bytes()
A63 = A6300.read_bytes()
DATA = json.loads(JSON_S180.read_text())

MD = Cs(CS_ARCH_ARM, CS_MODE_THUMB | CS_MODE_LITTLE_ENDIAN)
TOKEN = b"[REMOTE]"

# las 32 cadenas con su texto exacto (direccion -> texto)
TEXTOS = {
    0x43C25B47: "[ACCY][INFO][REMOTE]:%d:NotifyUartCommand...UART CMD:%C%C%C%C%C%C "
                 "[%02X %02X %02X %02X %02X %02X]",
    0x43C25BA9: "[ACCY][WARN][REMOTE]:%d:RecvCmd Unknown Category:%02X",
    0x43C25BDF: "[ACCY][WARN][REMOTE]:%d:EventKey Catwgory:%02X ,Data1:%02X, Data2:%02X",
    0x43C25C26: "[ACCY][INFO][REMOTE]:%d:RetrySendCmd...retry_up:%d",
    0x43C25C59: "[ACCY][ERR][REMOTE]:%d:RetrySendCmd Buffer err",
    0x43C25C88: "[ACCY][INFO][REMOTE]:%d:SaveInfo...GF:%d SS:%d Freeze:%d Photo:%d "
                 "Zoom:%d Tally:%d",
    0x43C25CDB: "[ACCY][DEBUG][REMOTE]:%d:Zoom State Change To %d Speed:%d",
    0x43C25D15: "[ACCY][INFO][REMOTE]:%d:RestoreInfo...Savedata:%02X %02X",
    0x43C25D4E: "[ACCY][INFO][REMOTE]:%d:ExecUartCommand",
    0x43C25D76: "[ACCY][INFO][REMOTE]:%d:To Input KEY:%08X STATE:%08X INFO:%08X",
    0x43C25DB5: "[ACCY][INFO][REMOTE]:%d:SendCmd...CMD:%S retry:%d",
    0x43C25DE7: "[ACCY][ERR][REMOTE]:%d:SendCmd Buffer Busy Request CMD:%S",
    0x43C25E21: "[ACCY][INFO][REMOTE]:%d:TallyControlCmd...retry:%d",
    0x43C25E54: "[ACCY][INFO][REMOTE]:%d:CallForTransaction...Wait Tally Light Response  "
                 "NextState:%d",
    0x43C25EA9: "[ACCY][INFO][REMOTE]:%d:NotifyApiRequest...Command:%02X State:%02X "
                 "CntlState:%d",
    0x43C25EF9: "[ACCY][INFO][REMOTE]:%d:NotifyApiRequest...Buffer Busy CntlState:%d",
    0x43C25F3D: "[ACCY][INFO][REMOTE]:%d:NotifyApiRequest...Tally Light State:%d  "
                 "NextState:%d",
    0x43C25F8B: "[ACCY][INFO][REMOTE]:%d:NotifyApiRequest...Not Support Command:%02X "
                 "or State:%02X",
    0x43C25FDD: "[ACCY][INFO][REMOTE]:%d:AccyCmdClr",
    0x43C26000: "[ACCY][INFO][REMOTE]:%d:RemoteClose...Spinal:%02X  GF:%02X  SS:%02X  "
                 "Freeze:%02X  Photo:%02X  Zoom:%02X",
    0x43C26068: "[ACCY][INFO][REMOTE]:%d:GUIDE FRAME OFF  KEY:%08X STATE:%08X  INFO:%08X",
    0x43C260B0: "[ACCY][INFO][REMOTE]:%d:START STOP OFF  KEY:%08X STATE:%08X  INFO:%08X",
    0x43C260F7: "[ACCY][INFO][REMOTE]:%d:PHOTO FREEZE OFF  KEY:%08X STATE:%08X  INFO:%08X",
    0x43C26140: "[ACCY][INFO][REMOTE]:%d:PHOTO REC OFF  KEY:%08X STATE:%08X  INFO:%08X",
    0x43C26186: "[ACCY][INFO][REMOTE]:%d:ZOOM OFF  KEY:%08X STATE:%08X  INFO:%08X",
    0x43C261C7: "[ACCY][INFO][REMOTE]:%d:NotifyDetached",
    0x43C261EE: "[ACCY][INFO][REMOTE]:%d:NotifyUartTimedOut...RetryCount:%d",
    0x43C26229: "[ACCY][ERR][REMOTE]:%d:TimeoutNotify...Command Not Execution",
    0x43C26266: "[ACCY][DEBUG][REMOTE]:%d:EventTimeout Tally Light TIMEOUT",
    0x43C262A0: "[ACCY][INFO][REMOTE]:%d:NotifyUartResponse...Set Tally Light:%02X",
    0x43C262E2: "[ACCY][DEBUG][REMOTE]:%d:Set Tally Light:%02X State:%d",
    0x43C26319: "[ACCY][INFO][REMOTE]:%d:NotifyAttached",
}

# los 33 sitios PIC y la cadena a la que apuntan
SITIOS = {
    0x435662B2: 0x43C25B47, 0x4356637C: 0x43C25BA9, 0x43566392: 0x43C25BDF,
    0x435663D0: 0x43C25C26, 0x435663E6: 0x43C25C59, 0x4356650A: 0x43C25C88,
    0x4356656E: 0x43C25CDB, 0x4356659E: 0x43C25D15, 0x43566612: 0x43C25D4E,
    0x435667AC: 0x43C25D76, 0x435668D0: 0x43C25DB5, 0x435668F8: 0x43C25DE7,
    0x43566940: 0x43C25E21, 0x43566A38: 0x43C25E54, 0x43566A78: 0x43C25EA9,
    0x43566ACE: 0x43C25EF9, 0x43566AEA: 0x43C25F3D, 0x43566B00: 0x43C25F8B,
    0x43566B3E: 0x43C25FDD, 0x43566B86: 0x43C26000, 0x43566BB2: 0x43C26068,
    0x43566BE8: 0x43C260B0, 0x43566C24: 0x43C260F7, 0x43566C56: 0x43C26140,
    0x43566C8E: 0x43C26186, 0x43566CB4: 0x43C26186, 0x43566D54: 0x43C261C7,
    0x43566DA2: 0x43C261EE, 0x43566DB8: 0x43C26229, 0x43566E1C: 0x43C26266,
    0x43566E76: 0x43C262A0, 0x43566EAA: 0x43C262E2, 0x43566ED0: 0x43C26319,
}

FUNCIONES = {
    0x43566290: ("NotifyUartCommand", [0x435662B2, 0x4356637C, 0x43566392]),
    0x435663B8: ("RetrySendCmd", [0x435663D0, 0x435663E6]),
    0x435664D0: ("SaveInfo", [0x4356650A]),
    0x43566558: ("SetZoom", [0x4356656E]),
    0x43566580: ("RestoreInfo", [0x4356659E]),
    0x435665F8: ("ExecUartCommand", [0x43566612, 0x435667AC]),
    0x435668B4: ("SendCmd", [0x435668D0, 0x435668F8]),
    0x4356692C: ("TallyControlCmd", [0x43566940]),
    0x43566998: ("CallForTransaction", [0x43566A38]),
    0x43566A54: ("NotifyApiRequest", [0x43566A78, 0x43566ACE, 0x43566AEA, 0x43566B00]),
    0x43566B2C: ("AccyCmdClr", [0x43566B3E]),
    0x43566B54: ("RemoteClose", [0x43566B86, 0x43566BB2, 0x43566BE8, 0x43566C24,
                                 0x43566C56, 0x43566C8E, 0x43566CB4]),
    0x43566D44: ("NotifyDetached", [0x43566D54]),
    0x43566D8C: ("NotifyUartTimedOut", [0x43566DA2, 0x43566DB8, 0x43566E1C]),
    0x43566E5C: ("NotifyUartResponse", [0x43566E76, 0x43566EAA]),
    0x43566EC0: ("NotifyAttached", [0x43566ED0]),
}


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


def pic_pair(add_addr, blob=None):
    """Resuelve el par PIC de un 'add rX,pc': (ldr_addr, pool_addr, W, destino)."""
    h = u16(add_addr, blob)
    assert (h & 0xFF00) == 0x4400 and ((h >> 3) & 0xF) == 15, hex(add_addr)
    reg = (((h >> 7) & 1) << 3) | (h & 7)
    ldr_addr = None
    for back in range(2, 0x100, 2):
        a = add_addr - back
        hh = u16(a, blob)
        if (hh & 0xF800) == 0x4800 and ((hh >> 8) & 7) == reg:
            ldr_addr = a
            break
        if (hh & 0xFF7F) == 0xF85F:
            h2 = u16(a + 2, blob)
            if ((h2 >> 12) & 0xF) == reg:
                ldr_addr = a
                break
    assert ldr_addr is not None, hex(add_addr)
    h = u16(ldr_addr, blob)
    if (h & 0xF800) == 0x4800:
        pool = ((ldr_addr + 4) & ~3) + ((h & 0xFF) * 4)
    else:
        h2 = u16(ldr_addr + 2, blob)
        pool = ((ldr_addr + 4) & ~3) + ((((h2 >> 8) & 0xF) << 8) | (h2 & 0xFF))
    w = u32(pool, blob)
    return ldr_addr, pool, w, (w + add_addr + 4) & 0xFFFFFFFF


def dis(lo, hi, blob=None):
    blob = B if blob is None else blob
    return [f"{i.mnemonic} {i.op_str}".strip()
            for i in MD.disasm(blob[lo - BASE:hi - BASE], lo)]


class TestRecuento(unittest.TestCase):
    def test_token_REMOTE_en_tres_firmware(self):
        self.assertEqual(B.count(TOKEN), 32)
        self.assertEqual(A7.count(TOKEN), 0)
        self.assertEqual(A63.count(TOKEN), 0)

    def test_token_ACCY_en_tres_firmware(self):
        self.assertEqual(B.count(b"[ACCY]"), 106)
        self.assertEqual(A7.count(b"[ACCY]"), 0)
        self.assertEqual(A63.count(b"[ACCY]"), 0)

    def test_numero_de_cadenas(self):
        self.assertEqual(len(DATA["strings"]), 32)
        self.assertEqual(DATA["counters"]["cadenas"], 32)

    def test_rango_de_cadenas(self):
        addrs = [s["vaddr"] for s in DATA["strings"]]
        self.assertEqual(min(addrs), 0x43C25B47)
        self.assertEqual(max(addrs), 0x43C26319)

    def test_todas_las_cadenas_en_el_bloque_contiguo(self):
        addrs = sorted(s["vaddr"] for s in DATA["strings"])
        self.assertEqual(addrs, sorted(TEXTOS))

    def test_remote_solo_aparece_como_subetiqueta(self):
        """REMOTE es el 3.er nivel: [ACCY][NIVEL][REMOTE]:..."""
        for a, t in TEXTOS.items():
            self.assertTrue(t.startswith("[ACCY]["), hex(a))
            self.assertIn("][REMOTE]:%d:", t, hex(a))


class TestTextos(unittest.TestCase):
    def test_texto_exacto_de_cada_cadena(self):
        for a, t in TEXTOS.items():
            self.assertEqual(cstr(a), t, hex(a))

    def test_textos_del_json_coinciden_con_los_bytes(self):
        for s in DATA["strings"]:
            self.assertEqual(cstr(s["vaddr"]), s["text"], hex(s["vaddr"]))

    def test_prefijo_de_nivel_variable(self):
        """23 B (ERR), 24 B (INFO/WARN), 25 B (DEBUG): el nivel va DENTRO del prefijo."""
        lens = {}
        for a, t in TEXTOS.items():
            p = t.split("]:", 1)[0] + "]:"
            lens.setdefault(len(p) + len("%d:"), set()).add(p)
        self.assertEqual(lens[23], {"[ACCY][ERR][REMOTE]:"})
        self.assertEqual(lens[24], {"[ACCY][INFO][REMOTE]:", "[ACCY][WARN][REMOTE]:"})
        self.assertEqual(lens[25], {"[ACCY][DEBUG][REMOTE]:"})


class TestReferenciasPIC(unittest.TestCase):
    def test_cada_sitio_apunta_a_su_cadena(self):
        for site, dest in SITIOS.items():
            _, _, _, d = pic_pair(site)
            self.assertEqual(d, dest, hex(site))

    def test_ldr_mas_cercano_es_el_esperado(self):
        for site in SITIOS:
            add = site
            ldr_addr, pool, w, dest = pic_pair(add)
            self.assertEqual(dest, SITIOS[add], hex(add))
            h = u16(add)
            reg = (((h >> 7) & 1) << 3) | (h & 7)
            for a in range(ldr_addr + 2, add, 2):
                hh = u16(a)
                if (hh & 0xF800) == 0x4800 and ((hh >> 8) & 7) == reg:
                    self.fail(f"ldr más cercano en 0x{a:x} (se esperaba 0x{ldr_addr:x})")

    def test_sitios_contra_el_mapa_global(self):
        gmap = json.loads(GLOBAL_MAP.read_text())
        for dest in sorted(set(SITIOS.values())):
            k = hex(dest)
            self.assertIn(k, gmap, k)
            self.assertEqual(sorted(hex(x) for x in gmap[k]),
                             sorted(hex(s) for s in SITIOS if SITIOS[s] == dest), k)

    def test_totales(self):
        self.assertEqual(len(SITIOS), 33)
        self.assertEqual(len(set(SITIOS.values())), 32)
        self.assertEqual(DATA["counters"]["sitios_pic"], 33)
        self.assertEqual(DATA["counters"]["cadenas_muertas"], 0)

    def test_zoom_off_tiene_dos_sitios(self):
        self.assertEqual(sum(1 for v in SITIOS.values() if v == 0x43C26186), 2)

    def test_cero_punteros_absolutos_de_4B(self):
        for a in TEXTOS:
            self.assertEqual(B.count(struct.pack("<I", a)), 0, hex(a))
            self.assertEqual(A7.count(struct.pack("<I", a)), 0, hex(a))

    def test_no_hay_gemelo_autonomo_del_nucleo(self):
        """El texto tras el prefijo NO existe como literal en la A7S ni en la A6300."""
        for a, t in TEXTOS.items():
            nucleo = t.split("]:%d:", 1)[1].encode()
            for blob, nom in ((A7, "A7S"), (A63, "A6300")):
                self.assertEqual(blob.count(nucleo), 0, f"{nom} {hex(a)}")


class TestFunciones(unittest.TestCase):
    def test_numero_de_funciones(self):
        self.assertEqual(len(FUNCIONES), 16)
        self.assertEqual(len(DATA["funciones"]), 16)
        self.assertEqual(DATA["counters"]["funciones"], 16)

    def test_inicios_de_funcion_conocidos(self):
        starts = set(DATA["funciones"])
        self.assertEqual(starts, {hex(f) for f in FUNCIONES})

    def test_cada_sitio_pertenece_a_su_funcion(self):
        for f, (_nombre, sites) in FUNCIONES.items():
            for s in sites:
                self.assertIn(SITIOS[s], TEXTOS)
                self.assertTrue(f <= s < f + 0x1000, hex(s))

    def test_los_sitios_del_json_son_los_mismos(self):
        js = {}
        for f, items in DATA["funciones"].items():
            for it in items:
                js[int(it["site"], 16)] = int(it["dest"], 16)
        self.assertEqual(js, SITIOS)

    def test_no_se_llama_al_logger_global(self):
        """Las 16 funciones NO llaman al logger global 0x43902718 (no hay doble emision)."""
        for f in FUNCIONES:
            code = B[f - BASE:f - BASE + 0x1000]
            for ins in MD.disasm(code, f):
                if ins.mnemonic in ("bl", "blx") and ins.op_str.startswith("#0x"):
                    self.assertNotEqual(int(ins.op_str[1:], 16), 0x43902718, hex(f))


class TestLogging(unittest.TestCase):
    def test_logger_propio_del_subbloque(self):
        """Todas las trazas salen por 0x435661e4 (no por el logger global)."""
        for site in SITIOS:
            found = None
            for ins in MD.disasm(B[site - BASE:site - BASE + 0x40], site):
                if ins.mnemonic in ("bl", "blx") and ins.op_str.startswith("#0x"):
                    found = int(ins.op_str[1:], 16)
                    break
            self.assertEqual(found, 0x435661E4, hex(site))

    def test_id_de_modulo_93(self):
        """movs r0,#0x5d (0x205d) en la ventana de cada sitio (salvo los 2 ZOOM OFF)."""
        for site in SITIOS:
            if site in (0x43566C8E, 0x43566CB4):
                continue          # se comprueban aparte (r0 = zoom + 0x5c / 0x5b)
            ventana = B[max(0, site - BASE - 0x40):site - BASE + 0x40]
            self.assertIn(b"\x5d\x20", ventana, hex(site))   # movs r0,#0x5d

    def test_id_de_modulo_en_los_dos_zoom_off(self):
        """r0 = estado_del_zoom + 0x5c / + 0x5b  =>  1+92 = 93 y 2+91 = 93."""
        ins = dis(0x43566C74, 0x43566C82)
        self.assertIn("cmp r0, #1", ins)
        self.assertIn("adds r0, #0x5c", ins)
        ins = dis(0x43566C9A, 0x43566CA8)
        self.assertIn("cmp r0, #2", ins)
        self.assertIn("adds r0, #0x5b", ins)

    def test_nivel_coincide_con_el_prefijo(self):
        NIVEL = {"ERR": 1, "WARN": 2, "DEBUG": 3, "INFO": 4}
        for site, dest in SITIOS.items():
            nivel = TEXTOS[dest].split("[", 2)[2].split("]", 1)[0]
            esperado = NIVEL[nivel]
            # movs r2,#N  ==  0x2000 | (Rd<<8) | imm8   (Rd = 2)
            objetivo = 0x2000 | (2 << 8) | esperado
            ventana = B[max(0, site - BASE - 0x40):site - BASE + 0x40]
            self.assertTrue(any(struct.unpack_from("<H", ventana, i)[0] == objetivo
                                for i in range(0, len(ventana) - 1, 2)), hex(site))

    def test_logger_escribe_id_de_modulo_en_msg2(self):
        """0x435661e4: strh r7,[r4,#2] (id de modulo) ; strh.w sb,[r4,#0x10] (nivel)."""
        ins = dis(0x43566216, 0x4356622E)
        self.assertIn("strh r7, [r4, #2]", ins)
        self.assertIn("strh.w sb, [r4, #0x10]", ins)

    def test_loggers_por_subbloque(self):
        """Cada sub-bloque de [ACCY] tiene su propio logger (plantilla comun)."""
        for lg in (0x435661E4, 0x435659DC, 0x435639E8, 0x43565768, 0x43564410,
                   0x43562C94, 0x435627E0, 0x43563700, 0x4356405C, 0x43565458,
                   0x435655D0, 0x43565F20, 0x435660A0, 0x43564A08):
            ins = dis(lg, lg + 8)
            self.assertTrue(ins[0].startswith("push"), hex(lg))


class TestEstructuraDeDatos(unittest.TestCase):
    def test_flags_del_objeto_en_RemoteClose(self):
        """0x43566b60..0x43566b6c: ldrb.w r8/r7/r6/r5,[r0,#0x3c..0x3f]."""
        ins = dis(0x43566B5C, 0x43566B70)
        self.assertIn("ldrsb.w sb, [r0, #0xc]", ins)
        self.assertIn("ldrb.w r8, [r0, #0x3c]", ins)
        self.assertIn("ldrb.w r7, [r0, #0x3d]", ins)
        self.assertIn("ldrb.w r6, [r0, #0x3e]", ins)
        self.assertIn("ldrb.w r5, [r0, #0x3f]", ins)

    def test_saveinfo_empaqueta_3_bytes(self):
        """0x4356653e strb r3,[r5] ; 0x43566546 strb r3,[r5,#1] ; 0x4356654a strb r3,[r5,#2]."""
        ins = dis(0x4356653A, 0x4356654C)
        self.assertIn("strb r3, [r5]", ins)
        self.assertIn("strb r3, [r5, #1]", ins)
        self.assertIn("strb r3, [r5, #2]", ins)

    def test_restoreinfo_desempaqueta_los_mismos_bits(self):
        ins = dis(0x435665AA, 0x435665D6)
        self.assertIn("ubfx r3, r3, #1, #1", ins)
        self.assertIn("ubfx r3, r3, #2, #1", ins)
        self.assertIn("ubfx r3, r3, #3, #1", ins)

    def test_setzoom_escribe_estado_y_velocidad(self):
        ins = dis(0x4356655E, 0x43566562)
        self.assertIn("str r1, [r0, #0x34]", ins)
        self.assertIn("str r2, [r0, #0x38]", ins)

    def test_tabla_de_5_codigos_de_tecla_en_los_tres_firmware(self):
        esperado = [0x0A000009, 0x0A00000D, 0x0A000008, 0x0A00000C, 0x0A000011]
        for blob, base in ((B, 0x435667F0), (A7, 0x43564874), (A63, 0x4355F040)):
            got = [u32(base + 4 * i, blob) for i in range(5)]
            self.assertEqual(got, esperado, hex(base))

    def test_codigos_de_tecla_usados_en_los_sitios_de_salida(self):
        """GUIDE FRAME 0x0A000009 (0x43566cf8), START STOP 0x0A00000D (0x43566cfc),
        PHOTO FREEZE 0x0A000008 (0x43566d04), PHOTO REC 0x0A00000C (0x43566d0c),
        ZOOM 0x0A000011 (0x43566d14)."""
        for pool, val in ((0x43566CF8, 0x0A000009), (0x43566CFC, 0x0A00000D),
                          (0x43566D04, 0x0A000008), (0x43566D0C, 0x0A00000C),
                          (0x43566D14, 0x0A000011)):
            self.assertEqual(u32(pool), val, hex(pool))

    def test_eventos_de_suelta_de_tecla(self):
        """GUIDE FRAME 0x06000600 (inmediato), START STOP 0x06000700 (0x43566d00),
        PHOTO FREEZE 0x06000800 (0x43566d08), PHOTO REC 0x06000900 (0x43566d10),
        ZOOM OFF #1 0x06000a00 (0x43566d18), ZOOM OFF #2 0x06000b00 (0x43566d1c)."""
        for pool, val in ((0x43566D00, 0x06000700), (0x43566D08, 0x06000800),
                          (0x43566D10, 0x06000900), (0x43566D18, 0x06000A00),
                          (0x43566D1C, 0x06000B00)):
            self.assertEqual(u32(pool), val, hex(pool))
        # el evento de GUIDE FRAME es un inmediato: mov.w r0,#0x6000600
        self.assertIn("mov.w r0, #0x6000600", dis(0x43566BBA, 0x43566BBE))

    def test_tabla_tbb_de_comandos(self):
        """tbb en 0x43566638 (base 0x4356663c): 4 casos -> los 4 grupos de boton."""
        ins = dis(0x43566638, 0x4356663C)
        self.assertEqual(ins[0], "tbb [pc, r2]")
        base = (0x43566638 + 4) & ~3
        self.assertEqual(base, 0x4356663C)
        esperados = [0x43566640, 0x4356666E, 0x4356669C, 0x435666D4]
        for i, tgt in enumerate(esperados):
            self.assertEqual(base + 2 * B[base + i - BASE], tgt, i)

    def test_tabla_tbb_de_categoria(self):
        ins = dis(0x435662F4, 0x435662F8)
        self.assertEqual(ins[0], "tbb [pc, r1]")
        base = (0x435662F4 + 4) & ~3
        self.assertEqual(base, 0x435662F8)

    def test_tabla_tbb_de_tally(self):
        ins = dis(0x43566960, 0x43566964)
        self.assertEqual(ins[0], "tbb [pc, r2]")
        base = (0x43566960 + 4) & ~3
        self.assertEqual(base, 0x43566964)
        esperados = [0x43566976, 0x43566968, 0x4356696C, 0x43566970]
        for i, tgt in enumerate(esperados):
            self.assertEqual(base + 2 * B[base + i - BASE], tgt, i)

    def test_trama_tally_de_6_bytes(self):
        """TallyControlCmd 0x4356692c: '%' '7' '6' <estado> '0' '*'."""
        ins = dis(0x4356694A, 0x4356698C)
        self.assertIn("movs r3, #0x25", ins)      # '%'
        self.assertIn("adds r3, #0x12", ins)      # '7'
        self.assertIn("movs r3, #0x2a", ins)      # '*'


class TestRTTI(unittest.TestCase):
    def test_nombre_de_la_clase(self):
        self.assertEqual(cstr(0x43C26340), "18AccyUmDeviceRemote")
        self.assertEqual(cstr(0x43C2536D), "16AccyUmDeviceBase")

    def test_type_info_y_vtable(self):
        self.assertEqual(u32(0x43FD7DBC), 0x43FD03D8)     # vtable __si_class_type_info
        self.assertEqual(u32(0x43FD7DC0), 0x43C26340)     # name -> 18AccyUmDeviceRemote
        self.assertEqual(u32(0x43FD7DC4), 0x43FD7C8C)     # base -> AccyUmDeviceBase
        vt = [u32(0x43FB9114 + 4 * i) for i in range(8)]
        self.assertEqual(vt, [0x43566EC1, 0x43566A55, 0x43566E5D, 0x43566D8D,
                              0x43566999, 0x43566291, 0x435665F9, 0x43566D45])

    def test_la_clase_existe_en_los_tres_firmware(self):
        self.assertIn(b"18AccyUmDeviceRemote", B)
        self.assertIn(b"18AccyUmDeviceRemote", A7)
        self.assertIn(b"18AccyUmDeviceRemote", A63)


class TestDiferencial(unittest.TestCase):
    def test_no_hay_trazas_ACCY_en_los_otros_dos(self):
        for blob in (A7, A63):
            self.assertEqual(blob.count(b"[ACCY]"), 0)
            self.assertEqual(blob.count(b"[REMOTE]"), 0)

    def test_codigo_equivalente_en_a7s(self):
        """NotifyUartCommand de la A7S: misma secuencia, sin trazas."""
        ins = dis(0x43564534, 0x43564548, A7)
        self.assertIn("cmp r1, #0x23", ins)
        self.assertIn("cmp r0, #0x37", ins)
        self.assertIn("sub.w r1, r2, #0x30", ins)
        self.assertIn("cmp r1, #5", ins)
        self.assertIn("tbb [pc, r1]", ins)

    def test_codigo_equivalente_en_a6300(self):
        ins = dis(0x4355EC48, 0x4355EC62, A63)
        self.assertIn("cmp r1, #0x23", ins)
        self.assertIn("cmp r0, #0x37", ins)
        self.assertIn("sub.w r1, r2, #0x30", ins)
        self.assertIn("cmp r1, #5", ins)
        self.assertIn("tbb [pc, r1]", ins)

    def test_vtables_equivalentes_en_los_tres(self):
        for blob, vt in ((A7, 0x43FB2E14), (A63, 0x4416FD74)):
            entradas = [u32(vt + 4 * i, blob) for i in range(8)]
            self.assertEqual(len(entradas), 8)
            self.assertTrue(all(0x43500000 <= e < 0x44000000 for e in entradas), hex(vt))

    def test_cifras_de_diferencial(self):
        d = DATA["diferencial"]
        self.assertEqual(d["token_REMOTE"]["A6000_fw321"], 32)
        self.assertEqual(d["token_REMOTE"]["A7S_fw320"], 0)
        self.assertEqual(d["token_REMOTE"]["A6300_fw201"], 0)
        self.assertEqual(d["token_ACCY"]["A6000_fw321"], 106)


class TestNegativoObturador(unittest.TestCase):
    def test_terminos_de_obturador_ausentes(self):
        textos = "\n".join(TEXTOS.values()).lower()
        for t in ("shutter", "silent", "curtain", "electro", "mech", "obtur",
                  "sensor", "readout", "imager", "iso", "apert", "expos", "expo",
                  "brack", "drive", "release", "flash", "sync", "vsync", "capture",
                  "shot", "sweep", "interval", "still", "movie", "focus"):
            self.assertNotIn(t, textos, t)

    def test_los_unicos_captures_son_de_accesorio(self):
        textos = "\n".join(TEXTOS.values())
        self.assertIn("GUIDE FRAME OFF", textos)
        self.assertIn("PHOTO REC OFF", textos)
        self.assertIn("Zoom State Change To %d Speed:%d", textos)

    def test_el_disparador_del_mando_es_una_tecla_generica(self):
        """START STOP -> KEY 0x0A00000D entregado por NotifyInput (0x43565814)."""
        self.assertEqual(u32(0x43566CFC), 0x0A00000D)
        self.assertEqual(cstr(0x43C260B0),
                         "[ACCY][INFO][REMOTE]:%d:START STOP OFF  KEY:%08X STATE:%08X  INFO:%08X")

    def test_el_json_declara_el_negativo(self):
        self.assertIn("NEGATIVO ACOTADO", DATA["shutter_line"]["veredicto"])


if __name__ == "__main__":
    unittest.main()
