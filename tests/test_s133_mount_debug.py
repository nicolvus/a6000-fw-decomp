"""Tests for S133 — `[MOUNT_DEBUG]`, el subsistema de trazas de la montura (132 trazas).

Tests de **bytes reales** sobre la A6000 fw3.21 y diferencial con A7S fw3.20 / A6300 fw2.01.
Cada comprobación decodifica el binario: si cambia una dirección o una instrucción, falla.
"""

import bisect
import json
import pathlib
import struct

ROOT = pathlib.Path(__file__).resolve().parents[1]
BASE = 0x43541000
BIN = "analysis/rea-independent/input/av-cam.bin"
A7S = (
    "firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/"
    "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"
)
A6300 = (
    "firmware/extracted/a6300-fw201/payload/firmware.tar_unpacked/"
    "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"
)
PREFIX = b"[MOUNT_DEBUG]: "
CODE_LO, CODE_HI = 0x43541000, 0x437D0000
MAX_LDR_GAP = 4096


def _data(path=BIN):
    with open(ROOT / path, "rb") as fh:
        return fh.read()


DATA = _data()
U16S = struct.Struct("<H")
U32S = struct.Struct("<I")


def _u16(addr, data=None):
    data = DATA if data is None else data
    off = addr - BASE
    assert 0 <= off <= len(data) - 2, f"vaddr {hex(addr)} fuera del binario"
    return U16S.unpack_from(data, off)[0]


def _u32(addr, data=None):
    data = DATA if data is None else data
    off = addr - BASE
    assert 0 <= off <= len(data) - 4, f"vaddr {hex(addr)} fuera del binario"
    return U32S.unpack_from(data, off)[0]


def _cstr(addr, data=None, maxlen=600):
    data = DATA if data is None else data
    off = addr - BASE
    end = off
    while end < len(data) and end < off + maxlen and data[end] != 0:
        end += 1
    return data[off:end].decode("latin1")


def _summary():
    with open(ROOT / "analysis" / "s133_mount_debug" / "mount_debug.json",
              encoding="utf-8") as fh:
        return json.load(fh)


def _strings(data=None, prefix=PREFIX):
    """(vaddr, texto) de cada cadena que empieza por el prefijo, en orden."""
    data = DATA if data is None else data
    out = []
    start = 0
    while True:
        i = data.find(prefix, start)
        if i < 0:
            break
        end = i
        while end < len(data) and data[end] != 0:
            end += 1
        out.append((BASE + i, data[i:end].decode("latin1")))
        start = i + 1
    return out


def _bl_target(site):
    h1, h2 = _u16(site), _u16(site + 2)
    assert (h1 & 0xF800) == 0xF000, (hex(site), hex(h1))
    s = (h1 >> 10) & 1
    imm10 = h1 & 0x3FF
    j1, j2 = (h2 >> 13) & 1, (h2 >> 11) & 1
    i1, i2 = 1 - (j1 ^ s), 1 - (j2 ^ s)
    off = (s << 24) | (i1 << 23) | (i2 << 22) | (imm10 << 12) | ((h2 & 0x7FF) << 1)
    if off & (1 << 24):
        off -= 1 << 25
    base = (site + 4) & ~3 if not (h2 & 0x1000) else site + 4
    return base + off


def _b16_target(site):
    h = _u16(site)
    assert (h & 0xF800) == 0xE000, (hex(site), hex(h))
    off = h & 0x7FF
    if off & 0x400:
        off -= 0x800
    return site + 4 + off * 2


