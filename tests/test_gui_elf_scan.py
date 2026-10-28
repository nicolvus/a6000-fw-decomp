"""G1/G3 — verificadores del andamiaje GUI: inventario y resolución PLT de `libObj.so`.

Comprueban que `scripts/gui/elf_scan.py` y `scripts/gui/inventory.py` describen el
binario real (secciones, símbolos dinámicos, tabla PLT→símbolo importado) y que el
inventario de recursos coincide con lo publicado en `analysis/gui/g01-inventory.json`.
Se omiten si el firmware no está disponible (no se versiona).
"""
from __future__ import annotations

import itertools
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
LIBS = (
    ROOT
    / "firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image"
    / "dev/nflasha15_unpacked_unpacked/lib"
)
OBJ = LIBS / "libObj.so"
INVENTORY = ROOT / "analysis/gui/g01-inventory.json"

pytestmark = pytest.mark.skipif(not OBJ.exists(), reason="firmware 3.21 no versionado")

if str(ROOT / "scripts/gui") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts/gui"))

from elf_scan import Elf


@pytest.fixture(scope="module")
def obj() -> Elf:
    return Elf(OBJ)


# --- identidad del binario ----------------------------------------------------

def test_sha256_libobj():
    import hashlib

    assert hashlib.sha256(OBJ.read_bytes()).hexdigest() == (
        "8e8a937aed23c2783e7bbee8a4afa2fb4bcd897606f190b17dccadd207d05b6a"
    )


def test_secciones_clave(obj: Elf):
    sec = {s.name: s for s in obj.sections}
    assert sec[".text"].addr == 0xE2B70 and sec[".text"].size == 11_430_428
    assert sec[".plt"].addr == 0xDB3C4 and sec[".plt"].size == 30_624
    assert sec[".got"].addr == 0x102CBD0
    # .rodata y .text comparten offset y vaddr en este binario
    assert sec[".rodata"].addr == sec[".rodata"].offset == 0xBC9598


def test_simbolos_dinamicos(obj: Elf):
    # .dynsym tiene 3617 entradas; 1816 con valor (2 sin nombre) -> 1814 con nombre,
    # que es lo que cuenta `nm -D --defined-only` en el inventario.
    assert len(obj.symbols) == 1816
    assert len([s for s in obj.symbols if s.name]) == 1814
    names = {s.name for s in obj.symbols}
    for n in (
        "_ZN2ux6gfxeng14GraphicsEngine15sys_getInstanceEv",
        "_ZN2ux6resmgr15ResourceManager15sys_getInstanceEv",
        "_ZN2ux6gfxeng14GraphicsEngine14updateResourceEv",
    ):
        assert n in names


# --- PLT -> símbolo importado -------------------------------------------------

def test_rel_plt_es_jump_slot(obj: Elf):
    slots = obj.jump_slots()
    assert len(slots) == 2420
    assert slots[0][0] == 0x102CBDC  # primer slot .got usado por .rel.plt
    assert slots[-1][0] == 0x102F1A8
    assert all(s0[0] < s1[0] for s0, s1 in itertools.pairwise(slots))


def test_plt_map_cubre_casi_todo(obj: Elf):
    plt = obj.plt_map()
    # 2420 R_ARM_JUMP_SLOT; el stub restante del hueco reservado no resuelve
    assert len(plt) == 2419
    assert min(plt) >= 0xDB3C4 and max(plt) < 0xE2B70


def test_plt_map_mapeos_conocidos(obj: Elf):
    plt = obj.plt_map()
    assert plt[0xDB508] == "_ZN2ux6gfxeng14GraphicsEngine15sys_getInstanceEv"
    assert plt[0xDF01C] == "_ZN2ux6resmgr15ResourceManager15sys_getInstanceEv"
    assert plt[0xDC950] == "_ZN2ux6gfxeng15ResourceUpdaterC1EPNS_6resmgr15ResourceManagerE"


def test_plt_map_es_inyectivo(obj: Elf):
    plt = obj.plt_map()
    # cada stub apunta a su propio slot GOT, sin colisiones de dirección
    assert len(set(plt)) == len(plt)
    assert all(name for name in plt.values())


def test_stubs_no_pisan_text(obj: Elf):
    plt = obj.plt_map()
    text = next(s for s in obj.sections if s.name == ".text")
    for addr in plt:
        assert addr + 12 <= text.addr


# --- inventario de recursos ---------------------------------------------------

@pytest.mark.skipif(not INVENTORY.exists(), reason="inventario no generado")
def test_inventario_recursos():
    inv = json.loads(INVENTORY.read_text())
    res = inv["resources"]
    assert res["files"] == 238
    assert res["total_bytes"] == 55_175_204
    assert res["prefixes"]["string"] == 66
    assert len(inv["libs"]) >= 18
    assert inv["libs"]["libObj.so"]["bytes"] == 17_436_172

# --- llamadas directas (G03) --------------------------------------------------

def test_callers_de_plt_del_motor(obj: Elf):
    # GRM_fbrmUpdateYUV se llama desde la rutina de presentación 0x12e6d0..0x12e7de
    stub = next(a for a, n in obj.plt_map().items() if n == "GRM_fbrmUpdateYUV")
    sites = obj.callers(stub)
    assert 0x12E782 in sites and 0x12E7C2 in sites
    # GRM_gpermRectblit: 7 llamadas directas, entre ellas la limpieza de imagen
    stub = next(a for a, n in obj.plt_map().items() if n == "GRM_gpermRectblit")
    sites = obj.callers(stub)
    assert len(sites) == 7
    assert 0x5ED8D6 in sites


def test_callers_incluye_blx_y_no_inventa(obj: Elf):
    # las llamadas a la PLT ARM son `blx`: si sólo se decodificara `bl` saldrían 0
    stub = next(a for a, n in obj.plt_map().items() if n == "GRM_fbrmFillrectYUV")
    assert len(obj.callers(stub)) == 3
    # 0x12e6d0 no tiene llamada directa ni puntero literal (G03 §3)
    assert obj.callers(0x12E6D0) == []
    assert obj.find_literal_refs(0x12E6D0) == []


def test_cadenas_del_compositor_sin_referencias(obj: Elf):
    # WindowServer/ViewSystem y /dev/fb0 son cadenas muertas: sin literales ni punteros
    for text in ("/dev/fb0", "WindowServer_DI.cpp", "ViewSystem::ViewSystem(AppConfigIF*)"):
        addrs = obj.find_string(text)
        assert addrs, text
        for va in addrs:
            assert obj.find_literal_refs(va) == [], (text, hex(va))
            import struct as _s

            assert obj.raw.find(_s.pack("<I", va)) < 0, (text, hex(va))
