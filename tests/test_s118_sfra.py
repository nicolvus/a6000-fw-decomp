"""Tests for S118 — `[SFRA]` (módulo de control del escalar, lado cámara).

Tests de **bytes reales**: leen el firmware y comprueban direcciones, textos y
recuentos concretos.  Cada test falla si una dirección o un texto cambia.
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
PREFIX = "[SFRA]"


def _data():
    with open(ROOT / BIN_PATH, "rb") as fh:
        return fh.read()


def _cstr(data, vaddr, maxlen=200):
    off = vaddr - BASE_VADDR
    assert 0 <= off < len(data), f"vaddr {hex(vaddr)} fuera del binario"
    end = off
    while end < len(data) and end < off + maxlen and 32 <= data[end] < 127:
        end += 1
    return data[off:end].decode("latin1")


def _strings(data):
    out = []
    start = 0
    while True:
        i = data.find(PREFIX.encode(), start)
        if i < 0:
            break
        end = i
        while end < len(data) and 32 <= data[end] < 127:
            end += 1
        out.append((BASE_VADDR + i, data[i:end].decode("latin1")))
        start = i + 1
    return out


def _json(name):
    with open(ROOT / "analysis" / "s118_sfra" / name, encoding="utf-8") as fh:
        return json.load(fh)


class TestModulo:
    def test_conteo_de_trazas(self):
        data = _data()
        assert len(_strings(data)) == 100

    def test_todas_las_trazas_son_distintas(self):
        data = _data()
        textos = [t for _, t in _strings(data)]
        assert len(set(textos)) == 100

    def test_bloque_de_cadenas(self):
        data = _data()
        ss = _strings(data)
        assert ss[0][0] == 0x43CE5A16
        assert ss[-1][0] == 0x43CE7723
        assert ss[0][1] == "[SFRA][CMD] ***GET_INFO***"
        assert ss[-1][1] == "[SFRA][RC] rcrt result error:%x"

    def test_cadenas_clave_en_su_direccion(self):
        data = _data()
        esperados = {
            0x43CE5A16: "[SFRA][CMD] ***GET_INFO***",
            0x43CE5A31: "[SFRA][CMP] ***GET_INFO_CMP***",
            0x43CE5A50: "[SFRA][CMD] ***SET_PATH(CLOSE)***",
            0x43CE5A72: "[SFRA][CMD] ***SET_PATH(OPEN)***",
            0x43CE5AA0: "[SFRA][CMP] ***SET_PATH_CMP(OPEN)***",
            0x43CE5AC5: "[SFRA][CMD] ***SET_SA_NOTIFY***",
            0x43CE5AE5: "[SFRA][CMP] ***SET_SA_NOTIFY_CMP***",
            0x43CE5B09: "[SFRA][CMD] ***GET_SA_RESULT***",
            0x43CE5B29: "[SFRA][CMP] ***GET_SA_RESULT_CMP***",
            0x43CE5B4D: "[SFRA][CMD] ***SET_JPEG_PARAM***",
            0x43CE5B6E: "[SFRA][CMP] ***SET_JPEG_PARAM_CMP***",
            0x43CE5B93: "[SFRA][CMD] ***GET_JPEG***",
            0x43CE5BAE: "[SFRA][CMP] ***GET_JPEG_CMP***",
            0x43CE5BCD: "[SFRA][CMD] ***LiveView SET_JPEG***",
            0x43CE5BF1: "[SFRA][CMP] ***LiveView SET_JPEG_CMP***",
            0x43CE5CAA: "[SFRA][CMP] ***SET_PATH_CMP(CLOSE)***",
            0x43CE6F65: "[SFRA][CMP] ***SET_PATH_CMP(SA CLOSE)***",
        }
        for vaddr, texto in esperados.items():
            assert _cstr(data, vaddr) == texto, hex(vaddr)

    def test_sub_bloques(self):
        d = _json("sfra.json")
        counts = {r["submodule"]: r["n"] for r in d["submodules"]}
        assert counts == {
            "RATECONTROL": 26,
            "(sin etiqueta)": 21,
            "ERROR": 14,
            "BUF": 11,
            "CMP": 9,
            "CMD": 8,
            "ERR": 4,
            "RC": 4,
            "NOTIFY": 1,
            "SFR_ERR_NOTREADY": 1,
            "WARNING": 1,
        }
        assert sum(counts.values()) == 100

    def test_catalogo_de_comandos(self):
        d = _json("sfra.json")
        nombres = sorted(c["name"] for c in d["commands"])
        assert nombres == sorted([
            "GET_INFO", "GET_INFO_CMP",
            "SET_PATH(CLOSE)", "SET_PATH(OPEN)", "SET_PATH_CMP(OPEN)",
            "SET_SA_NOTIFY", "SET_SA_NOTIFY_CMP",
            "GET_SA_RESULT", "GET_SA_RESULT_CMP",
            "SET_JPEG_PARAM", "SET_JPEG_PARAM_CMP",
            "GET_JPEG", "GET_JPEG_CMP",
            "LiveView SET_JPEG", "LiveView SET_JPEG_CMP",
            "SET_PATH_CMP(CLOSE)", "SET_PATH_CMP(SA CLOSE)",
        ])
        niveles = {}
        for c in d["commands"]:
            niveles.setdefault(c["level"], []).append(c["name"])
        assert len(niveles["CMD"]) == 8
        assert len(niveles["CMP"]) == 9

    def test_marcadores_asteriscos(self):
        data = _data()
        con_marcas = [t for _, t in _strings(data) if "***" in t]
        assert len(con_marcas) == 17
        for t in con_marcas:
            assert re.search(r"\*\*\*.+\*\*\*", t), t


class TestProtocolo:
    def test_tabla_de_comandos_con_ids(self):
        t = _json("command_table.json")
        por_nombre = {r["name"]: r for r in t}
        assert por_nombre["GET_INFO"]["msg_type"] == "0x100"
        assert por_nombre["GET_INFO"]["cmd_id"] == "0x10"
        assert por_nombre["GET_JPEG"]["cmd_id"] == "0x20"
        assert por_nombre["SET_JPEG_PARAM"]["cmd_id"] == "0x22"
        assert por_nombre["GET_SA_RESULT"]["cmd_id"] == "0x30"
        assert por_nombre["SET_SA_NOTIFY"]["cmd_id"] == "0x32"
        assert por_nombre["LiveView SET_JPEG"]["cmd_id"] == "0x42"
        assert por_nombre["GET_INFO_CMP"]["msg_type"] == "0x9010"
        assert por_nombre["SET_PATH(OPEN)"]["msg_type"] == "0x8120"
        assert por_nombre["SET_PATH(CLOSE)"]["msg_type"] == "0x8110"

    def test_predicados_en_sus_direcciones(self):
        """Bytes crudos de los predicados: tipo de mensaje y sub-comando."""
        data = _data()

        def raw(vaddr, n):
            return data[vaddr - BASE_VADDR:vaddr - BASE_VADDR + n].hex()

        # GET_INFO: tipo 0x100, sub-comando 0x10  (predicado 0x43b632ca)
        #   ldrh r3,[r0,#2] ; cmp.w r3,#0x100 ; ldrb r0,[r0,#0xf]
        assert raw(0x43B632CA, 10) == "4388b3f5807f06d1c07b"
        #   sub.w r1, r0, #0x10
        assert raw(0x43B632D4, 4) == "a0f11001"
        # GET_INFO_CMP: tipo 0x9010 (predicado 0x43b632b6)
        #   ldrh r0,[r0,#2] ; movw r3,#0x9010
        assert raw(0x43B632B6, 6) == "408849f21003"
        # SET_PATH(OPEN) 0x8120 / SET_PATH(CLOSE) 0x8110
        assert raw(0x43B63216, 6) == "408848f22013"
        assert raw(0x43B63226, 6) == "408848f21013"

    def test_sub_comandos_de_la_clase_0x0100(self):
        """Sub-comandos 0x20 (GET_JPEG) y 0x42 (LiveView SET_JPEG) en sus bytes."""
        data = _data()

        def raw(vaddr, n):
            return data[vaddr - BASE_VADDR:vaddr - BASE_VADDR + n].hex()

        # GET_JPEG: predicado 0x43b632e4, sub.w ip, r0, #0x20 en 0x43b632ee
        assert raw(0x43B632E4, 10) == "4388b3f5807f07d1c07b"
        assert raw(0x43B632EE, 4) == "a0f1200c"
        # LiveView SET_JPEG: predicado 0x43b63384, sub.w r2, r0, #0x42 en 0x43b6338e
        assert raw(0x43B63384, 10) == "4388b3f5807f06d1c07b"
        assert raw(0x43B6338E, 4) == "a0f14202"

    def test_resto_de_sub_comandos_de_la_clase_0x0100(self):
        """0x22 SET_JPEG_PARAM, 0x30 GET_SA_RESULT, 0x32 SET_SA_NOTIFY,
        0x34 y 0x40 (sin traza con ese nombre) en sus bytes."""
        data = _data()

        def raw(vaddr, n):
            return data[vaddr - BASE_VADDR:vaddr - BASE_VADDR + n].hex()

        assert raw(0x43B6330A, 4) == "a0f12203"   # SET_JPEG_PARAM  -> 0x22
        assert raw(0x43B63324, 4) == "a0f13002"   # GET_SA_RESULT   -> 0x30
        assert raw(0x43B6333E, 4) == "a0f13201"   # SET_SA_NOTIFY   -> 0x32
        assert raw(0x43B63374, 4) == "a0f13403"   # (sin nombre)     -> 0x34
        assert raw(0x43B63358, 4) == "a0f1400c"   # (sin nombre)     -> 0x40

    def test_tabla_tbb_del_despachador_de_finalizaciones(self):
        data = _data()
        off = 0x439A1654 - BASE_VADDR
        assert data[off:off + 5] == bytes([0x03, 0x1A, 0x29, 0x43, 0x91])
        # tbb [pc, r3] en 0x439a1650
        assert struct.unpack_from("<H", data, 0x439A1650 - BASE_VADDR)[0] == 0xE8DF
        # ldrb r3,[r0,#2] / subs r3,#1 / cmp r3,#4
        assert struct.unpack_from("<H", data, 0x439A1644 - BASE_VADDR)[0] == 0x7883
        assert struct.unpack_from("<H", data, 0x439A1648 - BASE_VADDR)[0] == 0x3B01
        assert struct.unpack_from("<H", data, 0x439A164A - BASE_VADDR)[0] == 0x2B04

    def test_nombre_de_fichero_del_despachador(self):
        data = _data()
        assert _cstr(data, 0x43CE59FD) == "ScalarInfraAsyncMain.cpp"


class TestFunciones:
    def test_recuentos(self):
        d = _json("sfra.json")
        c = d["counts"]
        assert c["strings"] == 100
        assert c["distinct_texts"] == 100
        assert c["pic_sites"] == 118
        assert c["functions"] == 47
        assert c["submodules"] == 11
        assert c["commands"] == 17
        assert c["source_files"] == 11

    def test_la_regla_canonica_sobrecuenta(self):
        """La regla del repo (4 KB, sin kill analysis) da 186: 68 falsos positivos."""
        d = _json("sfra.json")
        assert d["counts"]["pic_sites_regla_canonica"] == 186

    def test_despachador_principal(self):
        d = _json("sfra.json")
        f = [x for x in d["functions"] if x["func"] == "0x439a1864"]
        assert len(f) == 1
        assert f[0]["n_sites"] == 16
        textos = {s["text"] for s in f[0]["strings"]}
        assert "[SFRA][CMD] ***GET_INFO***" in textos
        assert "[SFRA][CMD] ***LiveView SET_JPEG***" in textos
        assert "[SFRA] ScalarInfraAsyncMain: Unknown Message(%d)!!!" in textos

    def test_todas_las_trazas_estan_referenciadas(self):
        d = _json("sfra.json")
        referenciadas = {s["vaddr"] for f in d["functions"] for s in f["strings"]}
        todas = {s["vaddr"] for s in d["strings"]}
        assert len(referenciadas) == 100
        assert referenciadas == todas

    def test_ficheros_fuente_del_modulo(self):
        d = _json("sfra.json")
        nombres = [f["name"] for f in d["source_files"]]
        assert nombres == [
            "ScalarInfraAsyncMain.cpp", "SfrJpegBuffer.h",
            "ScalarInfraSequenceJpeg.cpp", "ScalarInfraSequenceJpegStage.cpp",
            "ScalarInfraSequenceLiveView.cpp", "ScalarInfraSequenceLiveViewStage.cpp",
            "ScalarInfraSequenceSa.cpp", "ScalarInfraSequenceSaStage.cpp",
            "ScalarInfraSequenceUtility.cpp", "SfrYc.cpp", "DrvCallRc.cpp",
        ]
        vaddrs = [int(f["vaddr"], 16) for f in d["source_files"]]
        assert vaddrs == sorted(vaddrs)
        assert vaddrs[0] == 0x43CE59FD
        assert vaddrs[-1] == 0x43CE76FB


class TestDiferencialA7S:
    def test_la_a7s_tiene_el_prefijo(self):
        """La A7S fw3.20 SÍ lleva '[SFRA]': 100 apariciones, no 0."""
        ruta = ROOT / A7S_BIN
        if not ruta.exists():
            pytest.skip("blob de la A7S no disponible")
        a7s = ruta.read_bytes()
        assert a7s.count(PREFIX.encode()) == 100

    def test_los_100_mensajes_son_identicos(self):
        ruta = ROOT / A7S_BIN
        if not ruta.exists():
            pytest.skip("blob de la A7S no disponible")
        data = _data()
        a7s = ruta.read_bytes()
        comunes = 0
        for _, t in _strings(data):
            if t.encode() in a7s:
                comunes += 1
        assert comunes == 100

    def test_mismo_orden_y_mismos_recuentos(self):
        d = _json("sfra.json")
        a7s = d["a7s"]
        assert a7s["a6000"]["strings"] == a7s["a7s"]["strings"] == 100
        assert a7s["a6000"]["sites"] == a7s["a7s"]["sites"] == 118
        assert a7s["a6000"]["functions"] == a7s["a7s"]["functions"] == 47
        assert a7s["a6000"]["str_lo"] != a7s["a7s"]["str_lo"]

    def test_a6300_tiene_8_trazas_extra_con_nombres_genericos(self):
        ruta = ROOT / A6300_BIN
        if not ruta.exists():
            pytest.skip("blob de la A6300 no disponible")
        a6300 = ruta.read_bytes()
        assert a6300.count(PREFIX.encode()) == 108
        for viejo in (b"***CMD_JPEG***", b"***CMD_LIVEVIEW***",
                      b"***SET_PATH_CMP(JPEG CLOSE)***"):
            assert viejo in a6300
        data = _data()
        assert b"***CMD_JPEG***" not in data
        assert b"***CMD_LIVEVIEW***" not in data
