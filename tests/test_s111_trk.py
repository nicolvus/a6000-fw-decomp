"""Tests de S111 — módulo de trazas `[TRK]` del A6000 fw3.21.

Todos los tests son de **bytes reales**: leen el firmware, decodifican la pareja
PIC `ldr rX,[pc,#imm]` + `add rX, pc` y comprueban que el destino coincide con la
cadena citada. Además contrastan los agregados de `trk.json`/`refs.json`.
"""

import json
import pathlib
import struct

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
BASE_VADDR = 0x43541000
BIN_PATH = "analysis/rea-independent/input/av-cam.bin"
A7S_PATH = ("firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/"
            "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin")
TRK_DIR = ROOT / "analysis/s111_trk"


def _data(path=BIN_PATH):
    with open(ROOT / path, "rb") as fh:
        return fh.read()


def _off(vaddr):
    return vaddr - BASE_VADDR


def _u16(data, vaddr):
    off = _off(vaddr)
    assert 0 <= off <= len(data) - 2, f"vaddr {hex(vaddr)} fuera del binario"
    return struct.unpack_from("<H", data, off)[0]


def _u32(data, vaddr):
    off = _off(vaddr)
    assert 0 <= off <= len(data) - 4, f"vaddr {hex(vaddr)} fuera del binario"
    return struct.unpack_from("<I", data, off)[0]


def _cstr(data, vaddr, maxlen=200):
    off = _off(vaddr)
    assert 0 <= off < len(data), f"vaddr {hex(vaddr)} fuera del binario"
    end = off
    while end < len(data) and end < off + maxlen and 32 <= data[end] < 127:
        end += 1
    return data[off:end].decode("latin1")


def _runs(data, prefix=b"[TRK"):
    """(vaddr, texto) de cada ocurrencia del prefijo, en orden de fichero."""
    out = []
    start = 0
    while True:
        i = data.find(prefix, start)
        if i < 0:
            break
        v = BASE_VADDR + i
        out.append((v, _cstr(data, v)))
        start = i + 1
    return out


def _decode_pic(data, ldr, site):
    """Decodifica ldr+add y devuelve (registro, destino) sin mirar el JSON."""
    h = _u16(data, ldr)
    if (h & 0xF800) == 0x4800:              # ldr rT,[pc,#imm5*4]
        reg = (h >> 8) & 7
        lit = ((ldr + 4) & ~3) + (h & 0xFF) * 4
    elif (h & 0xFF7F) == 0xF85F:            # ldr.w rT,[pc,#imm12]
        h2 = _u16(data, ldr + 2)
        reg = (h2 >> 12) & 0xF
        lit = ((ldr + 4) & ~3) + ((((h2 >> 8) & 0xF) << 8) | (h2 & 0xFF))
    else:
        raise AssertionError(f"ldr desconocido en {hex(ldr)}: {hex(h)}")
    ha = _u16(data, site)
    assert (ha & 0xFF00) == 0x4400, f"no es add en {hex(site)}: {hex(ha)}"
    assert ((ha >> 3) & 0xF) == 15, f"add sin pc en {hex(site)}"
    reg_add = (((ha >> 7) & 1) << 3) | (ha & 7)
    assert reg_add == reg, f"registro distinto en {hex(site)}"
    destino = (_u32(data, lit) + (site + 4)) & 0xFFFFFFFF
    return reg, destino


def _refs_json():
    with open(TRK_DIR / "refs.json") as fh:
        return json.load(fh)


def _trk_json():
    with open(TRK_DIR / "trk.json") as fh:
        return json.load(fh)


