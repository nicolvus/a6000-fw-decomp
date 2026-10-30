"""E26-R13 — Offline static helpers for the Loader3 prefix (runtime 0xc01f0000, INFO 5 = 43 pages).

Reads ``bootloader.bin`` from the existing dumps; never touches the camera.
Thumb-only sweep: the ARM entry stub (0xc01f0000..0x28) is skipped; data pools can yield
false BL hits, so every decisive edge is re-read with ``disasm`` before it is cited in the report.
"""

import struct
from collections import defaultdict
from pathlib import Path

from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs

ROOT = Path(__file__).resolve().parents[1]
LOADER = ROOT / "camera-dumps/updater-20261020-175427/bootloader.bin"
BASE, OFF = 0xC01F0000, 0x22800
END = BASE + 43 * 0x800  # INFO 5: 43 pages, runtime 0xc01f0000..0xc0205800
LED_FN = 0xC01F3B74
DATA = LOADER.read_bytes()
_MD = Cs(CS_ARCH_ARM, CS_MODE_THUMB)


def u32(addr: int) -> int:
    o = addr - BASE + OFF
    return struct.unpack("<I", DATA[o : o + 4])[0]


def s32(v: int) -> int:
    return v - (1 << 32) if v >> 31 else v


def disasm(a: int, b: int) -> list[tuple[int, str, str, int | None]]:
    """(addr, mnemonic, operands, literal-pool value if ldr [pc])."""
    out, pc = [], a
    while pc < b:
        o = pc - BASE + OFF
        ins = next(_MD.disasm(DATA[o : o + 4], pc, 1), None)
        if ins is None:
            pc += 2
            continue
        lit = None
        if ins.mnemonic.startswith("ldr") and "[pc," in ins.op_str:
            imm = int(ins.op_str.split("#")[1].rstrip("]"), 16)
            lit = u32(((ins.address + 4) & ~3) + imm)
        out.append((ins.address, ins.mnemonic, ins.op_str, lit))
        pc += ins.size
    return out


def _hw(a: int) -> int:
    o = a - BASE + OFF
    return struct.unpack("<H", DATA[o : o + 2])[0]


def call_edges() -> dict[int, set[tuple[int, str]]]:
    """target -> {(call site, 'bl'|'blx'|'b.w')} decoded from Thumb-2 BL/BLX/B.W pairs."""
    edges: dict[int, set[tuple[int, str]]] = defaultdict(set)
    for a in range(BASE + 0x28, END - 2, 2):
        h1, h2 = _hw(a), _hw(a + 2)
        if (h1 & 0xF800) != 0xF000 or (h2 & 0xC000) != 0xC000:
            continue
        s, j1, j2 = (h1 >> 10) & 1, (h2 >> 13) & 1, (h2 >> 11) & 1
        i1, i2 = (~(j1 ^ s)) & 1, (~(j2 ^ s)) & 1
        imm = (
            (s << 24)
            | (i1 << 23)
            | (i2 << 22)
            | ((h1 & 0x3FF) << 12)
            | ((h2 & 0x7FF) << 1)
        )
        imm -= (1 << 25) if s else 0
        t = a + 4 + imm
        kind = {
            0x1000: "bl",
            0x5000: "bl",
            0x4000: "blx",
            0x0000: "b.w",
            0x1000 | 0: "bl",
        }.get(h2 & 0x5000, "b.w")
        edges[t & ~3 if kind == "blx" else t].add((a, kind))
    return edges


def function_starts(edges: dict[int, set[tuple[int, str]]]) -> list[int]:
    """BL targets inside the prefix plus every ``push {.., lr}`` prologue."""
    starts = {t for t in edges if BASE <= t < END}
    for a in range(BASE + 0x28, END - 2, 2):
        h = _hw(a)
        if (h & 0xFF00) == 0xB500 or (h == 0xE92D and _hw(a + 2) & 0x4000):
            starts.add(a)
    return sorted(starts)


def containing(starts: list[int], addr: int) -> int:
    best = starts[0]
    for s in starts:
        if s > addr:
            break
        best = s
    return best


def cstr(addr: int) -> str | None:
    if not BASE <= addr < END + 0x8000:
        return None
    o = addr - BASE + OFF
    d = DATA[o : o + 96]
    i = d.find(b"\0")
    s = d[:i] if i > 3 else b""
    return (
        s.decode("latin1") if s and all(32 <= c < 127 or c == 10 for c in s) else None
    )


def listing(a: int, b: int) -> str:
    """Disassembly with ldr/adr strings, literal values and BL targets annotated."""
    lines = []
    for ad, m, o, lit in disasm(a, b):
        note = ""
        if lit is not None:
            note = (
                f"; ={lit:#x}"
                + (f" {s32(lit)}" if lit >> 31 else "")
                + (f' "{cstr(lit)!r}"' if cstr(lit) else "")
            )
        elif m == "adr":
            t = ((ad + 4) & ~3) + int(o.split("#")[1], 16)
            note = f'; "{cstr(t)!r}"' if cstr(t) else ""
        lines.append(f"{ad:x}: {m} {o} {note}".rstrip())
    return "\n".join(lines)


def build_graph() -> tuple[dict[int, set[int]], list[int]]:
    """caller function -> callee functions (direct BL/BLX/B.W only); 'log + push' thunks are merged."""
    edges = call_edges()
    starts = function_starts(edges)
    targets = {t for t in edges if BASE <= t < END}
    merged = [
        s
        for s in starts
        if not any(0 < s - t <= 6 and t in targets and s not in targets for t in starts)
    ]
    g: dict[int, set[int]] = defaultdict(set)
    for t, sites in edges.items():
        if not BASE <= t < END:
            continue
        for site, _ in sites:
            g[containing(merged, site)].add(
                containing(merged, t) if t in merged or t >= BASE else t
            )
    return g, merged


def path_from(g: dict[int, set[int]], src: int, dst: int) -> list[int] | None:
    prev, todo = {src: 0}, [src]
    while todo:
        n = todo.pop(0)
        if n == dst:
            out = [n]
            while prev[out[-1]]:
                out.append(prev[out[-1]])
            return out[::-1]
        for m in sorted(g.get(n, ())):
            if m not in prev:
                prev[m] = n
                todo.append(m)
    return None
