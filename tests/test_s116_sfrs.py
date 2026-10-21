"""Tests for S116 — `[SFRS]` (módulo de 117 trazas en A6000 fw3.21).

Tests de **bytes reales**: leen el firmware y comprueban direcciones, textos, instrucciones y
recuentos. No abren REA/Ghidra ni ejecutan firmware.
"""

import importlib.util
import json
import pathlib
import struct

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
BASE_VADDR = 0x43541000
BIN_PATH = "analysis/rea-independent/input/av-cam.bin"
A7S_BIN = (
    "firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/"
    "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"
)
SFRS_DIR = ROOT / "analysis" / "s116_sfrs"
CODE_LO = 0x439A0000
CODE_HI = 0x439C0000

_cache = {}


def _load(name):
    if name not in _cache:
        path = SFRS_DIR / f"{name}.json"
        with open(path, encoding="utf-8") as fh:
            _cache[name] = json.load(fh)
    return _cache[name]


def _data():
    return _load("__bin__") if "__bin__" in _cache else _read_bin()


def _read_bin():
    with open(ROOT / BIN_PATH, "rb") as fh:
        _cache["__bin__"] = fh.read()
    return _cache["__bin__"]


def _u16(data, vaddr):
    return struct.unpack_from("<H", data, vaddr - BASE_VADDR)[0]


def _u32(data, vaddr):
    return struct.unpack_from("<I", data, vaddr - BASE_VADDR)[0]


def _cstr(data, vaddr, maxlen=200):
    off = vaddr - BASE_VADDR
    assert 0 <= off < len(data), f"vaddr {vaddr:#x} fuera del binario"
    end = off
    while end < len(data) and end < off + maxlen and 32 <= data[end] < 127:
        end += 1
    return data[off:end].decode("latin1")


def _ldr_literal(data, addr):
    """Palabra que carga un `ldr rX,[pc,#imm]` (formas T1 de 16 bits y T2 de 32 bits)."""
    h = _u16(data, addr)
    if (h & 0xF800) == 0x4800:
        lit = ((addr + 4) & ~3) + (h & 0xFF) * 4
        return _u32(data, lit)
    if (h & 0xFF7F) == 0xF85F:
        h2 = _u16(data, addr + 2)
        imm = (((h2 >> 8) & 0xF) << 8) | (h2 & 0xFF)
        lit = ((addr + 4) & ~3) + imm
        return _u32(data, lit)
    raise AssertionError(f"{addr:#x}: no es un ldr PC-relativo ({h:#06x})")


