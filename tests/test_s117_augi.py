"""Tests for S117 — `[AUGI]`: la cabecera de 32 B del bloque de códec.

Tests de **bytes reales**: leen el firmware y comprueban direcciones, textos,
instrucciones y recuentos. Fallan si cambia cualquiera de esos datos.
"""

import hashlib
import json
import pathlib

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
BASE_VADDR = 0x43541000
BIN_PATH = "analysis/rea-independent/input/av-cam.bin"
A7S_BIN = (
    "firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/"
    "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"
)
DATA_DIR = ROOT / "analysis" / "s117_augi"
TOKEN = b"[AUGI]"


def _data():
    with open(ROOT / BIN_PATH, "rb") as fh:
        return fh.read()


def _cstr(data, vaddr, maxlen=300):
    """Cadena imprimible desde vaddr (se detiene en el primer byte no imprimible)."""
    off = vaddr - BASE_VADDR
    assert 0 <= off < len(data), f"vaddr {hex(vaddr)} fuera del binario"
    end = off
    while end < len(data) and end < off + maxlen and 32 <= data[end] < 127:
        end += 1
    return data[off:end].decode("latin1")


def _cstr_nul(data, vaddr, maxlen=300):
    off = vaddr - BASE_VADDR
    assert 0 <= off < len(data), f"vaddr {hex(vaddr)} fuera del binario"
    end = data.index(b"\x00", off)
    assert end - off <= maxlen
    return data[off:end].decode("latin1")


def _all_strings(data):
    """Cadenas normalizadas al inicio real de la racha imprimible que contienen el token."""
    seen = set()
    out = []
    start = 0
    while True:
        i = data.find(TOKEN, start)
        if i < 0:
            break
        s = i
        while s > 0 and 32 <= data[s - 1] < 127:
            s -= 1
        e = i + len(TOKEN)
        while e < len(data) and 32 <= data[e] < 127:
            e += 1
        if s not in seen:
            seen.add(s)
            out.append((BASE_VADDR + s, data[s:e].decode("latin1")))
        start = i + 1
    return sorted(out)


def _summary():
    with open(DATA_DIR / "augi.json", encoding="utf-8") as fh:
        return json.load(fh)


class TestModulo:
    def test_sha256_del_blob(self):
        data = _data()
        assert hashlib.sha256(data).hexdigest() == (
            "b60c845ccb90c0ff86b7f62f1f3f2ecda714aa20c37805959ebee2b429e56bb9"
        )

    def test_75_cadenas(self):
        assert len(_all_strings(_data())) == 75

    def test_prefijos_26_y_49(self):
        textos = [t for _, t in _all_strings(_data())]
        assert len([t for t in textos if t.startswith("[AUGI]")]) == 26
        assert len([t for t in textos if t.startswith("[CodecIF][AUGI]")]) == 49

    def test_primer_y_ultima(self):
        cadenas = _all_strings(_data())
        assert cadenas[0][0] == 0x43C6A28A
        assert cadenas[-1][0] == 0x43CD9C8D

    def test_cadenas_clave_en_su_direccion(self):
        data = _data()
        esperados = {
            0x43C6A28A: "[AUGI][PRINT] size[%d] %s",
            0x43C6A909: "[CodecIF][AUGI][dec][%s()][% 4u]: length              %8d",
            0x43C6AB1C: "[CodecIF][AUGI][dec][%s()][% 4u]: end_flag            %8d",
            0x43C6AC43: "[CodecIF][AUGI][dec][%s()][% 4u]: ",
            0x43C6B090: "[CodecIF][AUGI][enc][%s()][% 4u]: length                %8d",
            0x43C6B517: "[CodecIF][AUGI][enc][%s()][% 4u]: size_PPS              %8d",
            0x43CD993D: "[AUGI] ----------------------------------",
            0x43CD9968: "[AUGI] length                = %d",
            0x43CD9C01: "[AUGI] Reffered_flag         = %d",
            0x43CD9C8D: "[AUGI] size_SPS              = %d",
        }
        for vaddr, texto in esperados.items():
            assert _cstr(data, vaddr) == texto, hex(vaddr)

    def test_cadenas_de_comando(self):
        data = _data()
        assert _cstr_nul(data, 0x43C6A25C) == "Usage: augicsv <a(audio)|v(video)>\n"
        assert _cstr_nul(data, 0x43C64FD1) == (
            "AUGI data : augidata [ad|ae|vd|ve] [start index] [count]"
        )
        assert _cstr_nul(data, 0x43C6A438) == "printaugi"

    def test_86_sitios_y_75_referenciadas(self):
        s = _summary()
        assert s["counts"]["strings"] == 75
        assert s["counts"]["referenced"] == 75
        assert s["counts"]["ref_sites"] == 86
        assert s["counts"]["functions"] == 6
        assert sum(f["n_strings"] for f in s["functions"]) == 86
        # 75 distintas + 1 cadena con 3 sitios + 9 con 2 = 86
        assert s["counts"]["ref_sites"] == 75 + 2 + 9

    def test_compartidas(self):
        s = _summary()
        por_cadena = {}
        for f in s["functions"]:
            assert f["n_strings"] == len(set(f["strings"]))
            for v in f["strings"]:
                por_cadena.setdefault(v, set()).add(f["func"])
        multi = {v: fs for v, fs in por_cadena.items() if len(fs) > 1}
        assert len(multi) == 10
        assert len(multi["0x43c6ac43"]) == 3
        assert sum(len(fs) for fs in multi.values()) == 3 + 9 * 2


