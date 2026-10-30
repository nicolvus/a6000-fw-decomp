"""E26-R13 — pruebas offline de la procedencia del patrón LED (Loader2 vs Loader3).

Solo leen volcados y cabeceras existentes; no tocan la cámara. Informe: docs/capture/e26-r13-led-error-provenance.md
"""

import importlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "analysis" / "e26-recovery"))

r13 = importlib.import_module("r13-led-provenance")
L = importlib.import_module("r13_loader3")


def test_loader2_banner_and_two_led_routines():
    ident = r13.identity()
    assert ident["loader2_banner"].startswith("Loader2 Ver.33.01.90")
    assert ident["led_fn_callers_l3"] == ["0xc01f1264"]  # única llamada en Loader3
    assert ident["led_fn_callers_l2"] == ["0xc00303e8", "0xc0034a7a"]


def test_loader2_adds_1000_before_led_and_loader3_does_not():
    r13.use(r13.LOADER2)
    assert next(iter(L.disasm(0xC00303E4, 0xC00303EC)))[1:3] == (
        "sub.w",
        "r0, r4, #0x3e8",
    )
    assert r13.led_triple(-r13.loader2_led_arg(-304)) == (
        1,
        3,
        4,
    )  # etapa Loader2 siempre >= 1 pulso LDR2
    assert r13.led_triple(302) == (0, 3, 2)  # Loader3: sin pulso LDR2


def test_both_led_routines_share_delay_constant():
    for region, lit_at in ((r13.LOADER2, 0xC0030D48), (r13.LOADER3, 0xC01F3C40)):
        r13.use(region)
        assert L.u32(lit_at) == r13.D


def test_minus_302_sites_and_derived_codes():
    sites = r13.minus_302_sites()
    assert sorted(sites) == [
        "0xc01f2c98",
        "0xc01f2f24",
        "0xc01f3d8a",
        "0xc01f3e54",
        "0xc01f3eb6",
        "0xc01f3fd0",
        "0xc01f407e",
    ]
    assert sum(len(v) for v in sites.values()) == 9
    r13.use(r13.LOADER3)
    # c01f3de0 / c01f3eee / c01f40ca: ldr -302 seguido de subs #4 -> devuelven -306, no -302
    for a in (0xC01F3DE2, 0xC01F3EF0, 0xC01F40CC):
        assert L.disasm(a, a + 2)[0][1:3] == ("subs", "r0, r0, #4")


def test_compatible_codes_with_3_then_2():
    assert [n for n in range(1, 10000) if r13.visual_3_then_2(n)] == [302, 3002, 3200]


def test_timer_model_gives_two_second_d():
    tc = r13.timer_constants()
    assert r13.TIMER_CTRL_L3 & tc["TMCS_FREERUN"] == tc["TMCS_FREERUN"]
    assert r13.tick_hz(r13.TIMER_CTRL_L3) == 2_000_000
    assert r13.D / r13.tick_hz(r13.TIMER_CTRL_L3) == 2.0
    cycle = sum(s for _, s in r13.timeline(302, 2_000_000))
    assert cycle == 8.0