class TestCadenas:
    def test_conteo_y_rango(self):
        s = _strings()
        assert len(s) == 132
        assert s[0][0] == 0x43C9648D
        assert s[-1][0] == 0x43C9A10F

    def test_el_json_lista_las_mismas_132(self):
        s = _summary()
        assert s["counts"]["strings"] == 132
        assert [int(x["vaddr"], 16) for x in s["strings"]] == [v for v, _ in _strings()]
        assert [x["text"] for x in s["strings"]] == [t for _, t in _strings()]

    def test_cada_cadena_esta_en_su_vaddr_y_termina_en_nul(self):
        s = _summary()
        for item in s["strings"]:
            v = int(item["vaddr"], 16)
            assert _cstr(v) == item["text"], hex(v)
            fin = v - BASE + len(item["text"].encode("latin1"))
            assert DATA[fin] == 0, f"{hex(v)} sin NUL final"
            assert item["text"].startswith("[MOUNT_DEBUG]: "), hex(v)

    def test_todas_referenciadas(self):
        s = _summary()
        assert s["counts"]["unreferenced"] == 0
        assert s["unreferenced"] == []
        assert all(x["sites"] for x in s["strings"])

    def test_prefijos_de_la_imagen(self):
        d = _summary()["counts"]["prefix_tokens"]
        assert d["[MOUNT_DEBUG]"] == 132
        assert d["[MOUNT_ERROR]"] == 80
        assert d["[MOUNT_INFO]"] == 6
        assert d["[MOUNT_WARNING]"] == 5
        assert d["[MOUNT_*]"] == 223
        for tok, n in (("[MOUNT_DEBUG]", 132), ("[MOUNT_ERROR]", 80),
                       ("[MOUNT_INFO]", 6), ("[MOUNT_WARNING]", 5)):
            assert DATA.count(tok.encode()) == n, tok
        assert sum(d[k] for k in
                   ("[MOUNT_DEBUG]", "[MOUNT_ERROR]", "[MOUNT_INFO]",
                    "[MOUNT_WARNING]")) == 223

    def test_cadenas_compartidas_por_varias_funciones(self):
        s = _summary()
        multi = [x for x in s["strings"] if len(x["funcs"]) > 1]
        # tres cadenas compartidas por 2 funciones y una por 3 funciones
        assert len(multi) == 4
        tres = [x for x in multi if len(x["funcs"]) == 3]
        assert len(tres) == 1
        assert tres[0]["vaddr"] == "0x43c965b9"
        assert tres[0]["funcs"] == ["0x436e1254", "0x436e1328", "0x436e14ac"]
        assert len(tres[0]["sites"]) == 3
        assert sorted(x["vaddr"] for x in multi if len(x["funcs"]) == 2) == [
            "0x43c97ac6", "0x43c97b06", "0x43c97b24"]


