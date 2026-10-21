"""Tests for S113 — `[CAM_DMM]` (gestor de memoria dinámico de la cámara).

Todos los tests son de **bytes reales**: leen el firmware y comprueban direcciones,
textos y recuentos. Si cambia una dirección, el test falla.
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
PREFIX = "[CAM_DMM]"


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


def _dmm_strings(data):
    out = []
    start = 0
    while True:
        i = data.find(PREFIX.encode(), start)
        if i < 0:
            break
        out.append((BASE_VADDR + i, _cstr(data, BASE_VADDR + i)))
        start = i + 1
    return out


def _summary():
    with open(ROOT / "analysis" / "s113_cam_dmm" / "summary.json", encoding="utf-8") as fh:
        return json.load(fh)


class TestModulo:
    def test_conteo_y_rango(self):
        data = _data()
        strings = _dmm_strings(data)
        assert len(strings) == 54
        assert strings[0][0] == 0x43CCE6AE
        assert strings[-1][0] == 0x43CCF1C3

    def test_operaciones_y_clases_de_error(self):
        s = _summary()
        assert s["counts"]["strings"] == 54
        assert s["counts"]["operations"] == 11
        assert s["counts"]["error_classes"] == 4
        for op, n in (("AllocNew", 4), ("AllocNewRdv", 4), ("AllocShare", 4),
                      ("Free", 2), ("FreeRdv", 2), ("Open", 3), ("Close", 2),
                      ("MemoryHandle", 5), ("AsyncAllocNew", 9),
                      ("AsyncAllocRule", 7), ("LoadExtraMap", 7)):
            assert s["operations"][op]["n"] == n, op
        for err, n in (("ERR_DMM_RET_CODE", 10), ("ERR_DMM_DIFFERENT_COMP", 10),
                       ("ERR_DMM_HANDLE", 4), ("ERR_DMM_OPEN", 5)):
            assert s["error_classes"][err]["n"] == n, err

    def test_cadenas_clave_en_su_direccion(self):
        data = _data()
        esperados = {
            0x43CCE6AE: "[CAM_DMM]: AllocNew: ERR_DMM_RET_CODE!: %d, %x, %x, %x",
            0x43CCE6E5: "[CAM_DMM]: AllocNew: ERR_DMM_DIFFERENT_COMP! msg_id %08x, my_id %08x, %x, %x, %x",
            0x43CCEB07: "[CAM_DMM]: MemoryHandle::AllocNew: ERR_EXTENT_SIZE! size[%d] max[%d]",
            0x43CCEB4C: "[CAM_DMM]: MemoryHandle::AllocRendezvous: ERR_EXTENT_SIZE! size[%d] max[%d]",
            0x43CCEB98: "[CAM_DMM]: MemoryHandle::AllocShare: DMM_UNIT_INVALID!",
            0x43CCED35: "[CAM_DMM]: AsyncAllocNew: rcv Invalid Src!: 0x%08x",
        }
        for vaddr, texto in esperados.items():
            assert _cstr(data, vaddr) == texto, hex(vaddr)

    def test_rdv_es_rendezvous(self):
        """`AllocNewRdv` se desarrolla como `MemoryHandle::AllocRendezvous`."""
        data = _data()
        assert b"MemoryHandle::AllocRendezvous" in data
        assert b"AllocNewRdv" in data


class TestFunciones:
    def test_25_funciones_en_un_bloque_contiguo(self):
        with open(ROOT / "analysis" / "s113_cam_dmm" / "func_map.json", encoding="utf-8") as fh:
            fm = json.load(fh)
        funcs = fm["functions"]
        assert len(funcs) == 25
        addrs = [int(f["func"], 16) for f in funcs]
        assert min(addrs) == 0x439011D8
        assert max(addrs) == 0x43903D5C
        # bloque contiguo: 25 funciones en menos de 12 KB
        assert max(addrs) - min(addrs) < 0x3000

    def test_bloque_asincrono(self):
        with open(ROOT / "analysis" / "s113_cam_dmm" / "func_map.json", encoding="utf-8") as fh:
            fm = json.load(fh)
        por_func = {f["func"]: f for f in fm["functions"]}
        assert por_func["0x439037c0"]["n_strings"] == 24      # AsyncAllocNew
        assert por_func["0x43903b80"]["n_strings"] == 17      # AsyncAllocRule
        assert por_func["0x43903d5c"]["n_strings"] == 8       # LoadExtraMap

    def test_la_traza_de_memoryhandle_asignada(self):
        with open(ROOT / "analysis" / "s113_cam_dmm" / "func_map.json", encoding="utf-8") as fh:
            fm = json.load(fh)
        textos = {s["text"] for f in fm["functions"] for s in f["strings"]}
        assert any("MemoryHandle::AllocRendezvous" in t for t in textos)
        assert any("DMM_UNIT_INVALID" in t for t in textos)


class TestUserland:
    def test_dmmaccess_exportado_en_libmprctrl(self):
        """S37: el userland es cliente del DMM del firmware."""
        lib = ROOT / ("firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/"
                      "nflasha15_unpacked_unpacked/lib/libmprctrl.so")
        if not lib.exists():
            pytest.skip("libmprctrl.so no disponible")
        data = lib.read_bytes()
        for simbolo in (b"DmmAllocateNEWAndOpen_body", b"DmmShare", b"DmmCloseORFree_body",
                        b"DmmOpen", b"GetUnitHandleFromDmmAlloc", b"GetDMMRetMsg",
                        b"CheckOSALRetCode", b"DmmAccess"):
            assert simbolo in data, simbolo


class TestDiferencialA7S:
    def test_a7s_no_tiene_el_prefijo(self):
        ruta = ROOT / A7S_BIN
        if not ruta.exists():
            pytest.skip("blob de la A7S no disponible")
        assert ruta.read_bytes().count(PREFIX.encode()) == 0

    def test_50_de_54_mensajes_equivalentes(self):
        ruta = ROOT / A7S_BIN
        if not ruta.exists():
            pytest.skip("blob de la A7S no disponible")
        a7s = ruta.read_bytes()
        data = _data()

        def norm(t):
            t = t.split("%")[0].replace("0x", "").replace(" ", "").rstrip(":!.,")
            return t

        a7s_norm = {norm(m.group().decode("latin1"))
                    for m in re.finditer(rb"[\x20-\x7e]{6,}", a7s)}
        comunes = 0
        faltan = []
        for vaddr, texto in _dmm_strings(data):
            core = texto[len(PREFIX) + 1:]
            if norm(core) in a7s_norm:
                comunes += 1
            else:
                faltan.append(vaddr)
        assert comunes == 50
        # las 4 restantes son los mensajes de AllocNew, sustituidos en la fw3.21
        assert faltan == [0x43CCE6AE, 0x43CCE6E5, 0x43CCE736, 0x43CCE766]

    def test_la_variante_allocnew_de_la_a7s(self):
        ruta = ROOT / A7S_BIN
        if not ruta.exists():
            pytest.skip("blob de la A7S no disponible")
        a7s = ruta.read_bytes()
        assert b"AllocNew(DMM_OPTION_NOUNIT_WARN): ERR_DMM_RET_CODE!: %x" in a7s
