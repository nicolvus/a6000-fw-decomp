"""G84 — «Zebra Nivel»: bytes originales, idempotencia, cueva fuera de lo vivo y emulación (Off no cambia nada; el resto fija el centro y conserva registros)."""
import struct
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "scripts/g61"), str(ROOT / "scripts/g84")]
import zebra_patch as P

pytestmark = pytest.mark.skipif(not P.SRC.exists(), reason="sin libObj extraído")


def test_bytes_originales_e_idempotencia():
    orig = P.SRC.read_bytes()
    img = P.apply_bytes(orig)
    assert len(img) == len(orig) and P.apply_bytes(orig) == img
    with pytest.raises(ValueError):
        P.apply_bytes(img)
    diff = [i for i in range(len(orig)) if orig[i] != img[i]]
    assert all(P.CAVE <= i < P.CAVE_FIN or P.HOOK[0] <= i < P.HOOK[0] + 4 for i in diff)


def test_gancho_y_vuelta_exactos():
    from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs
    img = P.apply_bytes(P.SRC.read_bytes())
    cs = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
    (i,) = list(cs.disasm(img[P.HOOK[0]:P.HOOK[0] + 4], P.HOOK[0]))
    assert i.mnemonic == "b.w" and i.op_str == f"#{P.CAVE:#x}"
    va, code = P.piezas()["zebra"]
    assert any(x.mnemonic == "b.w" and x.op_str == f"#{P.VUELTA:#x}" for x in cs.disasm(code, va))


def test_cueva_sin_referencias():
    d = P.SRC.read_bytes()
    a, b = P.CAVE, P.CAVE_FIN
    assert [i for i in range(0, len(d) - 3, 2) if a - 1 <= struct.unpack_from("<I", d, i)[0] < b + 1 and not a <= i < b] == []


def test_emulacion():
    P.comprobar()