class TestCadenas:
    def test_ocurrencias_y_cadenas_distintas(self):
        data = _data()
        runs = _runs(data)
        assert len(runs) == 216
        refs = _refs_json()
        assert len(refs["strings"]) == 215          # inicios de cadena
        assert len({t for _v, t in runs}) == 208    # incluye el 2.º prefijo
        assert len({r["text"] for r in refs["strings"]}) == 207

    def test_ocho_textos_stk_repetidos(self):
        with open(TRK_DIR / "refs.json") as fh:
            rows = json.load(fh)["strings"]
        repetidos = {}
        for row in rows:
            repetidos.setdefault(row["text"], []).append(row["vaddr"])
        dobles = {t: v for t, v in repetidos.items() if len(v) == 2}
        assert len(dobles) == 8
        assert all(t.startswith("[TRK]: [STK] PARAM ERR - box ") for t in dobles)

    def test_rango_de_cadenas(self):
        runs = sorted(_runs(_data()))
        assert runs[0][0] == 0x43CEBCEB
        assert runs[-1][0] == 0x43CFE31C

    def test_unica_cadena_con_dos_prefijos(self):
        data = _data()
        dobles = [(v, t) for v, t in _runs(data) if t.count("[TRK") > 1]
        assert dobles == [(0x43CFDA0E, "[TRK]: [TRK] cb_func == NULL")]
        assert _cstr(data, 0x43CFDA0E) == "[TRK]: [TRK] cb_func == NULL"

    def test_cadenas_concretas(self):
        data = _data()
        esperados = {
            0x43CEBCEB: "[TRK]: [CAM INIT] Message Alloc Error",
            0x43CEBD60: "[TRK]: [VSYNC CLOSE] Message Alloc Error",
            0x43CFB304: "[TRK]: [DETSA] CORE2 RESOURCE CONTENTION : %d",
            0x43CFB479: "[TRK]: [EDTSA] CORE3 RESOURCE CONTENTION : %d",
            0x43CFC45F: "[TRK]: [IRO2G] ALIGNMENT ERR : %d",
            0x43CFC6E6: "[TRK]: [PMV] Param Affine_err_thresh ERR : %d, %d",
            0x43CFC810: "[TRK]: [STK] Saliency CB is NULL (COMP)",
            0x43CFCF09: "[TRK]: [STK] PARAM ERR - box af_island_num : %d",
            0x43CFDA4D: "[TRK]: CAM MODE IS ALREADY OPEN!",
            0x43CFDF82: "[TRK]: [BT] fg_area : %d, %d, %d, %d",
            0x43CFE135: "[TRK]: [BT] cmn.af_rect_thres:%d",
            0x43CFE31C: "[TRK]: [BT] ddl_saCalcCancel:%d",
            0x43CFDB88: "[TRK]: osal_alloc_timer(): %d",
            0x43CFDCF8: "[TRK]: osal_can_timer(): %d",
        }
        for vaddr, texto in esperados.items():
            assert _cstr(data, vaddr) == texto, f"vaddr {hex(vaddr)}"

    def test_cadenas_sin_referencia(self):
        refs = _refs_json()
        sin = sorted(s["vaddr"] for s in refs["strings"] if not s["sites"])
        assert sin == ["0x43cfb3e9", "0x43cfc7ea"]
        textos = {s["vaddr"]: s["text"] for s in refs["strings"]}
        assert textos["0x43cfb3e9"] == "[TRK]: [EDTSA] Stop Message Alloc Error"
        assert textos["0x43cfc7ea"] == "[TRK]: [STK] Stop Message Alloc Error"


class TestReferenciasPIC:
    def test_recuentos(self):
        refs = _refs_json()
        assert refs["n_strings"] == 215
        assert refs["n_referenced"] == 213
        assert refs["n_sites"] == 288
        assert refs["n_sites_strict"] == 283
        assert refs["n_sites_relaxed"] == 5
        assert refs["n_sites_unowned"] == 0

    def test_los_288_sitios_recalculan_el_destino(self):
        data = _data()
        refs = _refs_json()
        vistos = 0
        for row in refs["strings"]:
            objetivo = int(row["vaddr"], 16)
            for o in row["refs"]:
                ldr = int(o["ldr"], 16)
                site = int(o["site"], 16)
                _reg, destino = _decode_pic(data, ldr, site)
                assert destino == objetivo, (
                    f"{row['text']!r}: {hex(site)} calcula {hex(destino)}"
                )
                vistos += 1
        assert vistos == 288

    def test_separacion_ldr_add(self):
        refs = _refs_json()
        gaps = []
        for row in refs["strings"]:
            for o in row["refs"]:
                gaps.append(int(o["site"], 16) - int(o["ldr"], 16))
        assert min(gaps) == 2
        assert max(gaps) == 14
        assert max(gaps) <= 0x40

    def test_af_rect_thres_no_sale_de_0x43a37c06(self):
        """La pasada amplia fabricaba esta referencia; el ldr real es 0x43a37c00."""
        data = _data()
        refs = _refs_json()
        fila = next(s for s in refs["strings"] if s["vaddr"] == "0x43cfe135")
        assert fila["sites"] == ["0x43a38720"]
        assert fila["funcs"] == ["0x43a380ac"]
        sitios = {o["site"] for s in refs["strings"] for o in s["refs"]}
        assert "0x43a37c06" not in sitios
        assert "0x43a3740e" in sitios
        # El add de 0x43a37c06 usa el ldr de 0x43a37c00 y calcula 0x43f61264,
        # una dirección de datos que no es ninguna cadena [TRK].
        _reg, destino = _decode_pic(data, 0x43A37C00, 0x43A37C06)
        assert destino == 0x43F61264
        fila_ref = fila["refs"][0]
        assert fila_ref["ldr"] == "0x43a3871c"
        _reg, destino = _decode_pic(data, 0x43A3871C, 0x43A38720)
        assert destino == 0x43CFE135

    def test_funciones_dominantes(self):
        trk = _trk_json()
        por_inicio = {f["start"]: f for f in trk["functions"]}
        assert len(por_inicio) == 47
        assert por_inicio["0x43a36a06"]["n_strings"] == 53
        assert por_inicio["0x43a36a06"]["n_sites"] == 53
        assert por_inicio["0x43a3588e"]["n_strings"] == 48
        assert por_inicio["0x43a36156"]["n_strings"] == 45
        assert por_inicio["0x43a380ac"]["n_strings"] == 34
        assert por_inicio["0x43a380ac"]["n_sites"] == 38
        assert por_inicio["0x43a3059c"]["n_sites"] == 16
        assert por_inicio["0x43a34f5c"]["n_strings"] == 13
        assert por_inicio["0x43a347d8"]["n_strings"] == 8
        assert por_inicio["0x43a301e4"]["n_strings"] == 6

    def test_relaxed_y_fin_no_verificado(self):
        trk = _trk_json()
        rel = trk["relaxed"]
        assert len(rel) == 5
        assert {r["func"] for r in rel} == {"0x43a375d8", "0x43a37ea4"}
        por_inicio = {f["start"]: f for f in trk["functions"]}
        assert por_inicio["0x43a375d8"]["end"] is None
        assert por_inicio["0x43a37ea4"]["end"] is None