class TestLayout:
    def test_tamano_stride_y_byte_orders(self):
        s = _summary()
        lay = s["layout"]
        assert lay["size"] == 32
        assert lay["stride"] == 32
        assert lay["host_byte_order"] == "little-endian"
        assert lay["stream_byte_order"] == "big-endian por palabra de 4 B"

    def test_campos(self):
        campos = [(f["off"], f["name"]) for f in _summary()["layout"]["fields"]]
        assert campos == [
            ("0x00", "length"),
            ("0x04", "Reserved2"),
            ("0x06", "flags"),
            ("0x07", "Num_AUs"),
            ("0x08", "PTS"),
            ("0x0c", "DTS"),
            ("0x10", "nextHRDBuffer"),
            ("0x14", "nextPTS"),
            ("0x18", "pic_parameter_set_id"),
            ("0x19", "num_PPS"),
            ("0x1a", "seq_parameter_set_id / num_SPS"),
            ("0x1b", "flags2"),
            ("0x1c", "size_PPS"),
            ("0x1e", "size_SPS"),
        ]

    def test_bits_de_los_dos_bytes_de_flags(self):
        campos = {f["off"]: f for f in _summary()["layout"]["fields"]}
        assert campos["0x06"]["bits"] == {
            "0": "end_flag",
            "1": "PS_flag",
            "2": "EP_flag",
            "3": "DTS_flag",
            "4-7": "Reserved1",
        }
        assert campos["0x1b"]["bits"] == {
            "0": "change_PPS_flag",
            "1": "change_SPS_flag",
            "2": "Reserved4",
            "3": "Reffered_flag",
            "4-6": "PictureType",
            "7": "Reserved3",
        }

    def test_mapa_del_stream(self):
        palabras = [(w["bytes"], w["content"]) for w in _summary()["layout"]["stream_words"]]
        assert palabras == [
            ("0x00-0x03", "length (BE)"),
            ("0x04", "Num_AUs"),
            ("0x05", "flags (+0x06: end/PS/EP/DTS/Reserved1)"),
            ("0x06-0x07", "Reserved2 (BE)"),
            ("0x08-0x0b", "PTS (BE)"),
            ("0x0c-0x0f", "DTS (BE)"),
            ("0x10-0x13", "nextHRDBuffer (BE)"),
            ("0x14-0x17", "nextPTS (BE)"),
            ("0x18", "flags2 (+0x1b)"),
            ("0x19", "seq_parameter_set_id/num_SPS (+0x1a)"),
            ("0x1a", "num_PPS (+0x19)"),
            ("0x1b", "pic_parameter_set_id (+0x18)"),
            ("0x1c-0x1d", "size_SPS (BE)"),
            ("0x1e-0x1f", "size_PPS (BE)"),
        ]
        assert len(palabras) == 14

    def test_instrucciones_de_tamano_y_rev(self):
        data = _data()
        assert data[0x436163C2 - BASE_VADDR:0x436163C6 - BASE_VADDR] == bytes.fromhex("4b0188b0")
        assert data[0x436150EA - BASE_VADDR:0x436150EE - BASE_VADDR] == bytes.fromhex("640103e0")
        assert data[0x43A5CB12 - BASE_VADDR:0x43A5CB16 - BASE_VADDR] == bytes.fromhex("08ba7047")


class TestEscritor:
    def test_identidad_del_escritor(self):
        data = _data()
        assert _cstr_nul(data, 0x43C4B313) == "Int32 McAvcEncAudioSeqCtrlState::WriteAugi()"
        assert _cstr_nul(data, 0x43C4B36A) == "seqCtrl/audio/mcAvcEncAudioSeqCtrlState.cpp"

    def test_instrucciones_del_escritor(self):
        data = _data()
        assert data[0x435D640C - BASE_VADDR:0x435D6410 - BASE_VADDR] == bytes.fromhex("4fea4218")
        assert data[0x435D6448 - BASE_VADDR:0x435D644A - BASE_VADDR] == bytes.fromhex("e371")
        assert data[0x435D644C - BASE_VADDR:0x435D6450 - BASE_VADDR] == bytes.fromhex("48f809b0")
        assert data[0x435D64AE - BASE_VADDR:0x435D64B2 - BASE_VADDR] == bytes.fromhex("a2600fd0")

    def test_entrada_de_api(self):
        data = _data()
        assert _cstr_nul(data, 0x43C66FBF) == (
            "void StrmEngEncCIIf::CodecEventCreateVAUGI(UInt32, const UInt32*)"
        )

    def test_rtti_de_las_cuatro_clases(self):
        data = _data()
        esperados = {
            0x43C6A8DB: "virtual void DecExAugiConverter::Print(void*)",
            0x43C6ACC5: "virtual void DecInAudioAugiConverter::Print(void*)",
            0x43C6B02E: "virtual void DecInVideoAugiConverter::Print(void*)",
            0x43C6B554: "virtual void EncExAugiConverter::Print(UInt16, const void*)",
        }
        for vaddr, texto in esperados.items():
            assert _cstr_nul(data, vaddr) == texto, hex(vaddr)


