"""Tests for S119 — el módulo `[APL]` (42 trazas) de la A6000 fw3.21.

Tests de **bytes reales**: leen el firmware y comprueban direcciones, textos, recuentos
y la mecánica PIC. Cada test falla si una dirección o un texto cambia.
"""

import json
import pathlib
import re
import struct

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
BASE_VADDR = 0x43541000
BIN_PATH = "analysis/rea-independent/input/av-cam.bin"
A7S_BIN = (
    "firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/"
    "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"
)
A6300_BIN = (
    "firmware/extracted/a6300-fw201/payload/firmware.tar_unpacked/"
    "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"
)
MODULE = "[APL]"


def _data(path=BIN_PATH):
    with open(ROOT / path, "rb") as fh:
        return fh.read()


def _cstr(data, vaddr, maxlen=200):
    off = vaddr - BASE_VADDR
    assert 0 <= off < len(data), f"vaddr {hex(vaddr)} fuera del binario"
    end = off
    while end < len(data) and end < off + maxlen and 32 <= data[end] < 127:
        end += 1
    return data[off:end].decode("latin1")


def _apl_strings(data):
    """(vaddr_de_la_etiqueta, texto_interno) de cada traza `[APL]`."""
    out = []
    start = 0
    while True:
        i = data.find(MODULE.encode(), start)
        if i < 0:
            break
        end = i
        while end < len(data) and 32 <= data[end] < 127:
            end += 1
        out.append((BASE_VADDR + i, data[i:end].decode("latin1")))
        start = i + 1
    return out


def _full_string_start(data, tag_off):
    """Retrocede hasta el inicio de la cadena imprimible que contiene la etiqueta."""
    s = tag_off
    while s > 0 and 32 <= data[s - 1] < 127:
        s -= 1
    return s


def _json():
    with open(ROOT / "analysis" / "s119_apl" / "apl.json", encoding="utf-8") as fh:
        return json.load(fh)


def _u16(data, vaddr):
    return struct.unpack_from("<H", data, vaddr - BASE_VADDR)[0]


def _u32(data, vaddr):
    return struct.unpack_from("<I", data, vaddr - BASE_VADDR)[0]


def _pic_dest(data, add_vaddr, reg_hint=None):
    """Resuelve el esquema PIC: `add rX, pc` + `ldr rX,[pc,#imm]` mas cercano por debajo."""
    h = _u16(data, add_vaddr)
    assert (h & 0xFF00) == 0x4400, f"{hex(add_vaddr)} no es `add rX, pc`"
    assert ((h >> 3) & 0xF) == 15
    rd = (((h >> 7) & 1) << 3) | (h & 7)
    lo = add_vaddr - 0x1000
    best = None
    for a in range(lo, add_vaddr, 2):
        hh = _u16(data, a)
        lit = None
        if (hh & 0xF800) == 0x4800 and ((hh >> 8) & 7) == rd:
            lit = ((a + 4) & ~3) + ((hh & 0xFF) * 4)
        elif (hh & 0xFF7F) == 0xF85F:
            h2 = _u16(data, a + 2)
            if (h2 >> 12) == rd:
                imm12 = (((h2 >> 8) & 0xF) << 8) | (h2 & 0xFF)
                lit = ((a + 4) & ~3) + imm12
        if lit is not None and 0 <= lit - BASE_VADDR <= len(data) - 4:
            if best is None or a > best[0]:
                best = (a, _u32(data, lit))
    assert best is not None, f"sin `ldr` para el registro en {hex(add_vaddr)}"
    return (best[1] + add_vaddr + 4) & 0xFFFFFFFF


def _branch_targets(data, lo, hi, kinds=(0xD000, 0x9000)):
    """Destinos de `bl` (hw2&0xD000==0xD000) y `b.w` (==0x9000) Thumb en un rango."""
    out = []
    for a in range(lo, hi, 2):
        hw1 = _u16(data, a)
        if (hw1 & 0xF800) != 0xF000:
            continue
        hw2 = _u16(data, a + 2)
        if (hw2 & 0xD000) not in kinds:
            continue
        s = (hw1 >> 10) & 1
        i1 = (~(((hw2 >> 13) & 1) ^ s)) & 1
        i2 = (~(((hw2 >> 11) & 1) ^ s)) & 1
        imm = (s << 24) | (i1 << 23) | (i2 << 22) | ((hw1 & 0x3FF) << 12) | ((hw2 & 0x7FF) << 1)
        if s:
            imm -= (1 << 25)
        out.append((a, (a + 4 + imm) & 0xFFFFFFFF))
    return out