class TestEstructura:
    def test_sub_bloques_suman_215_y_288(self):
        trk = _trk_json()
        bloques = {b["name"]: b for b in trk["blocks"]}
        assert len(bloques) == 17
        assert sum(b["n_strings"] for b in bloques.values()) == 215
        assert sum(b["n_sites"] for b in bloques.values()) == 288
        assert bloques["STK"]["n_strings"] == 76
        assert bloques["STK"]["n_sites"] == 145
        assert bloques["BT"]["n_sites"] == 48
        assert bloques["EDTSA"]["n_strings"] == 19
        assert bloques["PMV"]["n_strings"] == 16
        assert bloques["IRO2G"]["n_strings"] == 13
        assert bloques["DETSA"]["n_strings"] == 9

    def test_zonas(self):
        trk = _trk_json()
        zonas = {z["name"]: z for z in trk["zones"]}
        assert zonas["trk_face"]["n_sites"] == 284
        assert zonas["trk_face"]["n_functions"] == 43
        assert zonas["apl_sa"]["n_sites"] == 4
        for nombre in ("sa_stubs", "fc", "apl_osal"):
            assert zonas[nombre]["n_sites"] == 0, nombre
            assert zonas[nombre]["n_functions"] == 0, nombre

    def test_ficheros_fuente(self):
        trk = _trk_json()
        fuentes = {s["file"]: s["vaddr"] for s in trk["sources"]}
        assert len(fuentes) == 99
        assert fuentes["FC/Api/fc_api_tracking.cpp"] == "0x43cefa43"
        assert fuentes["FC/Drv/fc_drv_bt.cpp"] == "0x43cf603a"
        assert fuentes["FC/Drv/fc_drv_stk.cpp"] == "0x43cf627a"
        assert fuentes["FC/Drv/fc_drv_pmv.cpp"] == "0x43cf707a"
        assert fuentes["FC/Drv/fc_drv_detsa.cpp"] == "0x43cf03fa"
        assert fuentes["FC/Alg/fc_alg_tracking.cpp"] == "0x43cf0472"


class TestDiferencialA7S:
    def test_a7s_mismas_cadenas_y_misma_estructura(self):
        ruta = ROOT / A7S_PATH
        if not ruta.exists():
            pytest.skip("blob de la A7S no disponible")
        with open(ruta, "rb") as fh:
            a7s = fh.read()
        runs_a6 = _runs(_data())
        runs_a7 = _runs(a7s)
        assert len(runs_a6) == len(runs_a7) == 216
        assert sorted(t for _v, t in runs_a6) == sorted(t for _v, t in runs_a7)
        assert sorted(_v for _v, _t in runs_a7)[0] == 0x43CE1492
        assert sorted(_v for _v, _t in runs_a7)[-1] == 0x43CEE615

        with open(TRK_DIR / "a7s_diff.json") as fh:
            diff = json.load(fh)
        assert diff["a6000"]["n_sites"] == diff["a7s"]["n_sites"] == 288
        assert diff["a6000"]["n_functions"] == diff["a7s"]["n_functions"] == 47
        assert diff["a6000"]["n_sites_strict"] == 283
        assert diff["a6000"]["n_sites_relaxed"] == 5
        assert diff["a7s"]["n_sites_strict"] == 284
        assert diff["a7s"]["n_sites_relaxed"] == 4
        assert diff["identical_texts"] is True
        assert diff["identical_multiset"] is True
        assert diff["only_a6000"] == []
        assert diff["only_a7s"] == []


class TestJSON:
    def test_esquema_del_hito(self):
        trk = _trk_json()
        assert trk["milestone"] == "S111"
        assert trk["module"] == "TRK"
        assert trk["base_vaddr"] == "0x43541000"
        assert trk["counts"]["n_occurrences"] == 216
        assert trk["counts"]["n_strings"] == 215
        assert trk["counts"]["n_sites"] == 288
        assert trk["counts"]["n_functions"] == 47
        assert trk["string_range"] == {"lo": "0x43cebceb", "hi": "0x43cfe31c"}
