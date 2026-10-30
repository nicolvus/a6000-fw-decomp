"""E26-R12 — pruebas offline de la decodificación de códigos de LED (BootROM y Loader2).

Solo leen volcados existentes; no tocan la cámara. Informe: docs/capture/e26-r12-bootrom-static-audit.md
"""

import sys

ROOT = __import__("pathlib").Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "analysis" / "e26-recovery"))

r12 = __import__("r12-loader2-led-codes")


def test_bootrom_pattern_formula():
    assert r12.led_pattern_bootrom(0x1001) == (0, 1)
    assert r12.led_pattern_bootrom(0x3004) == (2, 4)


def test_bootrom_cannot_emit_three_slow():
    assert max(r12.led_pattern_bootrom(c)[0] for c in r12.BOOTROM_ERROR_CODES) == 2


def test_loader2_minus_302_is_three_medium_two_fast():
    assert r12.led_pattern_loader2(-302) == (0, 3, 2)


def test_loader2_minus_302_literal_present_in_dump():
    users = r12.literal_users(r12.LOADER.read_bytes(), {-302})
    assert len(users[-302]) >= 3
