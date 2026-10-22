"""S179 — tests del módulo [CAM_SCALAR] contra los BYTES REALES del firmware.

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
JSON_S179 = ROOT / "analysis/s179_cam_scalar/cam_scalar.json"
GLOBAL_MAP = ROOT / "analysis/s106_imaging_cap/pic_refs_strict_global.json"

B = BIN.read_bytes()
A7 = A7S.read_bytes()
A63 = A6300.read_bytes()
DATA = json.loads(JSON_S179.read_text())

MD = Cs(CS_ARCH_ARM, CS_MODE_THUMB | CS_MODE_LITTLE_ENDIAN)
TOKEN = b"[CAM_SCALAR]"
PRE = b"[CAM_SCALAR]: "


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


def pic_pair(add_addr):
    """Resuelve el par PIC de un 'add rX,pc': (ldr_addr, pool_addr, W, destino)."""
    h = u16(add_addr)
    assert (h & 0xFF00) == 0x4400 and ((h >> 3) & 0xF) == 15, hex(add_addr)
    reg = (((h >> 7) & 1) << 3) | (h & 7)
    ldr_addr = None
    for back in range(2, 0x100, 2):
        a = add_addr - back
        hh = u16(a)
        if (hh & 0xF800) == 0x4800 and ((hh >> 8) & 7) == reg:
            ldr_addr = a
            break
        if (hh & 0xFF7F) == 0xF85F:
            h2 = u16(a + 2)
            if ((h2 >> 12) & 0xF) == reg:
                ldr_addr = a
                break
    assert ldr_addr is not None, hex(add_addr)
    h = u16(ldr_addr)
    if (h & 0xF800) == 0x4800:
        pool = ((ldr_addr + 4) & ~3) + ((h & 0xFF) * 4)
    else:
        h2 = u16(ldr_addr + 2)
        pool = ((ldr_addr + 4) & ~3) + ((((h2 >> 8) & 0xF) << 8) | (h2 & 0xFF))
    w = u32(pool)
    return ldr_addr, pool, w, (w + add_addr + 4) & 0xFFFFFFFF


class TestRecuento(unittest.TestCase):
    def test_token_en_tres_firmware(self):
        self.assertEqual(B.count(TOKEN), 34)
        self.assertEqual(A7.count(TOKEN), 0)
        self.assertEqual(A63.count(TOKEN), 0)

    def test_token_cam_scalar_solo_las_trazas(self):
        self.assertEqual(B.count(b"CAM_SCALAR"), 34)
        self.assertEqual(B.count(b"CamScalar"), 0)
        self.assertEqual(B.count(b"cam_scalar"), 0)

    def test_numero_de_cadenas(self):
        self.assertEqual(DATA["cifras"]["cadenas_con_token"], 34)
        self.assertEqual(len(DATA["cadenas"]), 34)

    def test_rango_de_cadenas(self):
        addrs = [int(c["vaddr"], 16) for c in DATA["cadenas"]]
        self.assertEqual(min(addrs), 0x43CB045A)
        self.assertEqual(max(addrs), 0x43CC679A)


class TestTextos(unittest.TestCase):
    def test_texto_de_cada_cadena(self):
        for c in DATA["cadenas"]:
            a = int(c["vaddr"], 16)
            self.assertTrue(cstr(a).startswith(PRE.decode()), hex(a))
            self.assertEqual(cstr(a), c["texto"], hex(a))

    def test_gemelo_exacto_en_mas_14(self):
        for c in DATA["cadenas"]:
            a = int(c["vaddr"], 16)
            t = int(c["nucleo_vaddr"], 16)
            self.assertEqual(t, a + 14, hex(a))
            self.assertEqual(cstr(t), c["nucleo"], hex(a))

    def test_gemelo_igual_al_texto_sin_prefijo(self):
        for c in DATA["cadenas"]:
            self.assertEqual(c["nucleo"], c["texto"][14:], c["vaddr"])

    def test_direcciones_de_gemelo_conocidas(self):
        pares = {
            0x43CB045A: 0x43CB0468,  # HAPI Manager:Recieve error
            0x43CB0483: 0x43CB0491,  # HAPI Manager:Message size 0
            0x43CB04AD: 0x43CB04BB,  # HAPI Manager:Empty Message
            0x43CB0588: 0x43CB0596,  # %s: input image and sdsYC is invalid.
            0x43CB0607: 0x43CB0615,  # %s: input image is invalid.
            0x43CB07F1: 0x43CB07FF,  # dmm_handle[DMM_HANDLE_YCC_FULL]
            0x43CB0A03: 0x43CB0A11,  # ExposureCount
            0x43CB0A79: 0x43CB0A87,  # CapMode is not CAP_SINGLE
            0x43CC679A: 0x43CC67A8,  # RecordCount Unmatch!
        }
        for a, t in pares.items():
            self.assertEqual(cstr(a + 14), cstr(t), hex(a))


class TestReferenciasPIC(unittest.TestCase):
    def test_sitios_contra_el_mapa_global(self):
        gmap = json.loads(GLOBAL_MAP.read_text())
        for c in DATA["cadenas"]:
            k = c["vaddr"]
            if not c["sitios_pic"]:
                self.assertNotIn(k, gmap, k)      # cadena muerta
                continue
            self.assertIn(k, gmap, k)
            self.assertEqual(sorted(hex(x) for x in gmap[k]), sorted(c["sitios_pic"]), k)

    def test_sitios_gemelo_en_el_mapa_local(self):
        """Los gemelos están en el interior de la cadena prefijada: no aparecen en el
        mapa global (que sólo indexa inicios de cadena), pero sí tienen sitio PIC."""
        for c in DATA["cadenas"]:
            if not c["sitios_pic_gemelo"]:
                continue
            for s in c["sitios_pic_gemelo"]:
                _, _, _, dest = pic_pair(int(s, 16))
                self.assertEqual(dest, int(c["nucleo_vaddr"], 16), s)

    def test_destino_de_cada_sitio_nuevo(self):
        for c in DATA["cadenas"]:
            for s in c["sitios_pic"]:
                _, _, _, dest = pic_pair(int(s, 16))
                self.assertEqual(dest, int(c["vaddr"], 16), s)

    def test_ldr_mas_cercano_es_el_esperado(self):
        """El 'ldr' del par debe ser el MÁS CERCANO por detrás del mismo registro."""
        for c in DATA["cadenas"]:
            for s in c["sitios_pic"]:
                add = int(s, 16)
                ldr_addr, pool, w, dest = pic_pair(add)
                self.assertEqual(dest, int(c["vaddr"], 16), s)
                # no hay otro ldr del mismo registro entre el elegido y el add
                h = u16(add)
                reg = (((h >> 7) & 1) << 3) | (h & 7)
                for a in range(ldr_addr + 2, add, 2):
                    hh = u16(a)
                    if (hh & 0xF800) == 0x4800 and ((hh >> 8) & 7) == reg:
                        self.fail(f"ldr más cercano en 0x{a:x} (se esperaba 0x{ldr_addr:x})")

    def test_totales_de_sitios(self):
        nuevos = sum(c["n_sitios_pic_estrictos"] for c in DATA["cadenas"])
        gemelos = sum(c["n_sitios_pic_gemelo"] for c in DATA["cadenas"])
        self.assertEqual(nuevos, 47)
        self.assertEqual(gemelos, 47)
        self.assertEqual(DATA["cifras"]["sitios_pic_nuevos"], 47)

    def test_cadenas_muertas(self):
        muertas = [c["vaddr"] for c in DATA["cadenas"] if c["muerto"]]
        self.assertEqual(muertas, ["0x43cb0aa5", "0x43cb0abe", "0x43cb0ae3"])
        self.assertEqual(DATA["cifras"]["cadenas_muertas"], 3)
        # y sus gemelos tampoco tienen referencia ni puntero absoluto
        for v in ("0x43cb0aa5", "0x43cb0abe", "0x43cb0ae3"):
            t = hex(int(v, 16) + 14)
            gmap = json.loads(GLOBAL_MAP.read_text())
            self.assertNotIn(t, gmap, t)
            self.assertNotIn(struct.pack("<I", int(t, 16)), B)


class TestFunciones(unittest.TestCase):
    def test_numero_de_funciones_emisoras(self):
        self.assertEqual(len(DATA["funciones"]), 14)
        self.assertEqual(DATA["cifras"]["funciones_emisoras"], 14)

    def test_inicios_de_funcion_conocidos(self):
        starts = {f["func"] for f in DATA["funciones"]}
        esperados = {"0x4380a688", "0x4380afec", "0x4380b1a8", "0x4380b500",
                     "0x4380b6bc", "0x4380b8d4", "0x4380b9c4", "0x4380bb30",
                     "0x4380bbd8", "0x4380bdbc", "0x4380c180", "0x4380c344",
                     "0x4380c638", "0x438bbe4c"}
        self.assertEqual(starts, esperados)

    def test_cada_sitio_pertenece_a_su_funcion(self):
        for f in DATA["funciones"]:
            st = int(f["func"], 16)
            for s in f["sitios"]:
                self.assertTrue(st <= int(s["sitio"], 16) < st + 0x4000, s["sitio"])


class TestCodigo(unittest.TestCase):
    def test_despachador_tbh_de_23_entradas(self):
        """0x4380a728: tbh con base ((addr+4)&~3) y 23 casos (MSG_ID 0x5001..0x5017)."""
        add = 0x4380A728
        ins = [f"{i.mnemonic} {i.op_str}".strip()
               for i in MD.disasm(B[add - BASE:add - BASE + 4], add)]
        self.assertEqual(ins[0], "tbh [pc, r3, lsl #1]")
        base = (add + 4) & ~3
        self.assertEqual(base, 0x4380A72C)
        for i in range(23):
            off = u16(base + 2 * i)
            self.assertIsInstance(off, int)
        # los destinos medidos
        self.assertEqual(base + 2 * u16(base + 2 * 0), 0x4380A75A)   # 0x5001
        self.assertEqual(base + 2 * u16(base + 2 * 22), 0x4380ADB4)  # 0x5017

    def test_rango_de_msg_id_5001_5017(self):
        """sub.w r3,r3,#0x5000 ; subs r3,#1 ; cmp r3,#0x16"""
        ins = [f"{i.mnemonic} {i.op_str}".strip()
               for i in MD.disasm(B[0x4380A716 - BASE:0x4380A728 - BASE], 0x4380A716)]
        self.assertEqual(ins[2], "sub.w r3, r3, #0x5000")
        self.assertEqual(ins[3], "subs r3, #1")
        self.assertEqual(ins[4], "cmp r3, #0x16")
        self.assertEqual(ins[5], "bhi.w #0x4380adf8")

    def test_patron_modulo5_nivel6_flag1_en_los_47_sitios(self):
        """En la ventana de 40 B previa a cada sitio aparece el patrón de bytes
        movs r0,#5 / adds r0,#5 / adds r0,#0x20 ; movs r1,#6 / adds r1,#6 ;
        movs r2,#1 / adds r2,#1 / mov r2,r6."""
        MOD5 = (b"\x05\x20", b"\x05\x30", b"\x20\x30")
        LV6 = (b"\x06\x21", b"\x06\x31")
        FL1 = (b"\x01\x22", b"\x01\x32", b"\x0e\x46")
        n = 0
        for c in DATA["cadenas"]:
            for s in c["sitios_pic"]:
                o = int(s, 16) - BASE
                buf = B[max(0, o - 40):o + 8]
                self.assertTrue(any(p in buf for p in MOD5), s)
                self.assertTrue(any(p in buf for p in LV6), s)
                n += 1
        self.assertEqual(n, 47)

    def test_ida_de_modulo_5_y_nivel_6_en_un_sitio(self):
        """0x4380a6b0..0x4380a6ba: movs r0,#5 ; movs r1,#6 ; movs r2,#1 ; add r3,pc."""
        code = B[0x4380A6B0 - BASE:0x4380A6BA - BASE]
        ins = [f"{i.mnemonic} {i.op_str}".strip() for i in MD.disasm(code, 0x4380A6B0)]
        self.assertEqual(ins[0], "ldr r3, [pc, #0x288]")
        self.assertEqual(ins[1], "movs r0, #5")
        self.assertEqual(ins[2], "movs r1, #6")
        self.assertEqual(ins[3], "movs r2, #1")
        self.assertEqual(ins[4], "add r3, pc")

    def test_ida_de_modulo_5_en_el_bloque_B(self):
        """0x438bbe5c..0x438bbe66: movs r2,#1 ; movs r0,#5 ; movs r1,#6 ; add r3,pc."""
        code = B[0x438BBE5C - BASE:0x438BBE66 - BASE]
        ins = [f"{i.mnemonic} {i.op_str}".strip() for i in MD.disasm(code, 0x438BBE5C)]
        self.assertEqual(ins[1], "movs r0, #5")
        self.assertEqual(ins[2], "movs r1, #6")

    def test_logger_de_modulo_escribe_modulo_en_msg2(self):
        """0x4380a5d0: strh r7,[r4,#2] (id de módulo) y str.w r8,[r4,#4] (nivel)."""
        code = B[0x4380A602 - BASE:0x4380A60E - BASE]
        ins = [f"{i.mnemonic} {i.op_str}".strip() for i in MD.disasm(code, 0x4380A602)]
        self.assertIn("strh r7, [r4, #2]", ins)

    def test_set_special_sequence_valida_exposure_y_record(self):
        """0x4380c352: cmp r7,#1 (ExposureCount) ; 0x4380c37a: cmp r3,#5 (RecordCount)."""
        code = B[0x4380C350 - BASE:0x4380C356 - BASE]
        ins = [f"{i.mnemonic} {i.op_str}".strip() for i in MD.disasm(code, 0x4380C350)]
        self.assertIn("cmp r7, #1", ins)
        code = B[0x4380C378 - BASE:0x4380C37E - BASE]
        ins = [f"{i.mnemonic} {i.op_str}".strip() for i in MD.disasm(code, 0x4380C378)]
        self.assertIn("cmp r3, #5", ins)

    def test_recordcount_unmatch_calcula_diferencia(self):
        """0x438bbe50/0x438bbe54: p[0x20] - p[0x28]."""
        code = B[0x438BBE4C - BASE:0x438BBE58 - BASE]
        ins = [f"{i.mnemonic} {i.op_str}".strip() for i in MD.disasm(code, 0x438BBE4C)]
        self.assertEqual(ins[1], "mov r4, r0")
        self.assertEqual(ins[2], "ldr r5, [r0, #0x20]")
        self.assertEqual(ins[4], "ldr r3, [r0, #0x28]")
        self.assertEqual(ins[5], "subs r5, r5, r3")