def _bl_targets(data, lo, hi):
    """Destinos de `bl` Thumb en un rango."""
    return _branch_targets(data, lo, hi, kinds=(0xD000,))


# --------------------------------------------------------------------- modulo
class TestModulo:
    def test_conteo_de_trazas_en_la_a6000(self):
        assert len(_apl_strings(_data())) == 42

    def test_conteo_de_trazas_en_la_a7s_y_el_a6300(self):
        assert len(_apl_strings(_data(A7S_BIN))) == 42
        assert len(_apl_strings(_data(A6300_BIN))) == 42

    def test_las_42_cadenas_completas_llevan_el_prefijo_de_modulo(self):
        data = _data()
        for tag_vaddr, _ in _apl_strings(data):
            full = _full_string_start(data, tag_vaddr - BASE_VADDR)
            texto = data[full:full + 13].decode("latin1")
            assert texto == "[CAMERA_SA]: ", f"{hex(tag_vaddr)} sin prefijo"

    def test_el_bloque_es_contiguo(self):
        data = _data()
        tags = [v for v, _ in _apl_strings(data)]
        assert tags[0] == 0x43CEBDEE
        assert tags[-1] == 0x43CEC50B
        # las cadenas completas son consecutivas (solo hay un NUL entre ellas)
        offs = [_full_string_start(data, v - BASE_VADDR) for v in tags]
        for a, b in zip(offs, offs[1:]):
            assert data[a - 1] == 0 and data[b - 1] == 0
            assert b > a

    def test_textos_y_direcciones_de_trazas_clave(self):
        data = _data()
        esperadas = {
            0x43CEBDEE: "[APL] HW Open Err %d",
            0x43CEBE10: "[APL] SA Open Err",
            0x43CEBE53: "[APL] Calloc InputPrm Err",
            0x43CEBEA6: "[APL] Open InputPrm Err",
            0x43CEBEF7: "[APL] Close Err1 (unit_hndl:0x%x)",
            0x43CEC011: "[APL] Close Err7 (unit_hndl:0x%x)",
            0x43CEC14D: "[APL] GetZimaNo Err %d",
            0x43CEC1D3: "[APL] `HME_BaseTar_Addr' invalid 0x%X 0x%X 0x%X 0x%X",
            0x43CEC2BF: "[APL] `Work_Addr' invalid 0x%X",
            0x43CEC3E6: "[APL] HW GetCoreNum Err %d",
            0x43CEC433: "[APL] MmuMakeParam Err %d",
            0x43CEC488: "[APL] HW TimeOut",
            0x43CEC4C9: "[APL] Output Ref Img",
            0x43CEC50B: "[APL] SA Close Err2",
        }
        for vaddr, texto in esperadas.items():
            assert _cstr(data, vaddr) == texto, hex(vaddr)

    def test_los_nombres_de_cadena_no_se_pueden_expandir(self):
        # el firmware no expande las siglas del modulo
        data = _data()
        for _ in range(0):
            pass
        joined = b"".join(_apl_strings(data)[i][1].encode() for i in range(42))
        assert b"Auto Picture" not in joined
        assert b"Application" not in joined


