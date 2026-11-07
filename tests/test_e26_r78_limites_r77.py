"""E26-R78: cierra los límites de R77 (intérprete de secuencias, acciones 09/0a/13/14, alcance de 0x1fee2)."""
from __future__ import annotations

import bisect
import re
import struct
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
DZ = ROOT / "firmware/extracted/fw321/firmware.tar_unpacked/0640_darwin/darwin_core.bin"
capstone = pytest.importorskip("capstone")
pytestmark = pytest.mark.skipif(not DZ.is_file(), reason="firmware original ausente")
B = 0x4200
C, H, S = 0x1E4AA, 0x1E4C2, 0x1E4F6  # avanzar+seguir (0x40), retener (0x80), avanzar+ceder (bic 0x40)


@pytest.fixture(scope="module")
def fw():
    d = DZ.read_bytes()
    md = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_THUMB | capstone.CS_MODE_MCLASS)
    ins, a = [], B
    while a < B + len(d):
        ok = False
        for i in md.disasm(d[a - B:a - B + 0x1000], a):
            ins.append((i.address, i.size, i.mnemonic, i.op_str))
            a, ok = i.address + i.size, True
        if not ok:
            a += 2
    return d, ins


def _u32(d, a):
    return struct.unpack_from("<I", d, a - B)[0]


def _text(fw, a, n):
    return [f"{m} {o}" for ad, _, m, o in fw[1] if ad >= a][:n]


def _calls_to(fw, t):
    return [a for a, _, m, o in fw[1] if m in ("bl", "b.w") and o == f"#{t:#x}"]


def _func(d, tab, i):
    t, n = _u32(d, tab), d[tab + 4 - B]
    return next(_u32(d, t + 8 * k + 4) & ~1 for k in range(n + 2) if d[t + 8 * k - B] == i)


def test_tres_funciones_del_interprete(fw):
    for a, op in ((H, "orr r0, r0, #0x80"), (C, "orr r0, r0, #0x40"), (S, "bic r0, r0, #0x40")):
        assert _text(fw, a, 6)[3:6] == ["ldrh r0, [r4, #0x10]", op, "strh r0, [r4, #0x10]"]
    # 0x1e234: 0x80 salta el avance; 0x40 (al final) devuelve 1; 0x1e33e repite si devuelve 1
    assert _text(fw, 0x1E25A, 3) == ["ldrh r6, [r5, #0x10]", "lsls r7, r6, #0x18", "bmi #0x1e2b6"]
    assert _text(fw, 0x1E322, 5) == ["ldrh r0, [r5, #0x10]", "lsls r0, r0, #0x19", "bpl #0x1e338",
                                      "mov.w r8, #1", "b #0x1e338"]
    assert _text(fw, 0x1E3C2, 6)[2:5] == ["bl #0x1e234", "cmp r0, #0", "bne #0x1e346"]


def test_emulacion_minima_del_interprete(fw):
    uc = pytest.importorskip("unicorn")
    from unicorn.arm_const import UC_ARM_REG_LR, UC_ARM_REG_R0, UC_ARM_REG_SP

    d = fw[0]
    ram, desc, tab, seq, st = 0x20000000, 0x20001000, 0x20001100, 0x20001200, 0x20001300

    def run(ids, passes):
        u = uc.Uc(uc.UC_ARCH_ARM, uc.UC_MODE_THUMB | uc.UC_MODE_MCLASS)
        u.mem_map(0x4000, 0x30000)
        u.mem_write(B, d)
        u.mem_map(ram, 0x100000)
        for a in (0x5C9E, 0x5C88, 0x16ADC, 0x1E192, 0x1E1D2, 0x1E0E4):
            u.mem_write(a, b"\x70\x47")  # bx lr
        u.mem_write(0x25738, b"\x00\x20\x70\x47")
        acts = [(0, C), (1, H), (2, S), (4, S)]
        u.mem_write(tab, b"".join(struct.pack("<BxxxI", i, f | 1) for i, f in acts))
        u.mem_write(seq, bytes(ids))
        u.mem_write(seq + 0x10, struct.pack("<I", seq))
        u.mem_write(desc, struct.pack("<IIIII", tab, 4, st, st + 1, seq + 0x10) + bytes([4, 0, 0, 0, 0, 0, 0, 0x20]))
        u.mem_write(st, bytes([0, ids[0]]))
        u.mem_write(0x20000F00, b"\x70\x47")
        calls = []
        for a, nm in ((C, "C"), (H, "H"), (S, "S")):
            u.hook_add(uc.UC_HOOK_CODE, lambda _u, _a, _z, n: calls.append(n), begin=a, end=a, user_data=nm)
        out = []
        for _ in range(passes):
            calls.clear()
            u.reg_write(UC_ARM_REG_R0, desc)
            u.reg_write(UC_ARM_REG_SP, ram + 0x80000)
            u.reg_write(UC_ARM_REG_LR, 0x20000F01)
            u.emu_start(0x1E33F, 0x20000F00)
            out.append(("".join(calls), tuple(u.mem_read(st, 2))))
        return out

    # 0x40: avanza y sigue en el mismo paso; sin bandera (0x1e4f6): avanza y cede; al final id==n: termina
    assert run([0, 0, 2, 0, 4], 3) == [("CCS", (3, 0)), ("C", (4, 4)), ("", (4, 4))]
    assert run([1, 0, 4], 3) == [("H", (0, 1))] * 3  # 0x80: no avanza, reintenta
    assert run([2, 2, 0, 4], 3) == [("S", (1, 2)), ("S", (2, 0)), ("C", (3, 4))]


