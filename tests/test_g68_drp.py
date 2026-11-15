"""G68 — DR Prioridad: bytes originales, idempotencia, ramas a destino exacto, combinación con g61 y Unicorn (Off no cambia nada; Débil/Fuerte emiten DRO y sesgo)."""
import struct
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "scripts/g61"), str(ROOT / "scripts/g68")]
import cfw_ajustes as C
import drp_patch as P
import intervalo_patch as G61

pytestmark = pytest.mark.skipif(not P.SRC.exists(), reason="sin libObj extraído")


def test_bytes_originales_e_idempotencia():
    orig = P.SRC.read_bytes()
    img = P.apply_bytes(orig)
    assert len(img) == len(orig) and P.apply_bytes(orig) == img
    with pytest.raises(ValueError):
        P.apply_bytes(img)
    diff = [i for i in range(len(orig)) if orig[i] != img[i]]
    assert all(P.CAVE <= i < P.CAVE_FIN or P.HOOK[0] <= i < P.HOOK[0] + 4 for i in diff)


def test_ramas_a_destino_exacto():
    from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs
    vistos = set()
    for va, code in P.piezas().values():
        for i in Cs(CS_ARCH_ARM, CS_MODE_THUMB).disasm(code, va):
            if i.mnemonic in ("bl", "blx") or (i.mnemonic == "b.w" and not P.CAVE <= int(i.op_str[1:], 16) < P.CAVE_FIN):
                vistos.add(int(i.op_str[1:], 16))
    assert vistos == {*P.EXT, 0xDD5F4, P.CAVE, P.DESTINO}, {hex(x) for x in vistos}


def test_cueva_sin_referencias_y_sin_solape_con_g61():
    d = P.SRC.read_bytes()
    words = struct.unpack(f"<{len(d) // 4}I", d[:len(d) // 4 * 4])
    assert not any(P.CAVE <= (w & ~1) < P.CAVE_FIN for w in words)
    assert P.CAVE >= G61.CAVE_FIN
    both = G61.apply_bytes(P.apply_bytes(d))
    assert both == P.apply_bytes(G61.apply_bytes(d))


def test_ajuste_en_la_tabla():
    a = C.POR_ID["dr_prior"]
    assert [v for _, v in a.opciones] == [0, 1, 2] and a.backup in C.ID_LIBRES


def test_unicorn():
    P.comprobar()