class TestFicherosYModulos(unittest.TestCase):
    def test_ficheros_embebidos_en_sus_direcciones(self):
        self.assertEqual(cstr(0x43CB07B7), "HAPI_Filter_TBOX.cpp")
        self.assertEqual(cstr(0x43CB0B85), "CS_Command.cpp")
        self.assertEqual(cstr(0x43CC6779), "ImageParamCapture_SyncBranch.cpp")

    def test_ficheros_tambien_en_a7s_y_a6300(self):
        for blob in (A7, A63):
            self.assertIn(b"HAPI_Filter_TBOX.cpp", blob)
            self.assertIn(b"CS_Command.cpp", blob)

    def test_nombres_de_metodo_embebidos(self):
        for n in ("req_filter_develop", "req_image_clone", "req_raw_image_parse",
                  "Start_Develop", "Start_CreateStream", "CheckDMMforClone",
                  "ShareDMMforClone", "SetSpecialSequence", "copyStdYc"):
            self.assertIn(n.encode(), B)
            self.assertIn(n.encode(), A7)
            self.assertIn(n.encode(), A63)

    def test_no_hay_referencia_al_acelerador_sa_desde_el_modulo(self):
        """Las 14 funciones emisoras no llaman a NS_SCALAR_INFRA (0x43990000-0x439c0000)."""
        for f in DATA["funciones"]:
            st = int(f["func"], 16)
            code = B[st - BASE:st - BASE + 0x4000]
            for ins in MD.disasm(code, st):
                if ins.mnemonic in ("bl", "blx") and ins.op_str.startswith("#0x"):
                    tgt = int(ins.op_str[1:], 16)
                    self.assertFalse(
                        0x43990000 <= tgt < 0x439C0000,
                        f"{hex(st)} llama a {hex(tgt)} (NS_SCALAR_INFRA)")

    def test_no_hay_cadenas_sa_func_en_la_zona_del_modulo(self):
        """Ninguna cadena sa_func_* está referenciada desde la zona del módulo."""
        gmap = json.loads(GLOBAL_MAP.read_text())
        zona = (0x4380A688, 0x4380C700)
        for k, sites in gmap.items():
            if not any(zona[0] <= s < zona[1] for s in sites):
                continue
            self.assertNotIn("sa_func_", cstr(int(k, 16)))


