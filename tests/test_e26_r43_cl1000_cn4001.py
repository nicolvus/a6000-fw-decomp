"""E26-R43 — CL1000/BOOT_MAIN (bit0) no tiene salida trazable hacia CN4001 (Multi externo);
BOOT_SERIAL_IN (H21, bit1) sí, y llega al pin 10 (etiqueta de conector "AD_JACK_IN"), no al
pin 9 como daban por hecho R11/R19/R20/R29.

Lee `references/manuals/a6000_service_L3.pdf` con `pdftotext -bbox` y `pdftocairo -svg` (sin
rasterizar). Se omite si falta el PDF o las herramientas de poppler. Nada toca la cámara.
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "analysis" / "e26-recovery")]

from r43_cl1000_cn4001_trace import (  # type: ignore[import-not-found]
    PAGE_CLKBOOT,
    PAGE_CN4001,
    PDF,
    bbox_words,
    clkboot_export_target,
    cn4001_label_to_pin,
    pin_rows,
    svg_segments,
)


def _skip_if_missing() -> None:
    if not PDF.exists() or shutil.which("pdftotext") is None or shutil.which("pdftocairo") is None:
        pytest.skip("falta el PDF o poppler-utils (pdftotext/pdftocairo)")


def test_boot_serial_in_llega_al_pin_10_no_al_9():
    _skip_if_missing()
    words37 = bbox_words(PAGE_CN4001)
    segs37 = svg_segments(PAGE_CN4001, (150, 440), (625, 700))
    pins = pin_rows(words37)
    assert cn4001_label_to_pin("BOOT_SERIAL_IN", words37, segs37, pins) == 10
    assert cn4001_label_to_pin("DEBUG_UART0_RXD", words37, segs37, pins) == 9
    assert cn4001_label_to_pin("XRESET_REQ", words37, segs37, pins) == 7
    assert cn4001_label_to_pin("AD_JACK_IN", words37, segs37, pins) == 11


def test_h21_bit1_exporta_boot_serial_in():
    _skip_if_missing()
    words24 = bbox_words(PAGE_CLKBOOT)
    segs24 = svg_segments(PAGE_CLKBOOT, (375, 560), (210, 260))
    target = clkboot_export_target("H21", words24, segs24)
    assert target is not None
    assert target[2] == "BOOT_SERIAL_IN"


def test_p7_bit0_boot_main_sin_salto_externo_trazable():
    """CL1000 (P7/BOOT_MAIN, MODEREG bit 0) no tiene, en la hoja CLK BOOT, ningún trazo que
    llegue a una etiqueta de exportación global: sigue siendo un punto de prueba interno, sin
    atajo por el conector Multi externo."""
    _skip_if_missing()
    words24 = bbox_words(PAGE_CLKBOOT)
    segs24 = svg_segments(PAGE_CLKBOOT, (375, 560), (210, 260))
    assert clkboot_export_target("P7", words24, segs24) is None