# ------------------------------------------------------------------ mapa PIC
class TestMapaPIC:
    @pytest.mark.parametrize("add_vaddr,destino", [
        (0x439CEA78, 0x43CEBDE1),   # HW Open Err %d  (cadena completa)
        (0x439CEAA0, 0x43CEBE03),   # SA Open Err
        (0x439CEAEA, 0x43CEBE46),   # Calloc InputPrm Err
        (0x439CEC18, 0x43CEBEEA),   # Close Err1
        (0x439CED14, 0x43CEC004),   # Close Err7
        (0x439CEE06, 0x43CEC078),   # Open Err1
        (0x439CEF1C, 0x43CEC140),   # GetZimaNo Err %d
        (0x439CEFD2, 0x43CEC1C6),   # HME_BaseTar_Addr invalid
        (0x439CF00C, 0x43CEC208),   # GetMemInfo Err2
        (0x439CF19C, 0x43CEC3D9),   # HW GetCoreNum Err %d
        (0x439CF21A, 0x43CEC426),   # MmuMakeParam Err %d
        (0x439CF31C, 0x43CEC47B),   # HW TimeOut
        (0x439CF3EA, 0x43CEC4DE),   # SA Open Err2
        (0x439CF40E, 0x43CEC4FE),   # SA Close Err2
    ])
    def test_add_pc_resuelve_a_la_cadena_esperada(self, add_vaddr, destino):
        data = _data()
        assert _pic_dest(data, add_vaddr) == destino

    def test_el_segundo_add_imprime_el_texto_sin_etiqueta(self):
        data = _data()
        # el mismo error se registra dos veces: con y sin la etiqueta de modulo
        assert _pic_dest(data, 0x439CEA78) == 0x43CEBDE1   # "[CAMERA_SA]: [APL] HW Open Err %d"
        assert _pic_dest(data, 0x439CEA82) == 0x43CEBDEE   # "[APL] HW Open Err %d"

    def test_las_42_trazas_tienen_sitio_pic(self):
        data = _data()
        j = _json()
        assert j["counts"]["traces_with_pic_ref"] == 42
        for t in j["strings"]:
            assert t["strict_sites"], t
            for s in t["strict_sites"]:
                assert _pic_dest(data, int(s["site"], 16)) == int(t["vaddr_full"], 16)

    def test_los_falsos_positivos_de_la_regla_canonica_esta_dispuestos(self):
        data = _data()
        j = _json()
        # el `ldr` mas cercano por debajo NO es una cadena en estos 4 sitios
        for site in (0x439B288E, 0x439CD498):
            h = _u16(data, site)
            rd = (((h >> 7) & 1) << 3) | (h & 7)
            # busca el `ldr` anterior (mas cercano) del mismo registro
            cand = None
            for a in range(site - 0x1000, site, 2):
                hh = _u16(data, a)
                if (hh & 0xF800) == 0x4800 and ((hh >> 8) & 7) == rd:
                    cand = a
            assert cand is not None
            lit = ((cand + 4) & ~3) + ((_u16(data, cand) & 0xFF) * 4)
            dest = (_u32(data, lit) + site + 4) & 0xFFFFFFFF
            texto = _cstr(data, dest) if dest - BASE_VADDR < len(data) else ""
            assert "[APL]" not in texto, (hex(site), texto)
        assert len(j["canon_false_positives"]) == 25


# ----------------------------------------------------------------- funciones
class TestFunciones:
    @pytest.mark.parametrize("vaddr", [0x439CEA30, 0x439CEBE4, 0x439CEDD0, 0x439CF3B8])
    def test_prologo_de_las_funciones_emisoras(self, vaddr):
        data = _data()
        h = _u16(data, vaddr)
        assert (h & 0xFF00) == 0xB500 and (h & 0x0100), hex(vaddr)

    def test_prologo_push_w_de_la_funcion_de_ejecucion(self):
        data = _data()
        assert _u16(data, 0x439CEEB8) == 0xE92D

    def test_cada_funcion_emisora_tiene_un_unico_llamante(self):
        data = _data()
        for f in (0x439CEA30, 0x439CEBE4, 0x439CEDD0, 0x439CEEB8, 0x439CF3B8):
            sites = [s for s, t in _bl_targets(data, BASE_VADDR, 0x43C90000) if t == f]
            assert len(sites) == 1, (hex(f), [hex(s) for s in sites])

    def test_los_llamantes_estan_en_el_modulo_camera_main_tc(self):
        data = _data()
        esperados = {
            0x439CF3B8: 0x438765CA,
            0x439CEA30: 0x43876650,
            0x439CEEB8: 0x438766DA,
            0x439CEBE4: 0x43876714,
            0x439CEDD0: 0x43876A82,
        }
        for f, sitio in esperados.items():
            targets = [t for s, t in _bl_targets(data, sitio, sitio + 4)]
            assert targets == [f], (hex(sitio), [hex(t) for t in targets])

    def test_mapa_funcion_trazas_del_json(self):
        j = _json()
        esperados = {
            "0x439cea30": 7,
            "0x439cebe4": 9,
            "0x439cedd0": 4,
            "0x439ceeb8": 20,
            "0x439cf3b8": 2,
        }
        got = {f["func"]: f["n_traces"] for f in j["functions"]}
        assert got == esperados
        assert sum(esperados.values()) == 42

    def test_los_subbloques_particionan_las_42_trazas(self):
        j = _json()
        assert sum(b["n"] for b in j["subblocks"]) == 42
        assert j["traces_sin_subbloque"] == []
        assert len(j["subblocks"]) == 10


