"""G28: los descriptores van en la copia del gestor que lleva `viewUnified2.so` (la que usa la UI), no en `cmn_view_processDataMgr.so`."""
from __future__ import annotations

import struct
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts/gui"))
import add_menu_entry as A
import pp_descriptors as P
import pp_menu_spec as M
import silent_descriptor as S

LIB = ROOT / "firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha15_unpacked_unpacked/lib"
needs = pytest.mark.skipif(not (LIB / "viewUnified2.so").is_file(), reason="libs de Sony ausentes")
AJ = [P.Ajuste(M.PIDS[i], s.clave, tuple(v for _, v in s.opciones), s.evento) for i, s in enumerate(M.SETTINGS.values())]


def _rd(d, va, n=1):
    return struct.unpack_from(f"<{n}I", d, A._off(A._segments(d), va))


def _cadena(d, tabla, pid):
    """(nombre, evento, id lectura, clave set, clave get, valores) del modelo del descriptor de `pid`; None si no tiene."""
    desc = _rd(d, _rd(d, tabla + 4 * pid)[0], P.DESC_PALABRAS)
    if not desc[6]:
        return None
    m = _rd(d, desc[6], P.MODEL_PALABRAS)
    n = m[8] >> 8
    nombre = d[A._off(A._segments(d), m[0]):][:5]
    return nombre, m[2], m[3], _rd(d, m[4])[0], _rd(d, m[5])[0], _rd(d, m[7], n), desc[5] >> 8 & 0xFF


def _reloc(d):
    segs = A._segments(d)
    _, dyn = A._dynamic(d, segs)
    t = {k: v for k, v in dyn if k}
    o = A._off(segs, t[0x11])
    return {struct.unpack_from("<I", d, o + i)[0]: struct.unpack_from("<I", d, o + i + 4)[0] for i in range(0, t[0x12], 8)}


@needs
def test_vu2_lleva_los_mismos_descriptores_que_la_so_y_con_relocaciones():
    vu2 = (LIB / "viewUnified2.so").read_bytes()
    cmn = (LIB / "cmn_view_processDataMgr.so").read_bytes()
    nv = P.patch(S.patch(vu2, S.TABLA_D_VU2, S.DESC_EFCS_VU2), AJ, P.TABLA_D_VU2)
    nc = P.patch(S.patch(cmn), AJ)
    for pid in [S.PID_NUEVO, S.PID_EFCS, *M.PIDS]:
        assert _cadena(nv, P.TABLA_D_VU2, pid) == _cadena(nc, P.TABLA_D, pid), hex(pid)
    assert _cadena(nv, P.TABLA_D_VU2, S.PID_NUEVO)[1:5] == (0x5B, 0x6C, 0x291, 0x292)
    rel = _reloc(nv)
    for pid in [S.PID_NUEVO, *M.PIDS]:                      # cada puntero nuevo se reubica en la carga
        dv = _rd(nv, P.TABLA_D_VU2 + 4 * pid)[0]
        assert rel[P.TABLA_D_VU2 + 4 * pid] & 0xFF == 0x17 and rel[dv + 4] & 0xFF == 0x17 and rel[dv + 24] & 0xFF == 0x17


@needs
def test_clase_normal_para_todos_los_pids_del_menu():
    vu2 = (LIB / "viewUnified2.so").read_bytes()
    sin = struct.unpack_from("<233I", vu2, P.ELEM_VU2)
    assert len({sin[p] for p in M.PIDS}) > 1                 # antes: Normal y Custom*Button mezclados
    nuevo = struct.unpack_from("<233I", P.clase_normal(vu2, [S.PID_NUEVO, *M.PIDS]), P.ELEM_VU2)
    assert {nuevo[p] for p in [S.PID_NUEVO, *M.PIDS]} == {sin[S.PID_EFCS]}
    assert [p for p in range(233) if nuevo[p] != sin[p]] == sorted(p for p in M.PIDS if sin[p] != sin[S.PID_EFCS])
