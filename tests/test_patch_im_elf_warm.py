"""Verifica el parche de la compuerta del WBI en `im.elf` (scripts/gui/patch_im_elf_warm.py).

Sin cámara: comprueba la aritmética de offsets, que solo cambian 4 bytes y, si el firmware extraído está
en disco, que el fichero real tiene los bytes esperados en `0x9F44` y que el resultado desensambla a
`movs r0,#1 ; bx lr`.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("patch_im_elf_warm", RAIZ / "scripts/gui/patch_im_elf_warm.py")
assert SPEC and SPEC.loader
MOD = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MOD
SPEC.loader.exec_module(MOD)

IM_ELF_REAL = (RAIZ / "firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image"
               "/dev/nflasha15_unpacked_unpacked/bin/im.elf")


def test_parchea_solo_cambia_los_cuatro_bytes_de_la_compuerta() -> None:
    falso = bytearray(0x4000)
    falso[MOD._offset(MOD.GATE_VA):MOD._offset(MOD.GATE_VA) + 4] = MOD.GATE_ORIGINAL
    salida = MOD.parchea(bytes(falso))
    distintos = [i for i in range(len(falso)) if falso[i] != salida[i]]
    assert distintos == list(range(MOD._offset(MOD.GATE_VA), MOD._offset(MOD.GATE_VA) + 4))
    assert salida[MOD._offset(MOD.GATE_VA):MOD._offset(MOD.GATE_VA) + 4] == MOD.GATE_PARCHE


def test_no_parchea_dos_veces_ni_otro_fichero() -> None:
    sin_marca = bytes(0x4000)
    with pytest.raises(AssertionError):
        MOD.parchea(sin_marca)


@pytest.mark.skipif(not IM_ELF_REAL.exists(), reason="firmware extraído no disponible")
def test_im_elf_real_tiene_los_bytes_esperados() -> None:
    original = IM_ELF_REAL.read_bytes()
    parcheado = MOD.parchea(original)
    assert len(parcheado) == len(original)
    ef = MOD._offset(MOD.GATE_VA)
    assert parcheado[ef:ef + 4] == b"\x01\x20\x70\x47"      # movs r0,#1 ; bx lr
    assert parcheado[:0x34] == original[:0x34]               # cabecera ELF intacta
    assert sum(a != b for a, b in zip(original, parcheado)) == 4