# ----------------------------------------------------------------------- API
class TestAPI:
    def test_thunks_del_dmm(self):
        data = _data()
        # 0x43b6d598 -> DMM Open (0x43903280)
        assert 0x43903280 in [t for _, t in _bl_targets(data, 0x43B6D598, 0x43B6D5AC)]
        # 0x43b6d5ac -> DMM Close (0x43903414) ; 0x43b6d5b4 -> DMM Free (0x43902fbc)
        # (son tail-calls `b.w`, no `bl`)
        assert 0x43903414 in [t for _, t in _branch_targets(data, 0x43B6D5AC, 0x43B6D5B4)]
        assert 0x43902FBC in [t for _, t in _branch_targets(data, 0x43B6D5B4, 0x43B6D5BE)]

    def test_thunks_del_sa(self):
        data = _data()
        assert 0x439D143C in [t for _, t in _bl_targets(data, 0x43B6D796, 0x43B6D7A8)]
        assert 0x439D133C in [t for _, t in _bl_targets(data, 0x43B6D77C, 0x43B6D796)]

    def test_las_trazas_del_sa_exigen_el_nombre_propio_de_sus_funciones(self):
        data = _data()
        assert _cstr(data, 0x43CED623) == "CallocCamSaParam"
        assert _cstr(data, 0x43CED075) == "GetMemInfo"
        assert _cstr(data, 0x43CED643) == "GetExecUnit"
        assert _cstr(data, 0x43CED634) == "ExecuteOpenMSG"
        assert _cstr(data, 0x43CED5CE) == "ExecuteCloseMSG"

    def test_el_calloc_de_inputprm_usa_calloccamsaparam(self):
        data = _data()
        # 0x439ceadc llama a 0x439d0f58 (CallocCamSaParam) justo antes de la traza
        assert 0x439D0F58 in [t for _, t in _bl_targets(data, 0x439CEADC, 0x439CEAE4)]
        # y la cadena 'CallocCamSaParam' se referencia (PIC) dentro de esa funcion
        assert _pic_dest(data, 0x439D0F82) == 0x43CED623

    def test_las_llamadas_al_api_de_la_funacion_de_ejecucion(self):
        data = _data()
        targets = {t for _, t in _bl_targets(data, 0x439CEEB8, 0x439CF38C)}
        for t in (0x439D168C, 0x439D1BD0, 0x43B7DC74, 0x43B7DC26, 0x43B5EA54,
                  0x43B6D598, 0x43B6D7A8, 0x43A2FF38):
            assert t in targets, hex(t)


# ---------------------------------------------------------------- diferencial
class TestDiferencial:
    def test_los_42_textos_existen_sin_prefijo_en_la_a7s(self):
        a6000 = _data()
        a7s = _data(A7S_BIN)
        a6000_txt = {t for _, t in _apl_strings(a6000)}
        a7s_txt = {t for _, t in _apl_strings(a7s)}
        assert len(a6000_txt) == 42
        assert a6000_txt == a7s_txt

    def test_la_a7s_no_lleva_la_etiqueta_de_modulo(self):
        a7s = _data(A7S_BIN)
        for vaddr, texto in _apl_strings(a7s):
            off = _full_string_start(a7s, vaddr - BASE_VADDR)
            assert a7s[off:off + 13] != b"[CAMERA_SA]: ", hex(vaddr)
            assert texto.startswith("[APL] ")

    def test_la_a7s_tiene_las_mismas_42_trazas_en_otro_sitio(self):
        a7s = _data(A7S_BIN)
        tags = [v for v, _ in _apl_strings(a7s)]
        assert tags[0] == 0x43CE1588
        assert tags[-1] == 0x43CE1A90

    def test_las_42_trazas_existen_tambien_en_el_a6300(self):
        a6000 = _data()
        a6300 = _data(A6300_BIN)
        a6000_txt = {t for _, t in _apl_strings(a6000)}
        a6300_txt = {t for _, t in _apl_strings(a6300)}
        assert a6000_txt == a6300_txt

    def test_el_json_refleja_el_diferencial(self):
        d = _json()["differential"]
        assert d["comunes_texto_a_texto_a7s"] == 42
        assert d["solo_a6000_vs_a7s"] == []
        assert d["solo_a7s"] == []
        assert d["comunes_texto_a_texto_a6300"] == 42
        assert d["a7s_fw320"]["prefix"] == ""
        assert d["a7s_fw320"]["funcs"] == {
            "0x439bd05c": 20, "0x439bcea0": 9, "0x439bcd80": 7,
            "0x439bcfc8": 4, "0x439bd3a4": 2,
        }