def _closure(fw, roots):
    ins, d = fw[1], fw[0]
    addr = [x[0] for x in ins]
    starts = sorted(a for a, _, m, o in ins if m in ("push", "push.w") and "lr" in o)

    def body(s):
        i = bisect.bisect_left(addr, s)
        lim = starts[bisect.bisect_right(starts, s + 2)]
        out, mx = [], 0
        while i < len(ins) and ins[i][0] < lim:
            a, z, m, o = ins[i]
            out.append(ins[i])
            i += 1
            t = re.search(r"#(0x[0-9a-f]+)$", o)
            is_br = m != "bl" and (m.startswith("b") and m not in ("bic", "bics", "bx") or m in ("cbz", "cbnz"))
            if t and is_br and a < int(t.group(1), 0) < lim:
                mx = max(mx, int(t.group(1), 0))
            if ((m in ("pop", "pop.w") and "pc" in o) or (m == "bx" and o == "lr") or (m in ("b", "b.w") and t)) and a + z > mx:
                break
        return out

    seen, stack = set(), list(roots)
    while stack:
        f = stack.pop()
        if f in seen or not B <= f < B + len(d):
            continue
        seen.add(f)
        b = body(f)
        hi = b[-1][0] + b[-1][1]
        for a, _, m, o in b:
            if m in ("bl", "b.w", "b") and o.startswith("#"):
                t = int(o[1:], 0)
                if m == "bl" or not f <= t < hi:
                    stack.append(t)
    return seen, body


