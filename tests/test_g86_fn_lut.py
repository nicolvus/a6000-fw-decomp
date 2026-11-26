"""G86 — opción «LUT» en el menú Fn: despachador de `viewUnified4.so`, hijo 39, nodo de datos, textos y cambio en caliente (offline, sin arnés GUI)."""
from __future__ import annotations

import struct
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "scripts/gui"), str(ROOT / "scripts/lut")]
import add_menu_entry as A
import build_fn_lut
import cfw_ajustes as cfw
import fn_lut_menu as F
import uxc_strings

DEV_A = ROOT / "firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev"
DEV_B = ROOT / "firmware/extracted/a6300-fw201/payload/firmware.tar_unpacked/0700_part_image/dev"
LIB = DEV_A / "nflasha15_unpacked_unpacked/lib"
needs = pytest.mark.skipif(not (LIB / "viewUnified4.so").is_file() or not DEV_B.is_dir(), reason="firmware de Sony ausente")


def _srnum(img: bytes, valor: int) -> int | None:
    """Ejecuta (Unicorn) el bloque del `tbh` para `valor` hasta `str.w r3,[r4,#0x25c]` y devuelve r3; None si el valor no pasa por un bloque simple."""
    from unicorn import UC_ARCH_ARM, UC_MODE_THUMB, Uc, UcError
    from unicorn.arm_const import (
        UC_ARM_REG_R3,
        UC_ARM_REG_R4,
        UC_ARM_REG_R5,
        UC_ARM_REG_R6,
    )
    mu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
    mu.mem_map(0, 0x200000)
    mu.mem_write(0, img[:0x190000])
    mu.mem_map(0x20000000, 0x1000)
    tgt = F.TBH + 2 * struct.unpack_from("<H", img, F.TBH + 2 * valor)[0]
    for r, v in ((UC_ARM_REG_R4, 0x20000000), (UC_ARM_REG_R5, 0), (UC_ARM_REG_R6, 0), (UC_ARM_REG_R3, 0xDEAD)):
        mu.reg_write(r, v)
    try:
        mu.emu_start(tgt | 1, F.FIN, count=8)
    except UcError:
        return None
    return mu.reg_read(UC_ARM_REG_R3) if mu.reg_read(UC_ARM_REG_R4) == 0x20000000 else None


@needs
def test_despachador_conserva_todos_los_valores_y_anade_el_26():
    orig = (LIB / "viewUnified4.so").read_bytes()
    nuevo = F.patch_vu4(orig, 0x1000)
    antes = {v: _srnum(orig, v) for v in range(F.TBH_N)}
    despues = {v: _srnum(nuevo, v) for v in range(F.TBH_N)}
    assert antes[1] == 1 and antes[3] == 2 and antes[4] == 3 and antes[0x29] == 0x26     # sanidad del emulador (tabla del 3.21)
    assert antes[F.VALOR_LUT] is None                                                   # 0x26 caía en el «por defecto»
    assert despues[F.VALOR_LUT] == F.SRNUM_LUT == 0x27
    assert {v: s for v, s in despues.items() if v != F.VALOR_LUT} == {v: s for v, s in antes.items() if v != F.VALOR_LUT}


@needs
def test_raiz_fn_tiene_39_hijos_y_el_nuevo_apunta_al_nodo():
    orig = (LIB / "viewUnified4.so").read_bytes()
    nuevo = F.patch_vu4(orig, 0x1234)
    assert struct.unpack_from("<H", nuevo, F.MOVS_N)[0] == 0x2200 | 39
    segs = A._segments(nuevo)
    _, dyn = A._dynamic(nuevo, segs)
    tags = {t: v for t, v in dyn if t}
    rel = {struct.unpack_from("<I", nuevo, A._off(segs, tags[0x11]) + i)[0]: struct.unpack_from("<I", nuevo, A._off(segs, tags[0x11]) + i + 4)[0] for i in range(0, tags[0x12], 8)}
    lit = ((F.LIT_LDR + 4) & ~3) + 0xBC
    arr = (struct.unpack_from("<I", nuevo, lit)[0] + F.LIT_ADD + 4) & 0xFFFFFFFF
    assert arr != F.TABLA_VA
    words = struct.unpack_from("<39I", nuevo, A._off(segs, arr))
    o_segs = A._segments(orig)
    assert words[:38] == struct.unpack_from("<38I", orig, A._off(o_segs, F.TABLA_VA))
    assert words[38] == 0x1234 and rel[arr + 4 * 38] & 0xFF == A.R_ARM_ABS32
    assert all(arr + 4 * i in rel for i in range(39))
    with pytest.raises(ValueError):
        F.patch_vu4(nuevo, 0)                                                            # no se aplica dos veces