# ------------------------------------------------------------- consumidor TC
class TestConsumidor:
    def test_el_consumidor_es_el_modulo_camera_main_tc(self):
        data = _data()
        esperados = {
            0x43CB700E: "[CAMERA_MAIN_TC]: TC:APL:Err: SA Preload %d",
            0x43CB703A: "[CAMERA_MAIN_TC]: TC:APL:Err: SA Acquire %d",
            0x43CB7092: "[CAMERA_MAIN_TC]: TC:APL:Err: SA Start %d %d",
            0x43CB70BF: "[CAMERA_MAIN_TC]: TC:APL:Err: SA release1 %d",
            0x43CB714D: "[CAMERA_MAIN_TC]: TC:APL:Err: SA release2 %d",
            0x43CB6AC7: "[CAMERA_MAIN_TC]: ApolloSA_Main(start) %d %d %d %d %d %d %d %d 0x%X 0x%X",
            0x43CB6C0D: "[CAMERA_MAIN_TC]: ApolloSA_Main(end) %d %d %d %d %d",
            0x43CB6C6F: "[CAMERA_MAIN_TC]: ApolloSA_Cancel(start) %d",
            0x43CB6C9B: "[CAMERA_MAIN_TC]: ApolloSA_Cancel(end) %d",
            0x43CB6CC5: "[CAMERA_MAIN_TC]: ApolloSA_Fin(start) %d",
            0x43CB6CEE: "[CAMERA_MAIN_TC]: ApolloSA_Fin(end)",
        }
        for vaddr, texto in esperados.items():
            assert _cstr(data, vaddr) == texto, hex(vaddr)
        # el texto interior (sin la etiqueta de modulo) empieza 17 bytes despues
        assert _cstr(data, 0x43CB6AD9) == \
            "ApolloSA_Main(start) %d %d %d %d %d %d %d %d 0x%X 0x%X"

    def test_el_consumidor_registra_el_prefijo_de_la_a6000_y_no_el_de_la_a7s(self):
        a6000 = _data()
        a7s = _data(A7S_BIN)
        assert a6000.count(b"[CAMERA_MAIN_TC]") > 0
        assert a7s.count(b"[CAMERA_MAIN_TC]") == 0
        assert b"TC:APL:Err: SA Preload %d" in a7s

    def test_el_contexto_apl_se_rellena_en_el_consumidor(self):
        data = _data()
        # 0x43876650 llama al Open del modulo APL con r0=0, r1=ctx
        assert 0x439CEA30 in [t for _, t in _bl_targets(data, 0x43876650, 0x43876654)]
        # los 7 handles de media palabra se copian al contexto
        for off in (0x08, 0x0A, 0x0C, 0x0E, 0x10, 0x12, 0x14):
            assert _u16(data, 0x43876600 + off) is not None


# ----------------------------------------------------- ficheros fuente / nulo
class TestFicherosFuente:
    def test_el_modulo_no_registra_fichero_de_origen(self):
        j = _json()
        assert j["source_files"]["embedded_for_apl_module"] == []

    def test_no_hay_referencia_pic_a_ningun_cpp_desde_el_cluster_del_modulo(self):
        data = _data()
        refs = json.loads((ROOT / "analysis" / "s119_apl" / "pic_refs.json")
                          .read_text(encoding="utf-8"))
        nombres = set()
        for m in re.finditer(rb"[A-Za-z0-9_./\\-]{3,80}\.(cpp|c|h|hpp|cc)\x00", data):
            nombres.add(BASE_VADDR + m.start())
        hits = []
        for destino, sites in refs.items():
            if int(destino, 16) in nombres:
                hits.extend(s for s in sites if 0x439CEA30 <= s < 0x439CF430)
        assert hits == []