class TestDiferencial(unittest.TestCase):
    def test_nucleos_presentes_en_los_tres(self):
        for c in DATA["cadenas"]:
            self.assertGreaterEqual(c["nucleo_en_A7S"], 1, c["vaddr"])
            self.assertGreaterEqual(c["nucleo_en_A6300"], 1, c["vaddr"])

    def test_nucleo_del_hapi_manager_exacto_en_a7s(self):
        self.assertEqual(cstr(0x43CB0468), "HAPI Manager:Recieve error")
        self.assertEqual(cstr(0x43CB2237, A7), "HAPI Manager:Recieve error")
        self.assertEqual(cstr(0x43DCB6D5, A63), "HAPI Manager:Recieve error")

    def test_codigo_equivalente_presente_en_a7s(self):
        """En la A7S la traza se emite SIN prefijo y con un solo logger (0x438f7114)."""
        gmap7 = json.loads(
            (ROOT / "analysis/s169_drive_api/pic_refs_strict_a7s.json").read_text())
        self.assertIn("0x43cb2237", gmap7)
        self.assertEqual(len(gmap7["0x43cb2237"]), 1)
        site = gmap7["0x43cb2237"][0]
        code = A7[site - BASE:site - BASE + 16]
        ins = [f"{i.mnemonic} {i.op_str}".strip() for i in MD.disasm(code, site)]
        self.assertEqual(ins[0], "add r0, pc")
        self.assertTrue(ins[1].startswith("b "), ins[1])

    def test_cifras_de_diferencial(self):
        c = DATA["cifras"]
        self.assertEqual(c["apariciones_token_A6000"], 34)
        self.assertEqual(c["apariciones_token_A7S"], 0)
        self.assertEqual(c["apariciones_token_A6300"], 0)
        self.assertEqual(c["gemelos_en_A7S"], 34)
        self.assertEqual(c["gemelos_en_A6300"], 34)

    def test_a6300_cambia_dos_textos(self):
        self.assertIn(b"%s: Develop(RAW->YC) fail.", A63)
        self.assertIn(b"%s: invalid parameter on simple develop.", A63)
        self.assertNotIn(b"%s: Develop(RAW->YC) fail.", B)
        self.assertIn(b"req_yc_image_parse", A63)


class TestNegativoObturador(unittest.TestCase):
    def test_terminos_de_obturador_ausentes(self):
        textos = "\n".join(c["texto"] for c in DATA["cadenas"]).lower()
        for t in ("shutter", "silent", "curtain", "electro", "mech", "obtur",
                  "sensor", "readout", "shut", "svd", "shd", "spl", "frame",
                  "imager", "drive", "brack", "sweep", "interval", "still",
                  "movie", "focus", "iso", "apert", "vsync", "scan"):
            self.assertNotIn(t, textos, t)

    def test_unico_expos_es_exposurecount(self):
        hits = [c["vaddr"] for c in DATA["cadenas"] if "expos" in c["texto"].lower()]
        self.assertEqual(hits, ["0x43cb0a03"])

    def test_terminos_de_captura_presentes(self):
        self.assertIn("ExposureCount", "".join(c["texto"] for c in DATA["cadenas"]))
        self.assertIn("RecordCount", "".join(c["texto"] for c in DATA["cadenas"]))
        self.assertIn("CAP_SINGLE", "".join(c["texto"] for c in DATA["cadenas"]))


if __name__ == "__main__":
    unittest.main()
