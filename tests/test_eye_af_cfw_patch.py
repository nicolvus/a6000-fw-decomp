"""Pruebas del parche de Eye AF nativo en `av-cam.bin` (CFW, sin APK).

Requieren la imagen oficial de 3.21 (no versionada). Ruta: `AVCAM_BIN` o `analysis/rea-independent/input/av-cam.bin`.
"""
from __future__ import annotations

import hashlib
import os
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "scripts/cfw"))

import eye_af_patch as p

AVCAM = Path(os.environ.get("AVCAM_BIN", RAIZ / "analysis/rea-independent/input/av-cam.bin"))


@pytest.fixture(scope="module")
def original() -> bytes:
    if not AVCAM.exists():
        pytest.skip(f"falta {AVCAM} (firmware no versionado)")
    return p.leer(AVCAM)


def test_sitio_sin_aplicar(original: bytes) -> None:
    assert p.estado(original) == "sin aplicar"
    assert original[p._off(p.SITE):p._off(p.SITE) + 2] == p.PATCH[p.SITE][0]
    assert f"{p.SITE:#010x}" in p.describir(original)


def test_desensamblado_del_sitio(original: bytes) -> None:
    """`38d1` es un `bne`: anularlo deja caer la ejecución en el bloque del ojo."""
    capstone = pytest.importorskip("capstone")
    md = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_THUMB)
    cmp_, salto = list(md.disasm(original[p._off(0x437B723A):p._off(0x437B723A) + 4], 0x437B723A))
    assert cmp_.mnemonic == "cmp" and cmp_.op_str.startswith("r6, #2")
    assert salto.mnemonic == "bne" and salto.op_str == f"#{0x437B72B0:#x}"
    nop, = md.disasm(p.PATCH[p.SITE][1], p.SITE)
    assert nop.mnemonic == "nop"


def test_aplicar_solo_cambia_dos_bytes(original: bytes) -> None:
    nuevo, diff = p.apply_bytes(original)
    assert {d["address"] for d in diff} == p.allowed_addresses() == {0x437B723C, 0x437B723D}
    assert nuevo[0x437B723C - p.BASE:0x437B723E - p.BASE] == p.PATCH[p.SITE][1]
    assert len(nuevo) == p.TAMANO_INPUT
    assert p.estado(nuevo) == "aplicado"


def test_idempotente_y_reversible(original: bytes) -> None:
    aplicado, _ = p.apply_bytes(original)
    otra_vez, diff_vacio = p.apply_bytes(aplicado)
    assert otra_vez == aplicado and diff_vacio == []
    assert p.restore_bytes(original) == original
    assert hashlib.sha256(p.restore_bytes(aplicado)).hexdigest() == hashlib.sha256(original).hexdigest()


def test_bytes_inesperados_abortan(original: bytes) -> None:
    roto = bytearray(original)
    roto[0x437B723C - p.BASE:0x437B723E - p.BASE] = b"\x00\x00"
    with pytest.raises(ValueError):
        p.apply_bytes(bytes(roto))


def test_cli_aplicar_check_revertir(original: bytes, tmp_path: Path) -> None:
    copia = tmp_path / "av-cam.bin"
    copia.write_bytes(original)

    assert p.main(["--check", str(copia)]) == 3  # 3 = sin aplicar
    assert p.main(["--apply", str(copia)]) == 0
    assert p.estado(copia.read_bytes()) == "aplicado"
    assert p.main(["--check", str(copia)]) == 0
    assert p.main(["--revert", str(copia)]) == 0
    assert hashlib.sha256(copia.read_bytes()).hexdigest() == hashlib.sha256(original).hexdigest()


def test_tamano_distinto_aborta(tmp_path: Path) -> None:
    falso = tmp_path / "av-cam.bin"
    falso.write_bytes(b"\x00" * 16)
    with pytest.raises(SystemExit):
        p.leer(falso)
