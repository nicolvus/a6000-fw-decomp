"""E26-R13 — Offline: provenance of the 3-slow + 2-fast LED pattern (Loader2 vs Loader3).

Static only: reads the existing ``bootloader.bin`` dump through ``r13_loader3`` and Sony's public
kernel headers kept under ``analysis/session18``; never touches the camera.
"""

import re
from pathlib import Path

import r13_loader3 as L

ROOT = Path(__file__).resolve().parents[1]
REGS_TIMER = (
    ROOT
    / "session18/main/sony-oss-extracted/linux/arch/arm/mach-cxd90014/include/mach/regs-timer.h"
)
TIMEX = REGS_TIMER.parent / "timex.h"

LOADER2 = (
    0xC0030000,
    0x600,
    0xC0030000 + 0x6C00,
)  # EXBL: Loader2 at file 0x600..0x7200
LOADER3 = (0xC01F0000, 0x22800, 0xC01F0000 + 43 * 0x800)
LED_L2, LED_L3 = 0xC0030C7C, 0xC01F3B74
D = 0x3D0900  # literal at c01f3c40 / c0030d00 (verified in both loaders)
TIMER_CTRL_L3 = (
    0x31  # str r2,[r0] in c01f4fea: TMCS_FREERUN | TMCK_DIV2, then 0x1031 adds TMST
)


def use(region: tuple[int, int, int]) -> None:
    L.BASE, L.OFF, L.END = region


def led_triple(n: int) -> tuple[int, int, int]:
    """(LDR2, LNG, SHT) pulse counts for |code| = n: n/1000, (n%1000)/100, n%100."""
    return n // 1000, (n % 1000) // 100, n % 100


def loader2_led_arg(err: int) -> int:
    """Loader2 calls ``sub.w r0, r4, #0x3e8`` (c00303e4) before the LED routine."""
    return err - 1000


def visual_3_then_2(n: int) -> bool:
    """Non-empty groups, in time order LDR2 -> LNG -> SHT, are exactly 3 then 2."""
    return [c for c in led_triple(n) if c] == [3, 2]


def tick_hz(ctrl: int, input_hz: int = 4_000_000) -> int:
    """Timer clock = input / 2**TMCK (regs-timer.h); input 4 MHz from timex.h comments (non-FPGA)."""
    return input_hz >> (ctrl & 7)


def timeline(n: int, tick: int) -> list[tuple[str, float]]:
    """One LED cycle of c01f3b74 / c0030c7c: [(label, seconds)]; on and off phases last the same."""
    ldr2, lng, sht = led_triple(n)
    s = lambda t: t / tick
    out: list[tuple[str, float]] = []
    for label, cnt, delay in (
        ("LDR2", ldr2, D),
        ("LNG", lng, D >> 2),
        ("SHT", sht, D >> 3),
    ):
        out += [(f"{label} on", s(delay)), (f"{label} off", s(delay))] * cnt
        out.append((f"gap after {label}", s(D >> 1 if label != "SHT" else D)))
    return out


def minus_302_sites() -> dict[str, list[str]]:
    """Loader3 ldr-literal sites of -302, by containing function; and the pool words."""
    use(LOADER3)
    st = L.function_starts(L.call_edges())
    sites: dict[str, list[str]] = {}
    for a, _, _, lit in L.disasm(L.BASE + 0x28, L.END):
        if lit == 0xFFFFFED2:
            sites.setdefault(hex(L.containing(st, a)), []).append(hex(a))
    return sites


def identity() -> dict[str, object]:
    d = L.DATA
    l2 = d.find(b"Loader2 Ver.")
    return {
        "loader2_banner": d[l2 : l2 + 64].split(b"\0")[0].decode() if l2 >= 0 else None,
        "led_fn_callers_l3": sorted(hex(a) for a, _ in _callers(LOADER3, LED_L3)),
        "led_fn_callers_l2": sorted(hex(a) for a, _ in _callers(LOADER2, LED_L2)),
    }


def _callers(region: tuple[int, int, int], target: int) -> set[tuple[int, str]]:
    use(region)
    return L.call_edges().get(target, set())


def timer_constants() -> dict[str, int]:
    """TMCK/TMCS values and the non-FPGA input-clock comment, parsed from the public headers."""
    regs = REGS_TIMER.read_text()
    vals = {
        m.group(1): int(m.group(2), 16)
        for m in re.finditer(r"#\s*define\s+(TM\w+)\s+(0x[0-9a-fA-F]+)", regs)
    }
    assert "CLK=2MHz (count up rate = 4MHz)" in TIMEX.read_text()
    return vals


if __name__ == "__main__":
    print(identity())
    print("-302 sites:", minus_302_sites())
    tc = timer_constants()
    tick = tick_hz(TIMER_CTRL_L3)
    print(
        f"ctrl {TIMER_CTRL_L3:#x}: freerun={TIMER_CTRL_L3 & tc['TMCS_FREERUN'] == tc['TMCS_FREERUN']} tick={tick} Hz"
    )
    for n in (302, 3002, 3200):
        t = timeline(n, tick)
        print(
            n, led_triple(n), f"cycle {sum(s for _, s in t):.2f} s", visual_3_then_2(n)
        )
