"""Tests for S127 — `[CAMERA_MAIN_LC]`, el motor de AF de `Camera::LC` (72 trazas).

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
PREFIX = b"[CAMERA_MAIN_LC]:"
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
    with open(ROOT / "analysis" / "s127_camera_main_lc" / "camera_main_lc.json",
              encoding="utf-8") as fh:
        return json.load(fh)


def _strings(data=None):
    """(vaddr, texto) de cada cadena que empieza por el prefijo, en orden."""
    data = DATA if data is None else data
    out = []
    start = 0
    while True:
        i = data.find(PREFIX, start)
        if i < 0:
            break
        end = i
        while end < len(data) and data[end] != 0:
            end += 1
        out.append((BASE + i, data[i:end].decode("latin1")))
        start = i + 1
    return out


class TestCadenas:
    def test_conteo_y_rango(self):
        s = _strings()
        assert len(s) == 72
        assert s[0][0] == 0x43C9C6F6
        assert s[-1][0] == 0x43CA7E0B

    def test_el_json_lista_las_mismas_72(self):
        s = _summary()
        assert s["counts"]["strings"] == 72
        assert [int(x["vaddr"], 16) for x in s["strings"]] == [v for v, _ in _strings()]
        assert [x["text"] for x in s["strings"]] == [t for _, t in _strings()]

    def test_cada_cadena_esta_en_su_vaddr_y_termina_en_nul(self):
        s = _summary()
        for item in s["strings"]:
            v = int(item["vaddr"], 16)
            assert _cstr(v) == item["text"], hex(v)
            fin = v - BASE + len(item["text"].encode("latin1"))
            assert DATA[fin] == 0, f"{hex(v)} sin NUL final"
            assert item["text"].startswith("[CAMERA_MAIN_LC]: "), hex(v)

    def test_reparto_32_40(self):
        s = _summary()
        primero = [x for x in s["strings"] if int(x["vaddr"], 16) <= 0x43C9D646]
        segundo = [x for x in s["strings"] if int(x["vaddr"], 16) >= 0x43CA71FA]
        assert (len(primero), len(segundo)) == (32, 40)
        assert len(primero) + len(segundo) == 72
        assert primero[0]["vaddr"] == "0x43c9c6f6"
        assert primero[-1]["vaddr"] == "0x43c9d646"
        assert segundo[0]["vaddr"] == "0x43ca71fa"
        assert segundo[-1]["vaddr"] == "0x43ca7e0b"
        bloques = s["counts"]["string_blocks"]
        assert [b["strings"] for b in bloques] == [32, 40]
        assert [b["sites"] for b in bloques] == [37, 41]

    def test_sub_bloques_suman_72(self):
        s = _summary()
        assert len(s["sub_blocks"]) == 13
        assert sum(b["strings_first_site"] for b in s["sub_blocks"]) == 72

    def test_una_sola_cadena_sin_referencia(self):
        s = _summary()
        muertas = [x for x in s["strings"] if not x["sites"]]
        assert len(muertas) == 1
        assert muertas[0]["vaddr"] == "0x43c9c779"
        assert s["unreferenced"][0]["vaddr"] == "0x43c9c779"
        assert _cstr(0x43C9C779) == muertas[0]["text"]


class TestSitios:
    def _ldrs(self, lo, hi):
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

    def test_los_78_sitios_resuelven_su_cadena(self):
        s = _summary()
        total = 0
        for item in s["strings"]:
            v = int(item["vaddr"], 16)
            for sitio in item["sites"]:
                a = int(sitio["site"], 16)
                assert self._resolver(a) == v, f"{hex(a)} no apunta a {hex(v)}"
                total += 1
        assert total == 78

    def test_sitios_ordenados_y_suma_por_funcion(self):
        s = _summary()
        assert s["counts"]["sites"] == 78
        assert sum(f["site_count"] for f in s["functions"]) == 78
        assert len({x["site"] for item in s["strings"] for x in item["sites"]}) == 78


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

    def test_37_funciones_con_prologo_thumb(self):
        s = _summary()
        assert s["counts"]["functions"] == 37
        assert len(s["functions"]) == 37
        for f in s["functions"]:
            a = int(f["vaddr"], 16)
            assert self._es_prologo_push_lr(a), f"{hex(a)} sin push con lr"

    def test_frontera_corregida_de_0x4373c7f8(self):
        # La función empieza en el `ldr r3,[pc,#0x34]`, no en el push de +2.
        assert _u16(0x4373C7F8) == 0x4B0D
        assert _u16(0x4373C7FA) == 0xB510
        # lo anterior es cola/pool de la función previa, no un prólogo de esta
        assert _u16(0x4373C7F6) == 0x0055
        assert self._es_prologo_push_lr(0x4373C7F8)
        vaddrs = {f["vaddr"] for f in _summary()["functions"]}
        assert "0x4373c7f8" in vaddrs

    def test_sitios_de_cada_funcion_pertenecen_a_sus_cadenas(self):
        s = _summary()
        por_func = {f["vaddr"]: f for f in s["functions"]}
        for item in s["strings"]:
            for sitio in item["sites"]:
                f = por_func[sitio["func"]]
                assert sitio["site"] in f["sites"], (hex(int(sitio["site"], 16)), f["vaddr"])
                assert item["vaddr"] in f["string_vaddrs"]


class TestZpd:
    FUNC = 0x437C1E48

    def test_gate_ldrb_tst_beq(self):
        assert _u16(0x437C1E5A) == 0xF893      # ldrb.w
        assert _u16(0x437C1E5C) == 0x30C0      # r3,[r3,#0xc0]
        assert _u16(0x437C1E5E) == 0xF013      # tst.w
        assert _u16(0x437C1E60) == 0x0F02      # r3,#2
        assert (_u16(0x437C1E64) & 0xFF00) == 0xD000   # beq
        assert _u16(self.FUNC) == 0xB5F7       # push {r0,r1,r2,r4,r5,r6,r7,lr}
        assert _u16(self.FUNC + 2) == 0x4607   # mov r7,r0  -> full_count = 1er argumento

    def test_layout_leido_instruccion_a_instruccion(self):
        # (site, encoding esperado, Rn, offset) — ldr.w/ldrb.w con base r4.
        esperado = [
            (0x437C1E7A, 0x6823, None, 0x000),   # ldr r3,[r4]  buffer_user_id
            (0x437C1E8C, 0xF8D4, 4, 0x3C4),      # zpd_flags
            (0x437C1E98, 0xF8D4, 4, 0x3C8),      # defocus
            (0x437C1EA6, 0xF8D4, 4, 0x3CC),      # selected_ym
            (0x437C1EB2, 0xF8D4, 4, 0x3D0),      # selected_contrast
            (0x437C1EC0, 0xF8D4, 4, 0xCE4),      # base_defocus
            (0x437C1ED4, 0xF8D4, 4, 0xCE8),      # zaf_now_shut_cycle
            (0x437C1EE8, 0xF8D4, 4, 0xCEC),      # iris_cur
            (0x437C1EFC, 0xF894, 4, 0xCF0),      # select_area (byte)
            (0x437C1F10, 0xF894, 4, 0xCF1),      # mario_use_ng_flag (byte)
        ]
        for site, enc, rn, off in esperado:
            h = _u16(site)
            if enc == 0x6823:
                assert h == 0x6823, hex(site)
                continue
            assert h == enc, (hex(site), hex(h))
            assert (h & 0xF) == rn, hex(site)
            h2 = _u16(site + 2)
            assert (h2 >> 12) == 3, hex(site)          # Rt = r3
            assert (h2 & 0xFFF) == off, (hex(site), hex(h2 & 0xFFF))

    def test_el_json_declara_el_layout_medido(self):
        s = _summary()["zpd"]
        assert s["dump_function"] == "0x437c1e48"
        assert s["caller"] == "0x439d9d82"
        offsets = [x["offset"] for x in s["layout"]]
        assert offsets == ["[r4]+0x00", "+0x3c4", "+0x3c8", "+0x3cc", "+0x3d0",
                           "+0xce4", "+0xce8", "+0xcec", "+0xcf0", "+0xcf1"]
        assert s["read_sites"] == [
            "0x437c1e7a", "0x437c1e8c", "0x437c1e98", "0x437c1ea6", "0x437c1eb2",
            "0x437c1ec0", "0x437c1ed4", "0x437c1ee8", "0x437c1efc", "0x437c1f10",
        ]
        assert len(s["string_sites"]) == 10
        # los 10 sitios son add rX,pc de esta función y resuelven a sus 10 cadenas
        zpd = next(b for b in _summary()["sub_blocks"] if b["id"] == "zpd_result")
        assert zpd["strings_first_site"] == 10
        assert zpd["functions"] == ["0x437c1e48"]


class TestLlamadores:
    @staticmethod
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

    def test_bl_medidos(self):
        pares = {
            0x43738FE0: 0x4373C7F8,   # calibration_fc_pos -> getSaIfAddr
            0x4374A938: 0x43754BE0,   # -> lc_HybridAF
            0x4374A93C: 0x43545CD0,   # -> volcado scan/predict
            0x437CE2CE: 0x437CDE1C,   # -> zpd_HybridMovieAF_reset
            0x4373F51C: 0x43754BE0,
            0x4373F6B6: 0x43754BE0,
            0x4376D830: 0x43754BE0,
            0x4373FBEC: 0x4373F45C,
            0x4373FEA0: 0x4373F45C,
            0x439D9D82: 0x437C1E48,   # -> LC_GetZpdResultInfo
        }
        for site, destino in pares.items():
            assert self._bl_target(site) == destino, hex(site)

    def test_llamadores_declarados_en_el_json(self):
        s = _summary()
        por_func = {f["vaddr"]: f for f in s["functions"]}
        assert set(por_func["0x43754be0"]["bl_callers"]) == {
            "0x4373f51c", "0x4373f6b6", "0x4374a938", "0x4376d830"
        }
        for f in s["functions"]:
            for caller in f["bl_callers"]:
                assert self._bl_target(int(caller, 16)) == int(f["vaddr"], 16)


class TestCadenaMuerta:
    @staticmethod
    def _is_string_start(addr):
        off = addr - BASE
        if not (0 <= off < len(DATA)):
            return False
        if not (32 <= DATA[off] < 127):
            return False
        return off == 0 or not (32 <= DATA[off - 1] < 127)

    @classmethod
    def _scan_strict(cls, lo, hi):
        """Regla estricta canónica (scan_pic_refs_strict.py) sobre el rango de código."""
        unpack = U16S.unpack_from
        ldrs, adds = [], []
        a = lo
        while a < hi:
            h = unpack(DATA, a - BASE)[0]
            if (h & 0xF800) == 0x4800:
                lit = ((a + 4) & ~3) + ((h & 0xFF) * 4)
                if BASE <= lit <= BASE + len(DATA) - 4:
                    ldrs.append((a, (h >> 8) & 7, _u32(lit)))
            elif (h & 0xFF7F) == 0xF85F:
                h2 = unpack(DATA, a + 2 - BASE)[0]
                lit = ((a + 4) & ~3) + ((((h2 >> 8) & 0xF) << 8) | (h2 & 0xFF))
                if BASE <= lit <= BASE + len(DATA) - 4:
                    ldrs.append((a, (h2 >> 12) & 0xF, _u32(lit)))
            if (h & 0xFF00) == 0x4400 and ((h >> 3) & 0xF) == 15:
                adds.append((a, (((h >> 7) & 1) << 3) | (h & 7)))
            a += 2
        por_reg = {}
        for a, reg, w in ldrs:
            por_reg.setdefault(reg, []).append((a, w))
        for v in por_reg.values():
            v.sort()
        claves = {r: [x[0] for x in v] for r, v in por_reg.items()}
        res = {}
        for a, reg in adds:
            ks = claves.get(reg)
            if not ks:
                continue
            i = bisect.bisect_left(ks, a) - 1
            if i < 0:
                continue
            la, w = por_reg[reg][i]
            if a - la > MAX_LDR_GAP:
                continue
            tgt = (w + (a + 4)) & 0xFFFFFFFF
            if cls._is_string_start(tgt):
                res.setdefault(tgt, []).append(a)
        return res

    def test_la_cadena_muerta_no_tiene_ningun_sitio_estricto(self):
        res = self._scan_strict(CODE_LO, CODE_HI)
        assert 0x43C9C779 not in res
        # control: el escáner sí encuentra las demás del mismo bloque
        vivo = next(x for x in _summary()["strings"] if x["sites"])
        assert int(vivo["vaddr"], 16) in res
        assert len(res[int(vivo["vaddr"], 16)]) == len(vivo["sites"])

    def test_la_cadena_muerta_es_una_cadena_real(self):
        assert _cstr(0x43C9C779).startswith("[CAMERA_MAIN_LC]: [ERROR!!]")
        assert DATA[0x43C9C779 - BASE - 1] == 0


class TestDiferencial:
    def test_la_etiqueta_es_nueva_en_la_fw321(self):
        for path in (A7S, A6300):
            b = _data(path)
            assert b.count(PREFIX) == 0, path
            assert b.count(b"[CAMERA_MAIN_LC]") == 0, path

    def test_ningun_mensaje_interior_es_cadena_independiente(self):
        s = _summary()["strings"]
        for path in (A7S, A6300):
            b = _data(path)
            for item in s:
                interior = item["text"][len("[CAMERA_MAIN_LC]: "):].encode("latin1")
                independiente = b"\x00" + interior + b"\x00"
                assert independiente not in b, (path, item["vaddr"])

    def test_matiz_de_los_asteriscos(self):
        # `************` sí existe como subcadena en A7S/A6300, pero no como cadena propia.
        for path in (A7S, A6300):
            b = _data(path)
            assert b"************" in b
            assert b"\x00************\x00" not in b
        assert _cstr(0x43C9D03E) == "[CAMERA_MAIN_LC]: ************"
        assert _cstr(0x43C9D03E).endswith("************")

    def test_cifras_del_json(self):
        d = _summary()["differential"]
        assert d["a6000_strings"] == 72
        assert d["a7s_with_prefix"] == 0
        assert d["a6300_with_prefix"] == 0
        assert d["a7s_interior_exact"] == 0
        assert d["a6300_interior_exact"] == 0