class TestFunciones:
    def test_las_seis_funciones_y_sus_recuentos(self):
        s = _summary()
        assert [(f["func"], f["n_strings"]) for f in s["functions"]] == [
            ("0x436150ce", 1),
            ("0x43615eac", 15),
            ("0x4361610c", 10),
            ("0x43616200", 15),
            ("0x436163c0", 20),
            ("0x4391ca90", 25),
        ]

    def test_dumper_25_trazas(self):
        data = _data()
        assert data.count(b"[AUGI] ") == 25
        assert _cstr(data, 0x43CD9968) == "[AUGI] length                = %d"

    def test_handler_augicsv_usa_stride_32(self):
        data = _data()
        assert _cstr_nul(data, 0x43C6A25C) == "Usage: augicsv <a(audio)|v(video)>\n"
        assert _cstr(data, 0x43C6A28A) == "[AUGI][PRINT] size[%d] %s"


class TestVistasDec:
    def test_tres_vistas(self):
        v = _summary()["dec_views"]
        assert sorted(v) == ["0x43615eac", "0x4361610c", "0x43616200"]

    def test_el_offset_04_diverge(self):
        s = _summary()
        cabecera = {f["off"]: f["name"] for f in s["layout"]["fields"]}
        assert cabecera["0x04"] == "Reserved2"
        assert s["dec_views"]["0x43615eac"]["fields"]["0x04"] == "offset"

    def test_video_anade_dts_y_e_ptm(self):
        v = _summary()["dec_views"]
        audio = v["0x4361610c"]["fields"]
        video = v["0x43616200"]["fields"]
        assert "0x14" not in audio and video["0x14"] == "dts"
        assert "0x24" not in audio and video["0x24"] == "e_ptm"
        assert video["0x2a"] == "end_flag_33"
        assert "0x18" not in audio and video["0x18"] == "dts_33 (u8)"

    def test_instrucciones_de_la_vista_dec(self):
        data = _data()
        # bl 0x43a7e32e (invierte 32 B) al entrar en DecEx
        assert data[0x43615EB6 - BASE_VADDR:0x43615EBA - BASE_VADDR] == bytes.fromhex("68f03af2")
        # ldrb.w r3,[sp,#9]  -> AUGI_type
        assert data[0x43615EEE - BASE_VADDR:0x43615EF2 - BASE_VADDR] == bytes.fromhex("9df80930")
        # ubfx r3,r3,#2,#2   -> PTS_DTS_flag
        assert data[0x43615F02 - BASE_VADDR:0x43615F06 - BASE_VADDR] == bytes.fromhex("c3f38103")
        # DecInAudio/Video leen directamente: la copia 0x43a7e32e no se llama allí
        assert data[0x43615EAC - BASE_VADDR:0x43615EB0 - BASE_VADDR] == bytes.fromhex("10b588b0")


class TestDiferencialA7S:
    def test_75_cadenas_identicas(self):
        ruta = ROOT / A7S_BIN
        if not ruta.exists():
            pytest.skip("blob de la A7S no disponible")
        a7s = ruta.read_bytes()
        a6000 = _data()
        textos_a6000 = [t for _, t in _all_strings(a6000)]
        textos_a7s = [t for _, t in _all_strings(a7s)]
        assert len(textos_a6000) == 75
        assert len(textos_a7s) == 75
        assert set(textos_a6000) == set(textos_a7s)
        assert a6000.count(TOKEN) == 75
        assert a7s.count(TOKEN) == 75

    def test_posiciones_distintas(self):
        ruta = ROOT / A7S_BIN
        if not ruta.exists():
            pytest.skip("blob de la A7S no disponible")
        a7s = _all_strings(ruta.read_bytes())
        assert a7s[0][0] == 0x43C6740F
        assert a7s[-1][0] == 0x43CCA5A5
        assert a7s[0][0] != _all_strings(_data())[0][0]

    def test_resumen_sin_exclusivas(self):
        s = _summary()
        assert s["counts"]["a7s_strings"] == 75
        assert s["counts"]["a7s_comunes"] == 75
        assert s["counts"]["a7s_solo_a6000"] == 0
        assert s["counts"]["a7s_solo_a7s"] == 0
        assert s["a7s"]["solo_a6000"] == []
        assert s["a7s"]["solo_a7s"] == []