class TestSitios:
    @staticmethod
    def _ldrs(lo, hi):
        out = []
        a = lo
        while a < hi:
            h = _u16(a)
            reg = lit = None
            if (h & 0xF800) == 0x4800:                     # ldr rT, [pc, #imm5*4]
                reg = (h >> 8) & 7
                lit = ((a + 4) & ~3) + ((h & 0xFF) * 4)
            elif (h & 0xFF7F) == 0xF85F:                   # ldr.w rT, [pc, #imm12]
                h2 = _u16(a + 2)
                reg = (h2 >> 12) & 0xF
                lit = ((a + 4) & ~3) + ((((h2 >> 8) & 0xF) << 8) | (h2 & 0xFF))
            if reg is not None and BASE <= lit <= BASE + len(DATA) - 4:
                out.append((a, reg, _u32(lit)))
            a += 2
        return out

    @staticmethod
    def _add_reg(h):
        assert (h & 0xFF00) == 0x4400 and ((h >> 3) & 0xF) == 15, hex(h)
        return (((h >> 7) & 1) << 3) | (h & 7)

    def _resolver(self, site):
        """Regla estricta: `add rX,pc` + `ldr rX` más cercano por detrás (<=4 KB)."""
        reg = self._add_reg(_u16(site))
        ldrs = [(a, w) for a, r, w in self._ldrs(site - MAX_LDR_GAP - 4, site) if r == reg]
        assert ldrs, f"sin ldr r{reg} antes de {hex(site)}"
        la, w = ldrs[-1]
        assert site - la <= MAX_LDR_GAP, hex(site)
        return (w + (site + 4)) & 0xFFFFFFFF

    def test_los_148_sitios_resuelven_su_cadena(self):
        s = _summary()
        total = 0
        for item in s["strings"]:
            v = int(item["vaddr"], 16)
            for sitio in item["sites"]:
                a = int(sitio["site"], 16)
                assert self._resolver(a) == v, f"{hex(a)} no apunta a {hex(v)}"
                total += 1
        assert total == 148

    def test_sitios_unicos_y_suma_por_funcion(self):
        s = _summary()
        assert s["counts"]["sites"] == 148
        assert len({x["site"] for item in s["strings"] for x in item["sites"]}) == 148
        assert sum(f["site_count"] for f in s["functions"]) == 148
        assert sum(len(f["sites"]) for f in s["functions"]) == 148

    def test_reparto_por_sink(self):
        s = _summary()
        esperado = {
            "0x436e41e4": 94, "0x436e03b0": 29, "0x436e3914": 10,
            "0x436fe410": 6, "0x436e808c": 4, "0x436e9c70": 2,
            "0x436e36a8": 1, "0x436e7bec": 1, "0x436fdfc4": 1,
        }
        real = {}
        for item in s["strings"]:
            for sitio in item["sites"]:
                real[sitio["sink"]] = real.get(sitio["sink"], 0) + 1
        assert real == esperado
        assert s["counts"]["sink_sites"] == {**esperado, "sin_resolver": 0}
        assert sum(esperado.values()) == 148

    def test_sitios_de_cada_funcion_pertenecen_a_sus_cadenas(self):
        s = _summary()
        por_func = {f["vaddr"]: f for f in s["functions"]}
        for item in s["strings"]:
            for sitio in item["sites"]:
                f = por_func[sitio["func"]]
                assert sitio["site"] in f["sites"], (sitio["site"], f["vaddr"])
                assert item["vaddr"] in f["string_vaddrs"]


class TestFunciones:
    @staticmethod
    def _es_prologo_push_lr(addr):
        for i in range(0, 8, 2):
            h = _u16(addr + i)
            if (h & 0xFE00) == 0xB400 and (h & 0x100):      # push {...,lr}
                return True
            if h == 0xE92D and (_u16(addr + i + 2) & 0x4000):  # push.w {...,lr}
                return True
        return False

    def test_65_funciones_y_prologos(self):
        s = _summary()
        assert s["counts"]["functions"] == 65
        assert len(s["functions"]) == 65
        approx = {f["vaddr"] for f in s["functions"] if f["approx_function"]}
        assert approx == {"0x436e1328", "0x436e3bf8"}
        for f in s["functions"]:
            a = int(f["vaddr"], 16)
            if f["approx_function"]:
                continue
            assert self._es_prologo_push_lr(a), f"{hex(a)} sin push con lr"

    def test_64_funciones_por_primer_sitio(self):
        s = _summary()
        assert s["counts"]["functions_by_first_site"] == 64
        primeros = {item["sites"][0]["func"] for item in s["strings"]}
        assert len(primeros) == 64
        # la diferencia es la cadena con sitios en 3 funciones
        todos = {sitio["func"] for item in s["strings"] for sitio in item["sites"]}
        assert len(todos) == 65

    def test_prologos_medidos_en_bytes(self):
        assert _u16(0x436E2678) == 0xE92D      # push.w
        assert _u16(0x436E267A) == 0x4FF0
        assert _u16(0x436E3508) == 0xB570      # push {r4,r5,r6,lr}
        assert _u16(0x436E4598) == 0xB573      # push {r0,r1,r4,r5,r6,lr}
        assert _u16(0x436E5E3C) == 0xE92D      # push.w
        assert _u16(0x436E5E3E) == 0x47F0
        assert _u16(0x436E41E4) == 0xB408      # sink wrapper
        assert _u16(0x436E03B0) == 0xB408      # sink directo
        assert _u16(0x436E9C70) == 0xB408      # sink con tag fijo


