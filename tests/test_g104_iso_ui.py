"""G104 §8.5 — `iso_ui_patch`: las filas 32000/40000/51200 de `ViewIsoSensitivity` dejan de ocultarse (bytes, desensamblado, tabla de menú)."""
import struct
import sys
from pathlib import Path

import capstone
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts/gui"))
import iso_ui_patch as P

VU4 = ROOT / "firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha15_unpacked_unpacked/lib/viewUnified4.so"
pytestmark = pytest.mark.skipif(not VU4.is_file(), reason="viewUnified4.so 3.21 no disponible")


def _setvalid(d: bytes) -> dict[int, int]:
    """id de fila → valor de `setValid` en las llamadas fijas de 0xf0b1a…0xf0be0."""
    md = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_THUMB)
    fila, out = None, {}
    for i in md.disasm(d[0xF0B1A:0xF0BE0], 0xF0B1A):
        if i.mnemonic == "movs" and i.op_str.startswith("r1"):
            fila = int(i.op_str.split("#")[1], 16)
        elif i.mnemonic == "movs" and i.op_str.startswith("r2") and fila is not None:
            out[fila] = int(i.op_str.split("#")[1], 16)
    return out


def test_parche_e_idempotencia():
    d = VU4.read_bytes()
    n = P.patch(d)
    assert P.patch(n) == n
    assert sum(a != b for a, b in zip(d, n)) == 3
    antes, despues = _setvalid(d), _setvalid(n)
    assert {f: antes[f] for f in (0x1F, 0x20, 0x21)} == {0x1F: 0, 0x20: 0, 0x21: 0}
    assert {f: despues[f] for f in (0x1F, 0x20, 0x21)} == {0x1F: 1, 0x20: 1, 0x21: 1}
    assert {f: v for f, v in despues.items() if f not in (0x1F, 0x20, 0x21)} == {f: v for f, v in antes.items() if f not in (0x1F, 0x20, 0x21)}


def test_filas_existen_en_la_tabla():
    """Las filas que se dejan visibles existen en la tabla de menú de la vista (ids 0x1f–0x21 = 32000/40000/51200, texto 0x0204xxxx)."""
    d = VU4.read_bytes()
    va = lambda a: a - 0x8000  # segundo LOAD: vaddr 0x19a000 en el fichero 0x192000
    ids = {struct.unpack_from("<I", d, va(0x1B1164 + 0x28 * i) + 8)[0]: struct.unpack_from("<I", d, va(0x1B1164 + 0x28 * i) + 0xC)[0]
           for i in range(0x22)}
    assert {i: ids[i] & 0xFFFF for i in (0x1F, 0x20, 0x21)} == {0x1F: 0xEF54, 0x20: 0xEEE6, 0x21: 0xEF4D}


def test_rechaza_otra_version():
    with pytest.raises(AssertionError):
        P.patch(b"\0" * 0x100000)
