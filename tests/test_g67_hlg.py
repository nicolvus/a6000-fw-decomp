"""G67: HLG1–3 — tablas (monotonía, extremos, formato), parche de curvas del núcleo y libObj (Unicorn sobre bytes reales)."""
from __future__ import annotations

import struct
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts/gui"))
sys.path.insert(0, str(ROOT / "tests"))
import itertools

import patch_libobj_pp as P
import pp_curves_patch as C
import pp_hlg_curves as H

AVCAM = C.ROOT / "analysis/rea-independent/input/av-cam.bin"
needs_av = pytest.mark.skipif(not (AVCAM.is_file() and C.A6300.is_file()), reason="av-cam ausente")


@pytest.mark.parametrize("n", (1, 2, 3))
def test_tabla_monotona_extremos_y_niveles(n):
    t = H.tabla(n)
    assert len(t) == 2048 and all(a <= b for a, b in itertools.pairwise(t))
    assert t[0] == 64 and t[-1] == round(64 + 876 * H.NIVEL[n]) and max(t) <= 1023
    assert abs(t[66] - 397) <= 6          # gris 18 % ≈ 38 % de señal HLG (BT.2100)


def test_niveles_ordenados_y_comunes_bajo_la_rodilla():
    t1, t2, t3 = (H.tabla(n) for n in (1, 2, 3))
    assert t1[-1] < t2[-1] < t3[-1] and t1[:400] == t2[:400] == t3[:400]


def test_oetf_arib_puntos_conocidos():
    assert abs(H.oetf(1 / 12) - 0.5) < 1e-6 and abs(H.oetf(1.0) - 1.0) < 1e-6 and H.oetf(0) == 0


def _emula_hlg(img, malloc=0x30001000):
    """Ejecuta el gancho HLG sobre la imagen parcheada con `malloc` simulado; devuelve (unicorn, r3, llamadas a malloc)."""
    import avcam_dinamico as D
    from unicorn import UC_ARCH_ARM, UC_MODE_THUMB, Uc
    from unicorn.arm_const import (
        UC_ARM_REG_LR,
        UC_ARM_REG_R0,
        UC_ARM_REG_R3,
        UC_ARM_REG_SP,
    )
    mu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
    mu.mem_map(0x43541000, 0x00B00000 + 0x200000)
    mu.mem_write(0x43541000, img)
    for a, s in ((0x10000000 - 0x10000, 0x20000), (0x20000000, 0x1000), (0x30000000, 0x20000), (0x30100000, 0x1000)):
        mu.mem_map(a, s)
    mu.mem_write(D.MALLOC, D.malloc_simulado(0x30100000))
    mu.mem_write(0x30100004, struct.pack("<I", malloc))
    mu.mem_write(0x20000000 + 0x7CA, b"\x05")
    mu.reg_write(UC_ARM_REG_SP, 0x10000000)
    mu.reg_write(UC_ARM_REG_R3, 0x20000000)
    mu.reg_write(UC_ARM_REG_R0, 0x1234)
    mu.reg_write(UC_ARM_REG_LR, 0x30010000 | 1)
    mu.emu_start(_entrada(img) | 1, 0x30010000, count=2_000_000)
    return mu, mu.reg_read(UC_ARM_REG_R3), struct.unpack("<I", mu.mem_read(0x30100000, 4))[0]


def _entrada(img):
    import avcam_dinamico as D
    w = struct.unpack_from("<2H", img, D.HOOK_HLG[0] - C.BASE)               # bl del gancho → destino
    h1, h2 = w
    off = ((h1 & 0x7FF) << 12) | ((h2 & 0x7FF) << 1)
    if off & 0x400000:
        off -= 0x800000
    return D.HOOK_HLG[0] + 4 + off


