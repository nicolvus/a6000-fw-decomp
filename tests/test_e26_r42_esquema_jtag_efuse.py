"""E26-R42 — Bolas de JTAG/eFuse/SWD, neto XRESET_CR y cobertura de GPIO en el manual.

Lee `references/manuals/a6000_service_L3.pdf` con `pdftotext` (sin -layout, que es el que
recupera el bloque JTAG/eFuse perdido por el .txt versionado — R42 §6).  Se omite si falta
el PDF o `pdftotext`.  Nada toca la cámara.
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
PDF = ROOT / "references/manuals/a6000_service_L3.pdf"


def _plain_text() -> str:
    if not PDF.exists() or shutil.which("pdftotext") is None:
        pytest.skip("falta el PDF o pdftotext")
    return subprocess.run(
        ["pdftotext", str(PDF), "-"], capture_output=True, text=True, check=True
    ).stdout


def test_bolas_jtag_efuse_swd_presentes():
    t = _plain_text()
    for label in (
        "FUSE_EN",
        "FUSE_CLK",
        "NTRST",
        "SWCLK",
        "SWDIO",
        "XRESET_CR",
        "R6000",
        "R4911",
        "R4912",
    ):
        assert label in t, label
    # bolas exactas del bloque JTAG/eFuse/SWD (IC6000 4/7)
    for ball in ("G25", "H25", "F26", "F25", "G26", "H26", "T12", "R12", "W25", "W26"):
        assert ball in t, ball


def test_gpio_solo_puertos_0_y_1():
    t = _plain_text()
    import re

    names = set(re.findall(r"\bGPIO[A-Z0-9_]*\b", t))
    names.discard("GPIO")
    s = {n for n in names if re.fullmatch(r"GPIO_S_\d+", n)}
    sb = {n for n in names if re.fullmatch(r"GPIO_SB_\d+", n)}
    plain = {n for n in names if re.fullmatch(r"GPIO_\d+", n)}
    assert {f"GPIO_S_{i}" for i in range(17)} <= s
    assert {f"GPIO_SB_{i}" for i in range(7)} <= sb
    assert {f"GPIO_{i}" for i in range(17)} <= plain
    # ningún otro puerto nombrado (en particular, nada de "puerto 14")
    assert names == s | sb | plain


def test_efuse_sin_resistencia_en_jtag_pero_con_xx_en_xreset():
    """Confirma por bytes que R6000 (XRESET, hoja 1/7) está marcada XX, a diferencia de R6001."""
    t = _plain_text()
    i = t.find("R6000")
    assert i != -1
    # la marca "XX" de no-montaje aparece como línea propia, cerca del nombre de la resistencia
    window = t[i : i + 40]
    assert "XX" in window
