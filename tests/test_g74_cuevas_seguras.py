"""G74: cada cueva/celda de los parches de la campaña está a cero en el fichero Y en el volcado vivo de la cámara (G72), sin referencias, y fuera de zonas vivas."""
import importlib
import itertools
import struct
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "scripts/gui"), *(str(ROOT / "scripts" / g) for g in ("g22", "g38", "g55", "g57", "g63", "g65", "g69", "g61", "g68"))]
AV = ROOT / "analysis/rea-independent/input/av-cam.bin"
DUMP = ROOT / "analysis/camera-dumps/ram-servicio-20261020/ram_0x80000000.bin"
LIBOBJ = ROOT / "analysis/camera-extract/usr/lib/libObj.so"
B, RO = 0x43541000, 0x3541000
BSS_AV = (0x43CFE37F, 0x43F430D9)          # bss declarado en la cabecera LIRO (G72); lo que sigue hasta la cola 0x4409ce00 se respalda y restaura en suspensión
LIBRE_CABECERA = (0x4354141C, 0x435418D8)  # hueco verificado (test_e25_25_caves); 0x43541900 es viva (GOT 0x44020f00)


def _cuevas():
    g55, g57, g65, g69, r5, ad = (importlib.import_module(m) for m in ("bulb_timer_patch", "focus_bracket_patch", "jpeg_hook_patch", "color_chrome_patch", "patch_silent_r5", "avcam_dinamico"))
    return {
        "g55": (g55.CAVE, g55.CAVE_END), "g57": (g57.CAVE, g57.CAVE_END), "g57 celda": (g57.CELDA, g57.CELDA + 4),
        "g65": (g65.CAVE, g65.COUNTER + 4), "g69": (g69.CAVE, g69.CAVE_END), "g38/g63 silent": (r5.CAVE, r5.CAVE_END),
        "g73 A": ad.ZONA_A, "g73 B": ad.ZONA_B,
    }


@pytest.fixture(scope="module")
def av():
    if not (AV.exists() and DUMP.exists()):
        pytest.skip("faltan av-cam.bin o el volcado vivo")
    return AV.read_bytes()


def _vivo(a, b):
    with DUMP.open("rb") as f:
        f.seek(a - B + RO)
        return f.read(b - a)


def _refs(d, a, b):
    """Palabras literales y pares movw/movt (Thumb-2) que apuntan a [a-3, b)."""
    hit = [B + i for i in range(0, len(d) - 3, 4) if a - 3 <= struct.unpack_from("<I", d, i)[0] < b]
    lo, hi = {}, {}
    for i in range(0, len(d) - 3, 2):
        h1, h2 = struct.unpack_from("<HH", d, i)
        if h1 & 0xFBF0 in (0xF240, 0xF2C0) and not h2 & 0x8000:
            imm = ((h1 & 0xF) << 12) | ((h1 >> 10 & 1) << 11) | ((h2 >> 12 & 7) << 8) | (h2 & 0xFF)
            (lo if h1 & 0xFBF0 == 0xF240 else hi).setdefault((h2 >> 8) & 15, []).append((i, imm))
    for rg, ls in lo.items():
        for i, l in ls:
            hit += [B + i for j, h in hi.get(rg, []) if 0 < j - i <= 24 and a - 3 <= (h << 16 | l) < b]
    return hit


@pytest.mark.parametrize("nombre", list(_cuevas()))
def test_cueva_av_cam_viva_cero(av, nombre):
    a, b = _cuevas()[nombre]
    assert not any(av[a - B:b - B]), "no está a cero en el fichero"
    assert not any(_vivo(a, b)), "no está a cero en el volcado vivo (memoria viva)"
    assert b <= BSS_AV[0] or a >= BSS_AV[1]
    assert _refs(av, a, b) == []


@pytest.mark.parametrize("nombre", ["g55", "g57", "g57 celda", "g65"])
def test_cuevas_g74_en_hueco_verificado(nombre):
    a, b = _cuevas()[nombre]
    assert LIBRE_CABECERA[0] <= a and b <= LIBRE_CABECERA[1]


def test_cuevas_no_se_solapan():
    r = sorted(v for k, v in _cuevas().items() if k not in ("g73 A", "g73 B"))
    assert all(x[1] <= y[0] for x, y in itertools.pairwise(r))


def test_zona_antigua_g55_g65_era_viva(av):
    assert any(_vivo(0x43541900, 0x43541B00)) and any(_vivo(0x44018250, 0x44018294))


# ---------------------------------------------------------------- libObj
def test_libobj_funcion_muerta_sin_referencias():
    if not LIBOBJ.exists():
        pytest.skip("falta libObj.so")
    d = LIBOBJ.read_bytes()
    import drp_patch as g68
    import intervalo_patch as g61
    for a, b in ((g61.CAVE, g61.CAVE_FIN), (g68.CAVE, g68.CAVE_FIN)):
        # cualquier palabra de 32 bits (en pasos de 2) que apunte dentro (con o sin bit Thumb): ninguna, salvo el original de la propia función
        assert [i for i in range(0, len(d) - 3, 2) if a - 1 <= struct.unpack_from("<I", d, i)[0] < b + 1 and not a <= i < b] == []


def test_libobj_contador_en_cola_de_pagina():
    if not LIBOBJ.exists():
        pytest.skip("falta libObj.so")
    import intervalo_patch as g61
    d = LIBOBJ.read_bytes()
    ph = [struct.unpack_from("<8I", d, 52 + 32 * k) for k in range(5)]
    cargas = [p for p in ph if p[0] == 1]
    ini, memsz = cargas[1][2], cargas[1][5]
    fin = ini + memsz
    assert fin <= g61.CTR and g61.CTR + 4 <= (fin + 0xFFF) & ~0xFFF           # fuera de .bss declarado, dentro de su última página mapeada
    assert [i for i in range(0, len(d) - 3, 4) if fin <= struct.unpack_from("<I", d, i)[0] < fin + 0x1000] == []