@pytest.fixture(scope="module")
def construido(tmp_path_factory):
    import pp_menu_spec as M
    d = tmp_path_factory.mktemp("fnlut")
    snap = (dict(M.SETTINGS), list(M.PIDS), M.TREE)          # configurar_menu reescribe la spec global en el sitio
    try:
        build_fn_lut.main(DEV_A, DEV_B, d)
    finally:
        M.SETTINGS.clear()
        M.SETTINGS.update(snap[0])
        M.PIDS[:] = snap[1]
        M.TREE = snap[2]
    return d


@needs
def test_nodo_lut_en_caution_con_pid_y_opciones(construido):
    """G116: el nodo del hijo 39 existe en CautionConfig con el pid del ajuste «LUT», 7 opciones (Off + 6 ranuras de la SD) y textos nuevos."""
    cau = (construido / "lib/CautionConfig.so").read_bytes()
    vu4 = (construido / "lib/viewUnified4.so").read_bytes()
    import build_pp_gamma_menu as G
    segs = A._segments(cau)
    _, dyn = A._dynamic(cau, segs)
    ref = G.sym(cau, segs, dyn, "cmnViewSettingNodeRootMemoryRecallFn")[2][0]
    vsegs = A._segments(vu4)
    lit = ((F.LIT_LDR + 4) & ~3) + 0xBC
    arr = (struct.unpack_from("<I", vu4, lit)[0] + F.LIT_ADD + 4) & 0xFFFFFFFF
    nodo = ref + struct.unpack_from("<i", vu4, A._off(vsegs, arr + 4 * 38))[0]
    rd = lambda va, n: struct.unpack_from(f"<{n}I", cau, A._off(segs, va))
    _, kids, n, props = rd(nodo, 4)
    lst, ntri = rd(props, 2)
    tri = [rd(lst + 12 * i, 3) for i in range(ntri)]
    assert n == 7 and (0xE, 1, cfw.POR_ID["lut"].pid) in tri
    ops = []
    for k in rd(kids, n):
        p = rd(k, 4)[3]
        l2, nt2 = rd(p, 2)
        t = {a: v for a, _, v in (rd(l2 + 12 * i, 3) for i in range(nt2))}
        ops.append((t[0], t[0xF]))
    assert [v for _, v in ops] == list(range(7))
    en = uxc_strings.parse((construido / "share/app/string_english.uxc").read_bytes())[2]
    assert [en[t & 0xFFFF] for t, _ in ops] == ["Off"] + [f"LUT {i}" for i in range(1, 7)]
    assert en[tri[0][2] & 0xFFFF] == "LUT"


def test_ajuste_lut_pid_y_backup_unicos():
    a = cfw.POR_ID["lut"]
    assert a.backup == 0x1070211 and a.pid == cfw.PID_PRIMERO + 1
    assert len({x.pid or 0 for x in cfw.AJUSTES}) == len(cfw.AJUSTES)


def test_cambio_en_caliente_rearma_la_tabla_correcta():
    """Girar la rueda = la UI escribe el índice en el Backup `0x1070211`; la cueva lo lee en CADA escritura al hardware, sin caché de selección: la 2.ª escritura ya entrega el look nuevo (tabla del blob de la SD, G116)."""
    import lut_patch as L
    import lut_sd_userland as U
    img = L.apply_bytes(L.C.BIN.read_bytes())
    tablas = {k: bytes((i * 37 + k) % 256 for i in range(L.D.LUT_BYTES)) for k in range(1, 4)}
    blob = U.blob_tablas(tablas)
    bufs = []
    for opcion in (1, 2, 3, 1, 0):
        r, hw, _ = L.emular(img, 0, opcion, blob)
        bufs.append(hw if opcion else r)
    assert bufs[0] != bufs[1] != bufs[2] and bufs[3] == bufs[0]
    assert bufs[4] == 0x11223344                              # Off = puntero de fábrica
    assert [L.D.desempaqueta_21(t, list(struct.unpack_from("<405H", img, L.D.PERM - L.BASE))) for t in tablas.values()] == bufs[:3]