class TestMecanismo:
    def test_sink_directo_0x436e03b0(self):
        assert _u16(0x436E03C8) == 0x229A          # movs r2,#0x9a
        assert _bl_target(0x436E03CC) == 0x435612D0  # osal_try_valloc_msg
        assert _bl_target(0x436E03F6) == 0x439C5004  # vsnprintf (0x81)
        assert _bl_target(0x436E041E) == 0x43AD9EAE  # hook
        assert _bl_target(0x436E0426) == 0x4356120C  # osal_snd_msg

    def test_wrapper_0x436e41e4(self):
        assert _u16(0x436E41FE) == 0x229A          # movs r2,#0x9a
        assert _bl_target(0x436E4202) == 0x435612D0
        assert _bl_target(0x436E4236) == 0x43561244
        assert _bl_target(0x436E424C) == 0x439C5004
        assert _bl_target(0x436E4274) == 0x43ADA13C
        assert _bl_target(0x436E427C) == 0x4356120C

    def test_los_9_sinks_comparten_el_mismo_arranque(self):
        for sink in ("0x436e3914", "0x436fe410", "0x436e808c", "0x436e36a8",
                     "0x436e7bec", "0x436fdfc4"):
            a = int(sink, 16)
            assert _u16(a) == 0xB408, sink        # push {r3}
            assert _u16(a + 2) == 0x2300, sink    # movs r3,#0
            assert _u16(a + 4) == 0xE92D, sink    # push.w

    def test_sink_0x436e9c70_fija_tag_0x125(self):
        assert _u16(0x436E9C9A) == 0xF240      # movw r3,#0x125
        assert _u16(0x436E9C9C) == 0x1325

    def test_patron_de_llamada_tipico(self):
        assert _u16(0x436E4B42) == 0xF240      # movw r0,#0x125
        assert _u16(0x436E4B44) == 0x1025
        assert _u16(0x436E4B46) == 0x2203      # movs r2,#3
        assert _u16(0x436E4B48) == 0x447B      # add r3,pc
        assert _bl_target(0x436E4B4A) == 0x436E41E4

    def test_sitios_de_cola_acaban_en_el_wrapper(self):
        # 0x436e4378: pop.w {r4,lr} + b.w 0x436e41e4
        assert _u16(0x436E437A) == 0xE8BD
        assert _u16(0x436E437C) == 0x4010
        assert _bl_target(0x436E437E) == 0x436E41E4
        for site in (0x436E55FE, 0x436E560E):
            assert _u16(site) == 0x447B, hex(site)          # add r3,pc
            assert _b16_target(site + 2) == 0x436E561E, hex(site)
        # el tercer sitio cae directamente en la cola comun
        assert _u16(0x436E561C) == 0x447B
        assert _u16(0x436E561E) == 0xE8BD
        assert _u16(0x436E561E) == 0xE8BD
        assert _u16(0x436E5620) == 0x4070                    # pop.w {r4,r5,r6,lr}
        assert _bl_target(0x436E5622) == 0x436E41E4