@needs_av
def test_hlg_dinamico_unicorn_curvas_punteros_y_fallo():
    import avcam_dinamico as D
    base, a6300 = AVCAM.read_bytes(), C.A6300.read_bytes()
    ps = C.patches(base, C.A7S.read_bytes(), a6300, (1, 2, 3))
    assert not any(w.startswith(("puntero 0x1c", "puntero 0x1d", "puntero 0x1e")) for _, _, w in ps)
    ps_h = [p for p in ps if p[2].startswith(("dato cueva HLG", "gancho HLG"))]
    assert len(ps_h) == 2
    D.comprobar_zonas([(a, a + len(b)) for a, b, w in ps_h if w.startswith("dato")])
    gancho = next(p for p in ps_h if p[2].startswith("gancho"))
    assert base[gancho[0] - C.BASE:][:4] == D.HOOK_HLG[1]                  # bytes originales del gancho
    assert not any(any(base[a - C.BASE:a - C.BASE + len(b)]) for a, b, w in ps_h if w.startswith("dato"))
    assert all(base[D.SEL + 2 * (11 + n) - C.BASE:][:2] == bytes([0, 0x0A]) and base[D.TAB_PTR + 8 * (0x1B + n) + 4 - C.BASE:][:4] == b"\0" * 4 for n in (1, 2, 3))
    img = C.apply(base, ps_h)
    mu, r3, n = _emula_hlg(img)
    assert n == 1 and r3 == 5                                              # una reserva; la instrucción original (ldrb r3,[r3,#0x7ca]) se ejecutó
    buf = 0x30001000
    for k in (1, 2, 3):
        ptr = struct.unpack("<I", mu.mem_read(D.TAB_PTR + 8 * (0x1B + k) + 4, 4))[0]
        assert ptr == buf + (k - 1) * D.STRIDE_BUF
        got = struct.unpack("<2048H", mu.mem_read(ptr, 0x1000))
        err = max(abs(a - b) for a, b in zip(got, H.tabla(k)))
        assert err <= 1, err                                                # < 1 código de 10 bits frente a la OETF exacta (real) y ≤ 1 frente a la tabla redondeada
        assert max(abs(a - b) for a, b in zip(got, D.generar_hlg(*D.esquema(), k))) == 0   # la cueva = réplica Python
        cola = bytes(mu.mem_read(ptr + 0x1000, 26))
        assert cola[0x12] == 4 and cola[0x14] == 0x1B + k
        assert bytes(mu.mem_read(D.SEL + 2 * (11 + k), 2)) == bytes([0x1B + k] * 2)
    mu2, r3b, n2 = _emula_hlg(img, malloc=0)                               # fallo de reserva: nada escrito, comportamiento de fábrica
    assert n2 == 1 and r3b == 5
    assert bytes(mu2.mem_read(D.SEL + 24, 6)) == base[D.SEL + 24 - C.BASE:][:6] and bytes(mu2.mem_read(D.TAB_PTR + 8 * 0x1C + 4, 4)) == b"\0" * 4


@needs_av
def test_parche_original_sin_hlg_no_cambia():
    base = AVCAM.read_bytes()
    assert not any("HLG" in w for _, _, w in C.patches(base, C.A7S.read_bytes(), C.A6300.read_bytes()))


def test_libobj_hlg_unicorn():
    import test_g25_gamma_libobj as T
    if not T.LIB.is_file():
        pytest.skip("libObj ausente")
    old, new = T.LIB.read_bytes(), P.patch_gamma(T.LIB.read_bytes(), hlg=True)
    base = P.patch_gamma(T.LIB.read_bytes())
    for v in range(12):                                                    # lo anterior no cambia
        assert T.call(new, T.APP2OBJ_FN, 7, v) == T.call(base, T.APP2OBJ_FN, 7, v)
    for app, vid in enumerate(P.VALUEID_HLG):
        assert T.call(new, T.APP2OBJ_FN, 7, app) == (1, vid) and T.call(new, T.OBJ2APP_FN, 7, vid) == (1, app)
    assert T.call(new, T.APP2OBJ_FN, 7, 15)[0] == 0 and T.call(new, T.OBJ2APP_FN, 7, 0x589)[0] == 0
    assert len(new) == len(old)
