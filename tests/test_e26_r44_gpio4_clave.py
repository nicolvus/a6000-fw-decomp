"""E26-R44 — mecanismo exacto de la comprobación de clave en `main` del BootROM (una sola
palabra de 32 bits, comparación en una instrucción, `error_blink` nunca retorna) y candidato
de pin para `GPIO4.22` (bola N8 / `GPIO_SB_5`, la única sin red de cámara en el bloque "GPIO
SYS"). Nada toca la cámara; se omite si falta el volcado o Capstone/poppler.
"""

from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
BOOTROM = ROOT / "analysis/camera-dumps/updater-20261020-175427/bootrom.bin"
MANUAL = ROOT / "references/manuals/a6000_service_L3.pdf"
BASE = 0xFFFF0000


def _disasm(start: int, end: int):
    pytest.importorskip("capstone")
    from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs

    if not BOOTROM.exists():
        pytest.skip("falta bootrom.bin")
    rom = BOOTROM.read_bytes()
    md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
    return list(md.disasm(rom[start - BASE : end - BASE], start))


def test_comparacion_de_clave_es_una_sola_palabra_recibida_vs_guardada():
    ins = _disasm(0xFFFF11E6, 0xFFFF11FE)
    mnems = [(i.mnemonic, i.op_str) for i in ins]
    assert ("ldrd", "r0, r1, [sp, #4]") in mnems
    assert ("cmp", "r1, r0") in mnems
    # si coinciden, salta a serial_entry (0xffff0fa0) sin más comprobación
    assert any(i.mnemonic == "bl" and "0xffff0fa0" in i.op_str for i in ins)


def test_error_blink_es_bucle_infinito():
    ins = _disasm(0xFFFF0D62, 0xFFFF0E0A)
    last = ins[-1]
    assert last.mnemonic == "b" and "0xffff0db0" in last.op_str


def test_gpio4_bit22_salta_directo_a_serial_entry_sin_clave():
    ins = _disasm(0xFFFF10E6, 0xFFFF1104)
    # ubfx r0, r0, #0x16(=22), #1  -- extrae el bit 22
    assert any(i.mnemonic == "ubfx" and i.op_str.startswith("r0, r0, #0x16, #1") for i in ins)
    assert any(i.mnemonic == "cbz" for i in ins)  # si ==0, no salta
    assert any(i.mnemonic == "bl" and "0xffff0fa0" in i.op_str for i in ins)  # si !=0, serial_entry


def test_gpio_sb_5_es_la_unica_sin_red_de_camara():
    if not MANUAL.exists() or shutil.which("pdftotext") is None:
        pytest.skip("falta el manual o pdftotext")
    html = subprocess.run(
        ["pdftotext", "-bbox", "-f", "26", "-l", "26", str(MANUAL), "-"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    rows = [
        (float(m[2]), float(m[1]), m[5])
        for m in re.finditer(
            r'xMin="([0-9.]+)" yMin="([0-9.]+)" xMax="([0-9.]+)" yMax="([0-9.]+)">([^<]*)',
            html,
        )
    ]
    sb_rows = {
        txt: y0 for y0, x0, txt in rows if re.fullmatch(r"GPIO_SB_\d", txt) and x0 < 800
    }
    # etiqueta de destino de cámara en la franja x~940-950 a la misma altura que cada bola
    has_dest = {
        name: any(abs(y0 - y) < 3 and x0 > 900 for y0, x0, _txt in rows)
        for name, y in sb_rows.items()
    }
    assert has_dest["GPIO_SB_0"] is True
    assert has_dest["GPIO_SB_4"] is True
    assert has_dest["GPIO_SB_6"] is True
    assert has_dest["GPIO_SB_5"] is False