class TestMountChkCamCmdState:
    def test_lecturas_y_rango_c00_c03(self):
        assert _u16(0x436E4598) == 0xB573
        assert _bl_target(0x436E459C) == 0x436E2368
        assert _u16(0x436E45A4) == 0xF890      # ldrb.w r2,[r0,#0x28]
        assert _u16(0x436E45A6) == 0x2028
        assert _u16(0x436E45A8) == 0x8C83      # ldrh r3,[r0,#0x24]
        assert _u16(0x436E45B6) == 0xF5B3      # cmp.w r3,#0xc00
        assert _u16(0x436E45B8) == 0x6F40
        assert _u16(0x436E45BE) == 0xF640      # movw r2,#0xc03
        assert _u16(0x436E45C0) == 0x4203
        assert _cstr(0x43C979A0) == "[MOUNT_DEBUG]: [BL]CAM CmdStatus:%04X"
        assert _cstr(0x43C979C6) == "[MOUNT_DEBUG]: [BL]Mount_ChkCamCmdState RetVal:%d"
        assert _bl_target(0x436E45F2 + 2) is not None

    def test_los_dos_sitios_estan_en_la_funcion(self):
        s = _summary()
        f = next(x for x in s["functions"] if x["vaddr"] == "0x436e4598")
        assert f["sites"] == ["0x436e45f2", "0x436e4602"]
        assert f["string_vaddrs"] == ["0x43c979a0", "0x43c979c6"]

    def test_llamadores_bl(self):
        s = _summary()
        f = next(x for x in s["functions"] if x["vaddr"] == "0x436e4598")
        assert set(f["bl_callers"]) == {"0x436e5f7c", "0x436e5ffa"}
        for caller in f["bl_callers"]:
            assert _bl_target(int(caller, 16)) == 0x436E4598


class TestCapturaLog:
    def test_funcion_0x436e3508(self):
        assert _u16(0x436E3508) == 0xB570
        assert _u16(0x436E350A) == 0x200D            # movs r0,#0xd
        assert _bl_target(0x436E350E) == 0x439025E0
        assert _bl_target(0x436E3538) == 0x439C1C2C  # snprintf
        assert _cstr(0x43C97146) == "/mnt/Mount_ms_log_%03d.dat"
        assert DATA[0x43C97146 - BASE + 0x1A] == 0   # tamaño 0x1a, NUL al final
        assert _bl_target(0x436E3546) == 0x436E04B4
        assert _bl_target(0x436E357C) == 0x436E04B4

    def test_trazas_capstart_capstop(self):
        assert _cstr(0x43C97161) == "[MOUNT_DEBUG]: [BL]osal_capstart Ret=%04x"
        assert _cstr(0x43C9718B) == "[MOUNT_DEBUG]: [BL]osal_capstop Ret=%04x"
        # los dos sitios son add rX,pc y comparten el sink directo
        assert _u16(0x436E3550) == 0x447B
        assert _u16(0x436E3586) == 0x447B
        s = _summary()
        por_site = {x["site"]: x for item in s["strings"] for x in item["sites"]}
        assert por_site["0x436e3550"]["sink"] == "0x436e03b0"
        assert por_site["0x436e3586"]["sink"] == "0x436e03b0"

    def test_constructor_de_la_cadena_en_el_binario(self):
        # los 4 slots %03d del nombre se construyen como .dat independiente
        assert b"/mnt/Mount_ms_log_%03d.dat" in DATA
        assert b"\x00/mnt/Mount_ms_log_%03d.dat\x00" in DATA


class TestFuentes:
    def test_mount_controller_cpp(self):
        assert _cstr(0x43C9671A) == (
            "[MOUNT_ERROR]: [BL]ASYNC ERR Mount_Controller.cpp %d lines")
        s = _summary()
        src = next(x for x in s["sources"] if x["vaddr"] == "0x43c9671a")
        assert src["site"] == "0x436e146a"
        assert src["func"] == "0x436e1328"
        assert src["sub_block"] == "sync_send"

    def test_mount_dividedinfo_cpp(self):
        s = _summary()
        divided = [x for x in s["sources"] if x["name"] == "Mount_DividedInfo.cpp"]
        assert [x["vaddr"] for x in divided] == [
            "0x43c972fb", "0x43c9756f", "0x43c97754", "0x43c977bc", "0x43c97802"]
        for x in divided:
            assert _cstr(int(x["vaddr"], 16)) == x["text"]
        assert _cstr(0x43C97754) == (
            "[MOUNT_DEBUG]: Mount_EclipseComInit Mount_DividedInfo.cpp line %d")
        assert _cstr(0x43C97802) == (
            "[MOUNT_DEBUG]: Mount_InitializeEclipseDataForLensDetach "
            "Mount_DividedInfo.cpp line %d")

    def test_solo_dos_cadenas_debug_citan_fichero(self):
        citan = [x for x in _summary()["strings"]
                 if ".cpp" in x["text"]]
        assert [x["vaddr"] for x in citan] == ["0x43c97754", "0x43c97802"]


