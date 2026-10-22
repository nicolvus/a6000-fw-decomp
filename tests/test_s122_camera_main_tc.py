"""Tests for S122 — el módulo `[CAMERA_MAIN_TC]` (127 trazas) de la A6000 fw3.21.

Tests de **bytes reales**: leen el firmware y comprueban direcciones, textos, recuentos,
la mecánica PIC, el despacho, los llamadores y el diferencial A7S/A6300. Cada test falla
si una dirección, un texto o una instrucción cambia.
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
MODULE = "[CAMERA_MAIN_TC]"
PREFIX = "[CAMERA_MAIN_TC]: "
PRINTF_LOCAL = 0x43902718


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


def _u16(data, vaddr):
    return struct.unpack_from("<H", data, vaddr - BASE_VADDR)[0]


def _u32(data, vaddr):
    return struct.unpack_from("<I", data, vaddr - BASE_VADDR)[0]


def _json():
    with open(
        ROOT / "analysis" / "s122_camera_main_tc" / "camera_main_tc.json", encoding="utf-8"
    ) as fh:
        return json.load(fh)


def _full_string_start(data, off):
    """Retrocede hasta el inicio de la cadena imprimible que contiene `off`."""
    s = off
    while s > 0 and 32 <= data[s - 1] < 127:
        s -= 1
    return s


def _module_strings(data):
    """(vaddr_etiqueta, vaddr_inicio_cadena, texto_interior, texto_completo) por traza."""
    out = []
    start = 0
    while True:
        i = data.find(MODULE.encode(), start)
        if i < 0:
            break
        full = _full_string_start(data, i)
        end = i
        while end < len(data) and 32 <= data[end] < 127:
            end += 1
        out.append(
            (
                BASE_VADDR + i,
                BASE_VADDR + full,
                data[i + len(MODULE) + 2:end].decode("latin1"),
                data[full:end].decode("latin1"),
            )
        )
        start = i + 1
    return out


def _branch_targets(data, lo, hi, kinds=(0xD000, 0x9000)):
    """Destinos de `bl` (hw2&0xD000==0xD000) y `b.w` (==0x9000) Thumb en un rango.

    Los candidatos se localizan por byte alto 0xF0..0xF7 (condición `hw1 & 0xF800 == 0xF000`).
    """
    out = []
    for m in re.finditer(rb"[\xf0-\xf7]", data):
        o = m.start() - 1
        if o < 0 or o & 1 or o + 3 >= len(data):
            continue
        a = BASE_VADDR + o
        if not (lo <= a < hi):
            continue
        hw1 = data[o] | (data[o + 1] << 8)
        if (hw1 & 0xF800) != 0xF000:
            continue
        hw2 = data[o + 2] | (data[o + 3] << 8)
        if (hw2 & 0xD000) not in kinds:
            continue
        s = (hw1 >> 10) & 1
        i1 = (~(((hw2 >> 13) & 1) ^ s)) & 1
        i2 = (~(((hw2 >> 11) & 1) ^ s)) & 1
        imm = (
            (s << 24)
            | (i1 << 23)
            | (i2 << 22)
            | ((hw1 & 0x3FF) << 12)
            | ((hw2 & 0x7FF) << 1)
        )
        if s:
            imm -= 1 << 25
        out.append((a, (a + 4 + imm) & 0xFFFFFFFF))
    return out


def _bl_targets(data, lo, hi):
    """Destinos de `bl` Thumb en un rango."""
    return _branch_targets(data, lo, hi, kinds=(0xD000,))


def _pic_dest(data, add_vaddr):
    """Resuelve el esquema PIC: `add rX, pc` + `ldr rX,[pc,#imm]` mas cercano por debajo.

    Es la regla estricta canónica (`analysis/s106_imaging_cap/scan_pic_refs_strict.py`).
    """
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


# --------------------------------------------------------------------- modulo
class TestModulo:
    def test_conteo_de_trazas_y_token(self):
        data = _data()
        assert data.count(MODULE.encode()) == 127
        assert len(_module_strings(data)) == 127

    def test_las_127_trazas_son_distintas_y_conservan_el_prefijo(self):
        data = _data()
        trazas = _module_strings(data)
        assert len({t[2] for t in trazas}) == 127
        assert len({t[3] for t in trazas}) == 127
        for _, _, _, completo in trazas:
            assert MODULE + ": " in completo, completo

    def test_extremos_y_los_seis_tramos(self):
        j = _json()
        bloques = j["subblocks_content"]
        assert len(bloques) == 6
        assert bloques[0]["lo"] == "0x43ca7fd7"
        assert bloques[-1]["hi"] == "0x43ccb350"
        # tramos ordenados, disjuntos y no contiguos
        for a, b in zip(bloques, bloques[1:]):
            assert int(a["hi"], 16) < int(b["lo"], 16)
            assert int(b["lo"], 16) - int(a["hi"], 16) > 1
        assert sum(b["n"] for b in bloques) == 127
        assert sum(b["sites"] for b in bloques) == 256
        assert sum(b["referenced"] for b in bloques) == 123
        assert sum(len(b["functions"]) for b in bloques) == 41

    def test_textos_clave(self):
        data = _data()
        esperadas = {
            0x43CB6AC7: "[CAMERA_MAIN_TC]: ApolloSA_Main(start) %d %d %d %d %d %d %d %d 0x%X 0x%X",
            0x43CB6B10: "[CAMERA_MAIN_TC]: APL_MEM_INFO 0x%X 0x%X 0x%X 0x%X 0x%X 0x%X 0x%X 0x%X",
            0x43CB6B57: "[CAMERA_MAIN_TC]: APL_IMG_INFO %d %d %d %d %d %d %d",
            0x43CB6B8B: "[CAMERA_MAIN_TC]: APL_PANORAMA_INFO %d %d %d %d 0x%X 0x%X %d 0x%X 0x%X 0x%X 0x%X",
            0x43CB6BDC: "[CAMERA_MAIN_TC]: TC:APL Err: ChkExeSeq %d %d %d",
            0x43CB6C0D: "[CAMERA_MAIN_TC]: ApolloSA_Main(end) %d %d %d %d %d",
            0x43CB6C41: "[CAMERA_MAIN_TC]: TC:APL:Err: ChkPrm %d %d %d",
            0x43CB6A93: "[CAMERA_MAIN_TC]: TC:APL:Err: MakerNote:GetTagPt %d",
            0x43CCB350: "[CAMERA_MAIN_TC]: JudgeBdroRslt %d %d %d %d %d %d %d %d %d %d",
        }
        for vaddr, texto in esperadas.items():
            assert _cstr(data, vaddr) == texto, hex(vaddr)

    def test_los_tres_casos_especiales(self):
        data = _data()
        # idx 0: la cadena esta precedida por los bytes imprimibles "<20"
        assert _cstr(data, 0x43CA7FD4) == "<20[CAMERA_MAIN_TC]: GyroStitScl %d %d"
        # idx 32: prefijo pegado " &08@" y texto real desde la etiqueta
        assert _cstr(data, 0x43CA8542) == (
            " &08@[CAMERA_MAIN_TC]: TC:DIST:Err:SetDistMode1ForSync aspect, %d"
        )
        assert _cstr(data, 0x43CA8547).startswith("[CAMERA_MAIN_TC]: TC:DIST:Err:SetDistMode1")
        # idx 105: unica traza sin texto interior: en vaddr+18 hay 0x0a, no texto
        assert _cstr(data, 0x43CB74CD) == "[CAMERA_MAIN_TC]: "
        assert _cstr(data, 0x43CB74DF) == ""
        assert data[0x43CB74DF - BASE_VADDR] == 0x0A
        assert _cstr(data, 0x43CB74DD) == ": "  # vaddr+16, parte de la etiqueta
        # el `ldr` de idx 0 se usa como tabla de bytes, no como formato
        assert _u16(data, 0x437D07C0) & 0xFE00 == 0x5C00  # ldrb r1,[r3,r2]


# ------------------------------------------------------------------ anatomia
class TestAnatomia:
    def test_cada_traza_se_emite_dos_veces(self):
        j = _json()
        assert j["counts"]["strings"] == 127
        assert j["counts"]["referenced"] == 123
        assert j["counts"]["dead"] == 4
        assert j["counts"]["sites"] == 256
        assert j["counts"]["functions"] == 41
        assert j["counts"]["traces_with_two_pointers"] == 122
        assert j["counts"]["refs_by_kind"] == {"string": 127, "prefix": 2, "inner": 127}

    def test_reparto_exacto_de_punteros_por_traza(self):
        j = _json()
        reparto = {}
        for s in j["strings"]:
            kinds = [r["kind"] for r in s["refs"]]
            clave = (kinds.count("string"), kinds.count("prefix"), kinds.count("inner"))
            reparto[clave] = reparto.get(clave, 0) + 1
        assert reparto == {
            (1, 0, 1): 115,
            (2, 0, 2): 5,
            (0, 0, 0): 4,
            (1, 1, 1): 1,
            (0, 1, 1): 1,
            (1, 0, 0): 1,
        }

    def test_el_texto_interior_vive_18_bytes_despues(self):
        data = _data()
        for s in _json()["strings"]:
            vaddr = int(s["vaddr"], 16)
            for ref in s["refs"]:
                dest = int(ref["dest"], 16)
                if ref["kind"] == "inner":
                    assert dest == vaddr + 18, (s["idx"], ref)
                elif ref["kind"] == "prefix":
                    assert dest == vaddr, (s["idx"], ref)
                else:
                    assert dest == int(s["vaddr_string"], 16), (s["idx"], ref)

    def test_las_cuatro_cadenas_muertas(self):
        data = _data()
        a7s = _data(A7S_BIN)
        a6300 = _data(A6300_BIN)
        j = _json()
        assert j["dead"]["count"] == 4
        muertas = {int(d["vaddr"], 16) for d in j["dead"]["strings"]}
        assert muertas == {0x43CB6C6F, 0x43CB6C9B, 0x43CB717A, 0x43CB71A5}
        for d in j["dead"]["strings"]:
            vaddr = int(d["vaddr"], 16)
            assert _cstr(data, vaddr) == d["text"]
            assert d["text"].encode() not in a7s
            assert d["text"].encode() not in a6300
        # ninguna de las 256 referencias PIC apunta a una muerta
        for s in j["strings"]:
            for ref in s["refs"]:
                assert int(ref["dest"], 16) not in muertas
        assert j["dead"]["evidence"]["absolute_pointers"] == 0
        assert j["dead"]["evidence"]["addw_pc"] == 0
        assert j["dead"]["evidence"]["movw_movt_pairs"] == 0


# ------------------------------------------------------------------ mapa PIC
class TestMapaPIC:
    def test_los_256_pares_pic_resuelven_al_destino(self):
        data = _data()
        sites = 0
        for s in _json()["strings"]:
            for ref in s["refs"]:
                sites += 1
                add = int(ref["add"], 16)
                assert _pic_dest(data, add) == int(ref["dest"], 16), (s["idx"], ref)
        assert sites == 256

    @pytest.mark.parametrize(
        "add_vaddr,destino,kind",
        [
            (0x437D07BE, 0x43CA7FD4, "string"),   # idx 0: tabla de bytes, no emite
            (0x437D1ADE, 0x43CA7FD7, "prefix"),   # idx 0: etiqueta
            (0x437D1AF0, 0x43CA7FE9, "inner"),    # idx 0: interior (+18)
            (0x437D71A2, 0x43CA8547, "prefix"),   # idx 32 (sin sitio `string`)
            (0x437D71B2, 0x43CA8559, "inner"),    # idx 32
            (0x4387715C, 0x43CB74CD, "string"),   # idx 105: sin interior
        ],
    )
    def test_casos_especiales_del_mapa(self, add_vaddr, destino, kind):
        data = _data()
        assert _pic_dest(data, add_vaddr) == destino
        j = _json()
        refs = [
            r
            for s in j["strings"]
            for r in s["refs"]
            if int(r["add"], 16) == add_vaddr
        ]
        assert len(refs) == 1
        assert refs[0]["kind"] == kind

    def test_la_tabla_de_bytes_de_idx_0_no_es_un_formato(self):
        data = _data()
        # `ldrb r1,[r3,r2]` inmediatamente despues del add del sitio 0x437d07be
        assert _u16(data, 0x437D07C0) == 0x5C99
        assert _u16(data, 0x437D07C0) & 0xFE00 == 0x5C00


# ------------------------------------------------------------------ emisores
class TestEmisores:
    def test_los_17_publicadores_comparten_prologo(self):
        data = _data()
        pubs = _json()["emitters"]["publishers"]
        assert len(pubs) == 17
        assert sum(p["sites"] for p in pubs) == 128
        for p in pubs:
            vaddr = int(p["address"], 16)
            assert _u16(data, vaddr) == 0xB408, hex(vaddr)  # push {r3}
            bls = _bl_targets(data, vaddr, vaddr + 0x40)
            assert bls, hex(vaddr)
            assert bls[0] == (vaddr + 0x1E, 0x435612D0), hex(vaddr)

    def test_lectura_estructural_de_los_256_sitios(self):
        j = _json()
        est = j["emitters"]["structural"]
        assert est["publisher"] == 128
        assert est["printf"] == 127
        assert est["no_emit"] == 1
        assert est["total"] == 256
        assert est["breakdown"] == {
            "publisher_string": 126,
            "publisher_prefix": 2,
            "printf_inner": 127,
            "no_emit_string_byte_table": 1,
        }

    def test_la_heuristica_es_solo_contraste(self):
        j = _json()["emitters"]
        h = j["heuristic"]
        assert (h["publisher"], h["printf"], h["other"], h["none"], h["total"]) == (
            128,
            115,
            9,
            4,
            256,
        )
        anom = j["anomalies"]
        assert [a["site"] for a in anom] == ["0x43876fcc", "0x43879274"]
        assert anom[0]["kind"] == "string" and anom[0]["heuristic"] == "printf"
        assert anom[1]["kind"] == "inner" and anom[1]["heuristic"] == "publisher"
        # los 13 `inner` sin primera llamada a printf alcanzan el printf local
        assert j["non_printf_inners_reaching_printf"]["indices"] == [
            0, 43, 45, 46, 60, 68, 72, 73, 74, 86, 87, 121, 124
        ]

    def test_los_dos_sitios_anomalos_se_consumen_donde_dice_el_informe(self):
        data = _data()
        # 0x43876fcc: el registro es `sb`, consumido en `0x43876ffe: mov r3,sb` -> `bl 0x43876c08`
        assert 0x43876C08 in [t for _, t in _bl_targets(data, 0x43876FFE, 0x43877008)]
        assert 0x43902718 in [t for _, t in _bl_targets(data, 0x43877004, 0x4387700C)]
        # 0x43879274: cola `b 0x43879296` (branch de 16 bits, no `b.w`) -> `bl 0x43902718`
        h = _u16(data, 0x43879276)
        assert h & 0xF800 == 0xE000, hex(h)
        imm = h & 0x7FF
        if imm & 0x400:
            imm -= 0x800
        assert (0x43879276 + 4 + (imm << 1)) == 0x43879296
        assert 0x43902718 in [t for _, t in _bl_targets(data, 0x43879296, 0x4387929C)]

    def test_el_publicador_de_apollosa_main_tiene_nueve_llamadas(self):
        data = _data()
        sitios = [s for s, t in _bl_targets(data, BASE_VADDR, 0x43C90000) if t == 0x43873004]
        assert len(sitios) == 9, [hex(s) for s in sitios]
        assert [s for s in sitios if 0x438730B0 <= s < 0x43873644] == [
            0x438731BA, 0x43873232, 0x43873286, 0x438732F2,
            0x438733B4, 0x43873580, 0x438735C2,
        ]
        assert [s for s in sitios if 0x43873644 <= s < 0x43873700] == [
            0x43873668, 0x43873690
        ]


# ------------------------------------------------------------------ despacho
class TestDespacho:
    def test_prologo_y_epilogo_de_apollosa_main(self):
        data = _data()
        assert data[0x438730B0 - BASE_VADDR: 0x438730B6 - BASE_VADDR].hex() == "2de9f04f9fb0"
        assert data[0x4387359E - BASE_VADDR: 0x438735A2 - BASE_VADDR].hex() == "bde8f08f"

    def test_tabla_tbb_de_chequeo_de_rango(self):
        data = _data()
        j = _json()["dispatch"]
        assert j["tbb"]["addr"] == "0x4387333e"
        assert data[0x4387333E - BASE_VADDR: 0x43873342 - BASE_VADDR].hex() == "dfe805f0"
        tabla = data[0x43873342 - BASE_VADDR: 0x43873342 - BASE_VADDR + 9]
        assert tabla.hex() == "05050914140d0f0d0f"
        assert j["tbb"]["table"] == tabla.hex()

    def test_tabla_tbh_de_nueve_casos(self):
        data = _data()
        j = _json()["dispatch"]
        assert data[0x4387348E - BASE_VADDR: 0x43873492 - BASE_VADDR].hex() == "dfe815f0"
        tabla = data[0x43873492 - BASE_VADDR: 0x43873492 - BASE_VADDR + 18]
        assert tabla.hex() == j["tbh"]["table"]
        entradas = [struct.unpack_from("<H", tabla, i)[0] for i in range(0, 18, 2)]
        destinos = [(0x43873492 + 2 * e) for e in entradas]
        assert destinos == [
            0x438734A4, 0x438734A4, 0x438734AE, 0x438735D8, 0x438734DC,
            0x438734BC, 0x438734CC, 0x438734BC, 0x438734CC,
        ]

    def test_la_convergencia_tbh_es_0x438735d8_y_el_bl_esta_en_0x438735e2(self):
        data = _data()
        j = _json()["dispatch"]
        assert j["convergence"]["addr"] == "0x438735d8"
        bls = _bl_targets(data, 0x438735D8, 0x43873600)
        assert bls == [(0x438735E2, 0x43872C94)], [hex(a) for a, _ in bls]
        # 0x438735d8 es a la vez destino del caso 3 de la tabla y union de las 5 ramas
        assert j["tbh"]["cases"]["3"]["target"] == "0x438735d8"
        casos = [int(c["target"], 16) for c in j["tbh"]["cases"].values()]
        assert sorted(set(casos)) == [0x438734A4, 0x438734AE, 0x438734BC,
                                      0x438734CC, 0x438734DC, 0x438735D8]

    def test_entradas_reales_dos_bytes_antes_del_push(self):
        data = _data()
        assert _u16(data, 0x43872C94) == 0x2802  # cmp r0,#2
        assert _u16(data, 0x43872C96) == 0xE92D  # push.w
        assert _u16(data, 0x43873644) == 0x4B16  # ldr r3,[pc,#0x58]
        assert _u16(data, 0x43873646) == 0xB537  # push {r0,r1,r2,r4,r5,lr}


# ---------------------------------------------------------------- llamadores
class TestLlamadores:
    def test_solo_dos_llamadores_de_apollosa_main(self):
        data = _data()
        sitios = [s for s, t in _bl_targets(data, BASE_VADDR, 0x43C90000) if t == 0x438730B0]
        assert sitios == [0x437F1324, 0x438BDEAC], [hex(s) for s in sitios]

    def test_la_cadena_de_la_panoramica(self):
        data = _data()
        assert _bl_targets(data, 0x437F1310, 0x437F1318) == [(0x437F1314, 0x43873644)]
        assert _bl_targets(data, 0x437F1320, 0x437F1328) == [(0x437F1324, 0x438730B0)]
        assert 0x43902718 in [t for _, t in _bl_targets(data, 0x437F1368, 0x437F136C)]
        assert _u16(data, 0x437F12F6) == 0x2F02  # cmp r7,#2

    def test_la_cadena_de_error_de_la_panoramica(self):
        data = _data()
        assert _cstr(data, 0x43CACF9C) == "[IMAGING_CAP]: ApolloSA_Main: err[0x%02x]"
        assert _cstr(data, 0x43CACF9B) == ""  # NUL: S105 citaba este byte por error
        assert _cstr(data, 0x43CACFAB) == "ApolloSA_Main: err[0x%02x]"
        assert _pic_dest(data, 0x437F135A) == 0x43CACF9C
        assert _pic_dest(data, 0x437F1366) == 0x43CACFAB

    def test_los_seis_clientes_de_apl(self):
        data = _data()
        esperados = {
            0x438765C8: 0x43873378,
            0x438765FC: 0x438733E6,
            0x4387668C: 0x43873418,
            0x43876A80: 0x4387352C,
            0x43876AB4: 0x4387343A,
            0x43876B74: 0x438734E8,
        }
        for func, sitio in esperados.items():
            sitios = [
                s for s, t in _bl_targets(data, BASE_VADDR, 0x43C90000) if t == func
            ]
            assert sitios == [sitio], (hex(func), [hex(s) for s in sitios])

    def test_las_funciones_de_los_bloques(self):
        j = _json()["callers"]
        assert j["calibration"] == {
            "function": "0x437d48e8",
            "sites": 52,
            "labels": 26,
            "caller": "0x438734e0 (caso 4 del tbh)",
        }
        assert j["judge_bdro_rslt"]["caller"] == "0x438734b6 (caso 2 del tbh)"
        assert j["smart_zoom"]["caller"] == "0x4354af32 (función 0x4354a678)"
        assert j["ddt"]["no_direct_callers"] == [
            "0x438786c4", "0x43879204", "0x438792dc", "0x4387938e"
        ]


# ---------------------------------------------------------------- diferencial
class TestDiferencial:
    def test_la_etiqueta_es_exclusiva_de_la_a6000(self):
        a7s = _data(A7S_BIN)
        a6300 = _data(A6300_BIN)
        assert a7s.count(MODULE.encode()) == 0
        assert a6300.count(MODULE.encode()) == 0
        assert _data().count(MODULE.encode()) == 127

    def test_los_126_textos_interiores_existen_en_las_dos_versiones(self):
        trazas = _module_strings(_data())
        a7s = _data(A7S_BIN)
        a6300 = _data(A6300_BIN)
        for data in (a7s, a6300):
            encontrados = 0
            for _, _, inner, _ in trazas:
                if not inner.strip():
                    assert inner == ""
                    continue
                if inner.encode() in data:
                    encontrados += 1
            assert encontrados == 126

    def test_los_sitios_de_dos_punteros_resuelven_en_ambas_versiones(self):
        j = _json()
        textos = {s["idx"]: s["text"] for s in j["strings"]}
        for ver, path in (("a7s_fw320", A7S_BIN), ("a6300_fw201", A6300_BIN)):
            data = _data(path)
            filas = j["differential"]["versions"][ver]
            assert [e["idx"] for e in filas["two_sites"]] == [46, 109, 110, 118]
            for e in filas["two_sites"]:
                inner = textos[e["idx"]].split("]: ", 1)[-1]
                off = data.find(inner.encode())
                assert off >= 0, (ver, e["idx"])
                literal = BASE_VADDR + off
                for sitio in e["sites"]:
                    assert _pic_dest(data, int(sitio, 16)) == literal, (ver, e["idx"], sitio)

    def test_cifras_del_diferencial(self):
        j = _json()["differential"]
        for ver in ("a7s_fw320", "a6300_fw201"):
            v = j["versions"][ver]
            assert v["token_camera_main_tc"] == 0
            assert v["texts_found"] == 126
            assert v["texts_ref_pic"] == 119
            assert v["pic_sites"] == 123
            assert v["sites_distribution"] == {"0": 8, "1": 115, "2": 4}
            assert [(e["idx"], e["a6000_publisher_sites"], e["other_sites"]) for e in v["lost_sites"]] == [
                (2, 1, 0),
                (32, 1, 0),
                (108, 2, 0),
            ]
            assert v["not_found"] == [
                {"idx": 105, "vaddr": "0x43cb74cd", "why": "texto interior vacío"}
            ]


# ------------------------------------------------------ vocabulario y cierre
class TestVocabulario:
    def test_no_hay_vocabulario_de_obturador(self):
        textos = " ".join(t[2] for t in _module_strings(_data()))
        for palabra in (
            "shut", "silent", "electro", "mech", "sensor", "exposure", "drive",
            "readout", "jpeg", "movie", "stc", "bracket", "sweep", "interval",
        ):
            assert palabra not in textos, palabra
        assert "S51 A/B/C = NO se mantiene" in _json()["vocabulary"]["shutter_line"]

    def test_vocabulario_presente(self):
        textos = " ".join(t[2] for t in _module_strings(_data()))
        for palabra in ("ApolloSA", "DDT", "TC:", "Dist", "Gmv", "Gyro", "Lmv", "Raw",
                        "PANORAMA", "Exif", "SMART ZOOM", "Judge", "Stit"):
            assert palabra in textos, palabra
        assert _json()["vocabulary"]["present"]["ApolloSA"] == 6

    def test_la_etiqueta_smart_zoom_no_es_stc(self):
        textos = "\n".join(t[2] for t in _module_strings(_data()))
        assert "STC" not in textos
        assert "SMART ZOOM" in textos
        j = _json()
        assert [b["name"] for b in j["subblocks_content"]][3] == "SMART ZOOM"


# ------------------------------------------------------------ coherencia JSON
class TestCierre:
    def test_el_json_es_coherente(self):
        j = _json()
        assert j["milestone"] == "S122"
        assert j["module"] == "CAMERA_MAIN_TC"
        assert j["base_vaddr"] == "0x43541000"
        assert j["firmware"]["bin"] == BIN_PATH
        assert j["firmware"]["size"] == len(_data())
        assert j["counts"]["sites"] == sum(len(s["sites"]) for s in j["strings"])
        assert len(j["functions"]) == 41
        assert sum(f["n"] for f in j["functions"]) == 256
        assert len(j["not_verified"]) == 8
        assert j["rule"]["file"] == "analysis/s106_imaging_cap/scan_pic_refs_strict.py"
        assert (ROOT / j["rule"]["file"]).is_file()