def test_acciones_09_0a_13_14(fw):
    d = fw[0]
    assert [_func(d, 0x28FDC, i) for i in (9, 0xA, 0x13, 0x14)] == [0x186F0, 0x1871E, 0x1896A, 0x1898C]
    assert _text(fw, 0x18710, 4) == ["bl #0x16ca4", "mov r0, r4", "pop.w {r4, lr}", "b.w #0x1e4f6"]  # 09: avanza y cede
    assert _text(fw, 0x18722, 8) == ["bl #0x16d0c", "cmp r0, #0", "bne #0x18676", "mov r0, r4", "pop.w {r4, lr}",
                                      "b.w #0x1e4c2", "b #0x18676", "push {r4, lr}"]  # 0a: S acabada -> avanza; si no, retiene
    assert _text(fw, 0x18978, 5) == ["bl #0x16da2", "b #0x18982", "bl #0x16d84", "mov r0, r4", "pop.w {r4, lr}"]
    assert _text(fw, 0x18988, 1) == ["b.w #0x1e4f6"]  # 13: avanza y cede
    assert _text(fw, 0x18990, 8) == ["bl #0x16d9e", "cmp r0, #0", "mov r0, r4", "bne #0x189a2", "pop.w {r4, lr}",
                                      "b.w #0x1e4c2", "pop.w {r4, lr}", "b.w #0x1e4aa"]  # 14: espera o avanza y sigue
    assert _text(fw, 0x17900, 2) == ["ldr r0, [pc, #0x48]", "b.w #0x1e16e"] and _u32(d, 0x1794C) == 0x28DD4
    assert _text(fw, 0x1E16E, 3) == ["push {r4, lr}", "mov r2, r0", "ldrb r1, [r2, #0x14]"]

    def ids(a):
        out = []
        while d[a - B] < 0x32:
            out.append(d[a - B])
            a += 1
        return out

    assert ids(0x28DA1) == ids(0x28DAE) == [4, 5, 6, 7, 8, 0x2F, 9, 0xA, 0x2F, 0xB, 0x2F, 0xC]
    assert ids(0x28D8F) == [0xD, 0x1D] and ids(0x28D8B) == [0xD]
    roots = [0x186F0, 0x1871E, 0x1896A, 0x1898C] + [_func(d, 0x28DD4, i) for i in set(ids(0x28DAE) + [0xD, 0x1D])]
    seen, body = _closure(fw, roots)
    writers = {0xD116, 0xD18E, 0x1ECEC, 0x20C90, 0x20CB2, 0x20CD4, 0x20D00, 0x20D26, 0x20E0E, 0x20E98}
    assert seen & writers == {0xD116}  # ningún escritor de P4C/P4D/P4E; P4B solo vía 0xd116
    assert {0x16558, 0xD380, 0x16DC0} <= seen and 0x182D8 not in seen and 0x1961C not in seen
    # lecturas de S+0x32 / S+0x48 (S = 0x200036d8) en el cierre: solo el volcado de estado 0x18394
    hits = []
    for f in seen:
        reg = {}
        for a, _, m, o in body(f):
            r = re.match(r"(r\d+), \[pc, #(0x[0-9a-f]+)\]$", o)
            if m == "ldr" and r:
                reg[r.group(1)] = _u32(d, ((a + 4) & ~3) + int(r.group(2), 0))
                continue
            t = re.match(r"r\d+, \[(r\d+), #(0x[0-9a-f]+)\]$", o)
            if t and m.startswith(("ldr", "str")) and reg.get(t.group(1)) == 0x200036D8 and int(t.group(2), 16) in (0x32, 0x48):
                hits.append(a)
            reg.pop(o.split(",")[0], None)
    assert hits == [0x18394]


def test_p4b_solo_por_error_de_watchdog(fw):
    d = fw[0]
    assert _text(fw, 0x172FC, 2) == ["movw r1, #0x7148", "movs r0, #0x58"] and _text(fw, 0x1730E, 1) == ["bl #0x16dc0"]
    assert _text(fw, 0x16DEA, 1) == ["bl #0x16558"] and _text(fw, 0x165A8, 1) == ["bl #0xd380"]
    assert _text(fw, 0xD3A8, 3) == ["movs r1, #1", "movs r0, #0x40", "bl #0xd116"]
    assert _text(fw, 0xD174, 4) == ["movs r1, #1", "mov.w r0, #0x22c", "bl #0x51c0", "b #0xd186"]
    assert _u32(d, 0xD374) == 0x5407F and _u32(d, 0xD378) == 0x5444F and 0x5407F & 0x5444F & 0x40


def test_0x1fee2_solo_por_0x1984e(fw):
    d = fw[0]
    assert _calls_to(fw, 0x1FEE2) == [0x19880]
    assert sorted(_calls_to(fw, 0x1984E)) == [0xCEE8, 0x197D0, 0x1F22E, 0x1F262]
    assert not [o for o in range(0, len(d) - 3, 2) if _u32(d, o + B) in (0x1FEE2, 0x1FEE3, 0x1984E, 0x1984F)]
    assert _calls_to(fw, 0x197CE) == [0x1B138] and _calls_to(fw, 0xCEE6) == [0x1B274]
    assert _calls_to(fw, 0x1B260) == [0x765E] and _u32(d, 0x295C4) == 0x1B137 and _u32(d, 0x25B70) == 0x75F1
    assert _text(fw, 0x1BFB6, 1) == ["bl #0x1f362"] and _calls_to(fw, 0x1F362) == [0x1BFB6]
    assert {_u32(d, 0x2A39C + 8 * k) for k in range(95)} == {0x1BFB3}
    assert _text(fw, 0x1F36A, 1) == ["b #0x1f0a0"] and _text(fw, 0x1F22C, 2) == ["movs r0, #1", "bl #0x1984e"]
    assert d[0x1F0F0 + 8 - B] == (0x1F22C - 0x1F0F0) >> 1  # tbb 0x1f0ec, índice 8 (orden 0x60) -> 0x1f22c