class TestSubBloques:
    def test_diez_sub_bloques_y_sumas(self):
        s = _summary()
        assert len(s["sub_blocks"]) == 10
        assert sum(b["strings_first_site"] for b in s["sub_blocks"]) == 132
        assert sum(b["sites"] for b in s["sub_blocks"]) == 148
        assert sum(b["functions_touched"] for b in s["sub_blocks"]) == 65

    def test_reparto_exacto(self):
        s = _summary()
        real = {b["id"]: (b["strings_first_site"], b["sites"], b["functions_touched"])
                for b in s["sub_blocks"]}
        assert real == {
            "sync_send": (13, 17, 8),
            "drv_uart": (1, 2, 1),
            "rx_analyzer": (8, 8, 1),
            "cap_lif": (3, 3, 2),
            "divided_eclipse": (10, 10, 8),
            "mount_controller": (47, 50, 35),
            "main_task": (37, 44, 1),
            "lif_tasks": (7, 7, 7),
            "lens_remove": (1, 1, 1),
            "fw_update": (5, 6, 1),
        }

    def test_rangos_de_cada_sub_bloque(self):
        s = _summary()
        real = {b["id"]: tuple(b["string_vaddr_range"]) for b in s["sub_blocks"]}
        assert real["sync_send"] == ("0x43c9648d", "0x43c9678b")
        assert real["drv_uart"] == ("0x43c96946", "0x43c96946")
        assert real["rx_analyzer"] == ("0x43c96e73", "0x43c97010")
        assert real["cap_lif"] == ("0x43c97161", "0x43c971b4")
        assert real["divided_eclipse"] == ("0x43c97218", "0x43c97802")
        assert real["mount_controller"] == ("0x43c9788a", "0x43c98417")
        assert real["main_task"] == ("0x43c98460", "0x43c98a9e")
        assert real["lif_tasks"] == ("0x43c98b58", "0x43c98c8e")
        assert real["lens_remove"] == ("0x43c9a10f", "0x43c9a10f")
        assert real["fw_update"] == ("0x43c9805f", "0x43c981dc")


class TestSinRelacionConObturador:
    CLAVES = ("SHUT", "SENS", "APER", "ACTU", "DIAG", "CONTACT", "FC", "AF")

    def test_ninguna_traza_menciona_la_claves(self):
        textos = [t for _, t in _strings()]
        for clave in self.CLAVES:
            hits = [t for t in textos if clave in t]
            assert hits == [], (clave, hits)

    def test_el_unico_af_es_el_falso_positivo_de_lensdetach(self):
        textos = [t for _, t in _strings()]
        hits = [(i, t) for i, t in enumerate(textos) if "af" in t.lower()]
        assert len(hits) == 1
        assert _cstr(0x43C97802).lower().count("af") == 1
        assert "InitializeEclipseDataForLensDetach" in hits[0][1]
        assert "AF" not in hits[0][1]

    def test_no_existe_ninguna_cadena_diagnosis(self):
        for path in (None, A7S, A6300):
            data = DATA if path is None else _data(path)
            assert b"Diagnosis" not in data, path
            assert b"DIAGNOSIS" not in data, path
            assert b"diagnosis" not in data, path