def _scan_sfrs():
    spec = importlib.util.spec_from_file_location("scan_sfrs", SFRS_DIR / "scan_sfrs.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class TestCadenas:
    def test_117_cadenas(self):
        data = _data()
        assert data.count(b"[SFRS]") == 117
        assert len(_load("strings_raw")["strings"]) == 117

    def test_toda_aparicion_inicia_racha_imprimible(self):
        data = _data()
        start = 0
        while True:
            i = data.find(b"[SFRS]", start)
            if i < 0:
                break
            assert i == 0 or not (32 <= data[i - 1] < 127), f"{BASE_VADDR + i:#x}"
            start = i + 1

    def test_rango(self):
        strings = _load("strings_raw")["strings"]
        assert strings[0]["vaddr"] == "0x43ce7661"
        assert strings[-1]["vaddr"] == "0x43ceb8c4"

    def test_cadenas_clave_en_su_direccion(self):
        data = _data()
        esperados = {
            0x43CE7661: "[SFRS]RC_CALLBACK result:0x%x",
            0x43CE767F: "[SFRS][ERR]ERR at CtSetAicParam",
            0x43CE78EC: "[SFRS]SendExecTrigger TriggerType 0x%02x",
            0x43CE8CDE: "[SFRS][DEBUG][SETPIN] YccOut(false): file=%s line=%d",
            0x43CE8D2F: "[SFRS][DEBUG][GETPIN] ReqYccAsap(true): file=%s line=%d",
            0x43CE9407: "[SFRS][ERR][PINSEND]  ERROR!!: file=%s line=%d",
            0x43CE9436: "[SFRS][ERROR][PINSEND]  ERROR!!: file=%s line=%d",
            0x43CE962D: "[SFRS][PINSEND]  YC FREE at async task: file=%s line=%d",
            0x43CE97F4: "[SFRS] ***SA_ACK",
            0x43CE9AB9: "[SFRS][CMD] ***SET_PATH(0x%02x)***",
            0x43CEA29B: "[SFRS][INFO] ***SEND_MSG_TO_EXECUTER, cateID:0x%x msgID:0x%x err:0x%x",
            0x43CEAB13: "[SFRS]MultiplexTriggerExecuterActivate",
            0x43CEACB8: "[SFRS] ***SET_PATH_SUPERSTABLEMOVIE::Initialize_SaOpen",
            0x43CEB80D: ("[SFRS][ERR] ***SUPERSTABLEMOVIE_EXECUTE_PIN_SEND, "
                         "dataContent:0x%x, dataPlacement:0x%x, dataTransfer:0x%x, "
                         "scanline:0x%x"),
            0x43CEB8C4: "[SFRS][ERR] ***SUPERSTABLEMOVIE_VFXOUTPUTMEM_FREE_FAILED, 0x%x",
        }
        for vaddr, texto in esperados.items():
            assert _cstr(data, vaddr) == texto, hex(vaddr)

    def test_cadenas_vecinas_no_etiquetadas_no_cuentan(self):
        strings = {s["vaddr"] for s in _load("strings_raw")["strings"]}
        for vaddr in ("0x43ceb4ca", "0x43ceb4ec", "0x43ceb534", "0x43ceb58b"):
            assert vaddr not in strings

    def test_etiquetas_internas(self):
        textos = [s["text"] for s in _load("strings_raw")["strings"]]
        assert sum(1 for t in textos if t.startswith("[SFRS][ERR]")) == 54
        assert sum(1 for t in textos if t.startswith("[SFRS][CMP]")) == 13
        assert sum(1 for t in textos if "file=%s line=%d" in t) == 9


class TestSubBloques:
    def test_ocho_bloques_que_suman_117(self):
        bloques = {b["name"]: b["count"] for b in _load("sfrs")["sub_blocks"]}
        assert bloques == {
            "SUPERSTABLEMOVIE": 37,
            "MOTIONSHOTVIDEO": 25,
            "EFFECTMOVIEREC": 23,
            "PINSEND": 12,
            "SET_PATH_STATUS": 9,
            "SA": 6,
            "RC_AIC_TRIGGER": 3,
            "MULTIPLEXTRIGGER": 2,
        }
        assert sum(bloques.values()) == 117

    def test_rangos_de_los_bloques(self):
        bloques = {b["name"]: b for b in _load("sfrs")["sub_blocks"]}
        assert bloques["SUPERSTABLEMOVIE"]["first_vaddr"] == "0x43ceabc3"
        assert bloques["SUPERSTABLEMOVIE"]["last_vaddr"] == "0x43ceb8c4"
        assert bloques["MOTIONSHOTVIDEO"]["first_vaddr"] == "0x43ce99ab"
        assert bloques["PINSEND"]["first_vaddr"] == "0x43ce8cde"
        assert bloques["RC_AIC_TRIGGER"]["first_vaddr"] == "0x43ce7661"


class TestPuntosDeEmision:
    def test_131_sitios_todos_en_el_cluster(self):
        refs = _load("pic_refs_sfrs")
        sitios = [int(a, 16) for v in refs.values() for _, a in v]
        assert len(sitios) == 131
        assert min(sitios) == 0x439A6DC8
        assert max(sitios) == 0x439B2034
        assert all(CODE_LO <= s < CODE_HI for s in sitios)

    def test_formula_pc_sin_alinear_en_los_131_sitios(self):
        data = _data()
        refs = _load("pic_refs_sfrs")
        for vaddr, pares in refs.items():
            for ldr, add in pares:
                la, aa = int(ldr, 16), int(add, 16)
                assert la < aa <= la + 0x20, f"{ldr} -> {add}"
                w = _ldr_literal(data, la)
                assert (w + aa + 4) & 0xFFFFFFFF == int(vaddr, 16), (ldr, add, vaddr)
                assert _cstr(data, int(vaddr, 16)).startswith("[SFRS]")

    def test_variante_alineada_seria_erronea(self):
        data = _data()
        refs = _load("pic_refs_sfrs")
        for vaddr, add_hex, literal in (
            ("0x43ce8cde", 0x439AADC2, 0x33DF18),
            ("0x43ce8d2f", 0x439AAE4E, 0x33DEDD),
        ):
            alineado = (literal + ((add_hex + 4) & ~3)) & 0xFFFFFFFF
            sin_alinear = (literal + add_hex + 4) & 0xFFFFFFFF
            assert sin_alinear == int(vaddr, 16)
            assert alineado == int(vaddr, 16) - 2
            assert _cstr(data, alineado) != _cstr(data, int(vaddr, 16))
            assert vaddr in refs

    def test_cadena_repetida_y_dos_sitios_en_la_misma_funcion(self):
        refs = _load("pic_refs_sfrs")
        assert len(refs["0x43ce9436"]) == 7
        assert len(refs["0x43ce9407"]) == 3
        assert len(refs["0x43ce9a69"]) == 3
        assert [a for _, a in refs["0x43ce767f"]] == ["0x439a6e16", "0x439a6e78"]
        # 3 sitios `add` para 0x43ce9407, pero solo 2 funciones los contienen
        mapa = _load("func_map")["functions"]
        duenas = {f["func"] for f in mapa
                  if any(s["vaddr"] == "0x43ce9407" for s in f["strings"])}
        assert duenas == {"0x439ab7fc", "0x439ac742"}


class TestFunciones:
    def test_52_funciones_y_131_atribuciones(self):
        s = _load("sfrs")
        assert s["counts"] == {
            "strings": 117,
            "add_sites": 131,
            "functions": 52,
            "unreferenced_strings": 0,
            "strings_with_more_than_one_function": 3,
        }
        assert sum(f["refs"] for f in s["functions"]) == 131

    def test_funciones_con_mas_trazas(self):
        fmap = {f["func"]: f for f in _load("func_map")["functions"]}
        assert len(fmap) == 52
        assert fmap["0x439b07c2"]["refs"] == 15
        assert fmap["0x439b0f16"]["refs"] == 9
        assert fmap["0x439aec00"]["refs"] == 9
        assert fmap["0x439aec00"]["strings"][0]["vaddr"] == "0x43ce9f11"
        assert fmap["0x439b1cb2"]["refs"] == 7
        assert {s["vaddr"] for s in fmap["0x439b1cb2"]["strings"]} >= {
            "0x43ceb6d7", "0x43ceb80d", "0x43ceb8c4"}

    def test_rastro_de_funcion_dentro_del_cluster(self):
        s = _load("sfrs")
        assert s["ranges"]["functions"] == ["0x439a6be8", "0x439b1cb2"]


class TestEvidenciaDeBytes:
    def test_setpin_compara_con_1_y_registra_linea_58(self):
        data = _data()
        assert _u16(data, 0x439AADA2) & 0xF800 == 0x6800        # ldr r1,[r0,#0x10]
        assert _u16(data, 0x439AADA4) == 0x2901                  # cmp r1,#1
        assert _u16(data, 0x439AADA6) == 0xD104                  # bne 0x439aadb2
        assert _u16(data, 0x439AADB4) == 0x2100                  # movs r1,#0
        assert _u16(data, 0x439AADC0) == 0x223A                  # movs r2,#0x3a (58)
        assert (0x33DF18 + (0x439AADC2 + 4)) == 0x43CE8CDE
        assert (0x33DF4B + (0x439AADC4 + 4)) == 0x43CE8D13
        assert _cstr(data, 0x43CE8D13) == "SystemCmdAsyncCmdSetPin.cpp"
        assert _ldr_literal(data, 0x439AADBC) == 0x33DF18
        assert _ldr_literal(data, 0x439AADBE) == 0x33DF4B

    def test_getpin_compara_con_1_y_registra_linea_56(self):
        data = _data()
        assert _u16(data, 0x439AAE3C) == 0x2901                  # cmp r1,#1
        assert _u16(data, 0x439AAE3E) == 0xD10B                  # bne 0x439aae58
        assert _u16(data, 0x439AAE4C) == 0x2238                  # movs r2,#0x38 (56)
        assert (0x33DEDD + (0x439AAE4E + 4)) == 0x43CE8D2F
        assert (0x33DF13 + (0x439AAE50 + 4)) == 0x43CE8D67
        assert _cstr(data, 0x43CE8D67) == "SystemCmdAsyncGetPin.cpp"

    def test_execute_pin_send_lee_cuatro_campos_del_mismo_objeto(self):
        data = _data()
        # ldrb.w r2,[r4,#0x3f5] / ldrb.w r1,[r4,#0x3f6] / ldrb.w r3,[r4,#0x3f4]
        # ldrb.w r0,[r4,#0x3ff]
        for addr, imm12 in ((0x439B1F4C, 0x3F5), (0x439B1F50, 0x3F6),
                            (0x439B1F5A, 0x3F4), (0x439B1F62, 0x3FF)):
            assert _u16(data, addr) == 0xF894, hex(addr)
            assert _u16(data, addr + 2) & 0xFFF == imm12, hex(addr)
        assert _u16(data, 0x439B1F56) == 0xF8C4                  # str.w r3,[r4,#0x410]
        # ldr r0,[pc,#0x108] en 0x439b1f68; el `add r0,pc` está en 0x439b1f6a,
        # luego el PC que se suma es 0x439b1f6e (sin alinear).
        assert (0x43CEB80D - (0x439B1F6A + 4)) == _ldr_literal(data, 0x439B1F68)
        assert (0x43CEB80D - (0x439B1F68 + 4)) == _ldr_literal(data, 0x439B1F68) + 2


class TestFicherosFuente:
    def test_24_ficheros_y_sin_nombres_repetidos(self):
        s = _load("sfrs")
        assert len(s["source_files"]) == 24
        data = _data()
        nombres = []
        i = 0
        while i < len(data):
            if 32 <= data[i] < 127:
                e = i
                while e < len(data) and 32 <= data[e] < 127:
                    e += 1
                txt = data[i:e].decode("latin1")
                if txt.endswith(".cpp") and " " not in txt and len(txt) < 120:
                    nombres.append(txt)
                i = e
            else:
                i += 1
        assert len(nombres) == 573
        assert len(set(nombres)) == 573

    def test_ficheros_con_traza_asociada(self):
        s = _load("sfrs")
        por_nombre = {f["name"]: f for f in s["source_files"]}
        assert por_nombre["SystemCmdPinSend.cpp"]["vaddr"] == "0x43c843ac"
        assert len(por_nombre["SystemCmdPinSend.cpp"]["sfrs_cluster_functions"]) == 9
        assert por_nombre["SystemCmdAsyncCmdSetPin.cpp"]["vaddr"] == "0x43ce8d13"
        assert por_nombre["SystemCmdAsyncGetPin.cpp"]["vaddr"] == "0x43ce8d67"
        assert por_nombre["ScalarInfraSuperStableMovieManager.cpp"]["vaddr"] == "0x43ceb0aa"


class TestDiferencialA7S:
    def test_normalizacion_de_especificadores(self):
        mod = _scan_sfrs()
        assert mod.norm("%04d") == "%"
        assert mod.norm("nowVfc:0x%x") == mod.norm("nowVfc:0x%08x")
        assert mod.norm("nowVfc:0x%x") == "nowVfc:0x%"
        assert mod.norm("[SFRS][DEBUG] NowVfc=%d") == mod.norm("[SFRS][DEBUG] NowVfc=%02d")
        assert mod.norm("sin formato") == "sin formato"

    def test_diferencial_151_117_0_34(self):
        ruta = ROOT / A7S_BIN
        if not ruta.exists():
            pytest.skip("blob de la A7S no disponible")
        s = _load("sfrs")
        d = s["differential_a7s"]
        assert d["a7s_strings"] == 151
        assert d["common"] == 117
        assert d["a6000_only"] == 0
        assert d["a7s_only"] == 34
        assert len(d["a7s_only_texts"]) == 34
        assert any("AUDIO" in t for t in d["a7s_only_texts"])
        assert any("TransPathAudio" in t for t in d["a7s_only_texts"])
        assert not any(t.startswith("[SFRS]") is False for t in d["a7s_only_texts"])

    def test_a7s_contiene_las_117_de_a6000(self):
        ruta = ROOT / A7S_BIN
        if not ruta.exists():
            pytest.skip("blob de la A7S no disponible")
        mod = _scan_sfrs()
        a7s = ruta.read_bytes()
        a7s_textos = {mod.norm(s["text"]) for s in mod.sfrs_strings(a7s)}
        with open(ROOT / BIN_PATH, "rb") as fh:
            a6000_textos = [s["text"] for s in mod.sfrs_strings(fh.read())]
        assert len(a6000_textos) == 117
        faltan = [t for t in a6000_textos if mod.norm(t) not in a7s_textos]
        assert faltan == []
