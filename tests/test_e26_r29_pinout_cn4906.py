"""E26-R29 — verificación del trazado por píxel del esquema CN4906 (BIONZ+Darwin combinado)."""

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "analysis" / "e26-recovery"))

spec = importlib.util.spec_from_file_location(
    "r29", ROOT / "analysis/e26-recovery/r29_pinout_pixel_trace.py"
)
r29 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r29)

r11 = __import__("r11-pinout-reconstruction")

# (x, (y_top_esperado, y_bottom_esperado)) — tolerancia 4 px por redondeo de renderizado
EXPECTED = {
    2736: (308, 1015),  # pin6 UART_RXD_DWN <- DWN_UART_RXD
    2778: (349, 1056),  # pin7 UART_TXD_DWN <- DWN_UART_TXD
    2819: (392, 1098),  # pin8 NSRST <- MD0_DWN
    2861: (432, 1139),  # pin9 TDO <- TDO_DWN
    2903: (510, 1180),  # pin11 TCK(SWCLK) <- TCK_DWN (unido a SWCLK)
    2944: (552, 1222),  # pin12 TMS(SWDIO) <- TMS_DWN (unido a SWDIO)
    2986: (599, 1263),  # pin13 TDI <- TDI_DWN
    3027: (641, 1306),  # pin14 NTRST <- TRST_DWN
    3068: (676, 1348),  # pin15 DEBUG_MODE <- XDWN_RESET (unido a VIO_FLD)
}


def test_pdf_disponible():
    assert r29.PDF.exists(), "manual de servicio ausente"


def test_trazado_por_pixel_reproduce_el_cableado_esperado():
    segs = r29.main()
    assert set(segs) == set(EXPECTED)
    for x, (etop, ebot) in EXPECTED.items():
        top, bot = segs[x]
        assert abs(top - etop) <= 4, f"x={x} tope {top} vs esperado {etop}"
        assert abs(bot - ebot) <= 4, f"x={x} pie {bot} vs esperado {ebot}"


def test_cn4906_tiene_18_pines_no_32():
    assert set(r11.CN4906_PINS) == set(range(1, 19))
    assert 31 not in r11.CN4906_PINS and 32 not in r11.CN4906_PINS


def test_cn4906_pin10_rtck_sin_red_externa():
    assert r11.CN4906_PINS[10] == "RTCK"
    assert r11.CN4906_SOURCES[10][0] == "(sin red externa)"


def test_cn4001_pin1_es_vbus_no_data():
    assert r11.CN4001_PINS[1] == "USB_VBUS"
    assert r11.CN4001_PINS[2] == "USB_D-"
    assert r11.CN4001_PINS[3] == "USB_D+"