class TestDiferencial:
    def test_las_etiquetas_son_nuevas_en_fw321(self):
        for path in (A7S, A6300):
            b = _data(path)
            for tok in (b"[MOUNT_", b"[MOUNT_DEBUG", b"[MOUNT_ERROR",
                        b"[MOUNT_INFO", b"[MOUNT_WARNING"):
                assert b.count(tok) == 0, (path, tok)

    def test_ningun_mensaje_interior_es_cadena_independiente(self):
        s = _summary()["strings"]
        for path in (A7S, A6300):
            b = _data(path)
            for item in s:
                interior = item["text"][len("[MOUNT_DEBUG]: "):].encode("latin1")
                assert b"\x00" + interior + b"\x00" not in b, (path, item["vaddr"])

    def test_dos_falsos_positivos_por_subcadena(self):
        s = _summary()["differential"]
        assert s["a7s_interior_substring"] == 2
        assert s["a6300_interior_substring"] == 2
        assert [x["vaddr"] for x in s["substring_false_positives"]] == [
            "0x43c966a8", "0x43c98a29"]
        for path in (A7S, A6300):
            b = _data(path)
            assert b"[BL]Wait_BL_ASYNC_RCV (%+hd)" in b
            assert b"SaveUsr:POFF Req" in b

    def test_cifras_del_json(self):
        d = _summary()["differential"]
        assert d["a6000_strings"] == 132
        assert d["a7s_with_prefix"] == 0
        assert d["a6300_with_prefix"] == 0
        assert d["a7s_interior_exact"] == 0
        assert d["a6300_interior_exact"] == 0
        for k, v in (("[MOUNT_", 223), ("[MOUNT_DEBUG", 132),
                     ("[MOUNT_ERROR", 80), ("[MOUNT_INFO", 6),
                     ("[MOUNT_WARNING", 5)):
            assert d["prefix_tokens"][k] == {"a6000": v, "a7s": 0, "a6300": 0}

    def test_mecanismo_preexistente(self):
        d = _summary()["differential"]["preexisting"]
        for k, v in (("Mount_DividedInfo.cpp", (5, 3, 4)),
                     ("Mount_Controller.cpp", (1, 2, 1)),
                     ("/mnt/Mount_ms_log_%03d.dat", (1, 1, 1)),
                     ("LENS DETACH", (2, 1, 1)),
                     ("Eclipse", (13, 6, 6))):
            assert (d[k]["a6000"], d[k]["a7s"], d[k]["a6300"]) == v, k
            if k == "Eclipse":
                # 13 cadenas [MOUNT_*] (7 DEBUG + 6 ERROR) contienen Eclipse y
                # hay 14 apariciones literales: la 14a es "InitializeEclipse"
                # dentro de 0x43c97802.
                ecl = []
                for pref in (b"[MOUNT_DEBUG]: ", b"[MOUNT_ERROR]: ",
                             b"[MOUNT_INFO]: ", b"[MOUNT_WARNING]: "):
                    ecl.extend(t for _, t in _strings(prefix=pref) if "Eclipse" in t)
                assert len(ecl) == 13
                assert sum(1 for t in ecl if t.startswith("[MOUNT_DEBUG]")) == 7
                assert DATA.count(b"Eclipse") == 14


class TestPuentesSinTrazas:
    def test_0x4377e0e8(self):
        assert _u16(0x4377E0E8) == 0xE92D
        assert _bl_target(0x4377E0F0) == 0x436E8328
        assert _u16(0x4377E21E) == 0xF5A2      # sub.w r3,r2,#0xc00
        assert _u16(0x4377E220) == 0x6340
        assert _u16(0x4377E22C) == 0xE8DF      # tbb [pc,r3]
        assert _u16(0x4377E22E) == 0xF003

    def test_0x437d24c8(self):
        assert _u16(0x437D24C8) == 0xE92D
        assert _bl_target(0x437D24F2) == 0x436E97A8

    def test_ninguno_contiene_sitios_del_mapa(self):
        sitios = {int(x["site"], 16) for item in _summary()["strings"]
                  for x in item["sites"]}
        assert not [a for a in sitios if 0x4377E0E8 <= a < 0x4377F000]
        assert not [a for a in sitios if 0x437D24C8 <= a < 0x437D3000]
