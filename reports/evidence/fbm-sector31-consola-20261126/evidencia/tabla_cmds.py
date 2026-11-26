#!/usr/bin/env python3
"""Tabla de comandos del monitor FBM (0x7E7FAC, 29x12 B) con, por comando:
nombre, handler, tamaño, argc mínimo exigido (cmp r0,#N; ble -> ayuda), cadenas de ayuda y de
traza, parser de cada argumento (0x5FFE1A=HEX, 0x5FFE6E=DEC) y destinos `bl` fuera de .plt."""
import sys
sys.path.insert(0, "reports/evidence/fbm-sector31-consola-20261126/evidencia")
import mprdis as M
from capstone import Cs, CS_ARCH_ARM, CS_MODE_THUMB

TAB, N, SZ = 0x7E7FAC, 29, 12
ents = []
for k in range(N):
    e = TAB + k * SZ
    name, fn, desc = M.rd32(e), M.rd32(e + 4), M.rd32(e + 8)
    ents.append((k, M.cstr(name), (fn - 1) if fn & 1 else fn, M.cstr(desc), e))
md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
hdrs = sorted(h for _, _, h, _, _ in ents)
print(f"# {'#':>2} {'nombre':10} {'handler':9} {'len':>5} {'argc>=':>6}  ayuda / traza / destinos")
for k, name, h, desc, e in ents:
    nxt = min([x for x in hdrs if x > h] + [h + 0x400])
    code = M.rd(h, min(nxt - h, 0x300))
    ins = list(md.disasm(code, h))
    argc = ""
    parsers, strs, tgt = [], [], []
    for j, i in enumerate(ins):
        if i.mnemonic == "cmp" and i.op_str.startswith("r0, #") and j < 6:
            try: argc = str(int(i.op_str.split("#")[1], 0) + 1)
            except ValueError: pass
        if i.mnemonic in ("bl", "blx") and i.op_str.startswith("#"):
            t = int(i.op_str[1:], 0) & ~1
            if t == 0x5FFE1A: parsers.append("HEX")
            elif t == 0x5FFE6E: parsers.append("DEC")
            elif t in M.PLT: tgt.append("PLT:" + M.PLT[t])
            else: tgt.append(f"{t:#x}")
        if i.mnemonic == "ldr" and "[pc," in i.op_str:
            try: imm = int(i.op_str.split("#")[-1].rstrip("]"), 0)
            except ValueError: continue
            a = (i.address + 4) & ~3
            v = M.rd32(a + imm)
            if v and M.RO[0] <= v < M.RO[1]:
                s = M.cstr(v, 90)
                if s: strs.append(s)
    print(f"[{k:02d}] {name:10} {h:#08x} {(min(nxt-h,0x300)):#7x} {argc:>6}  parsers={parsers}")
    print(f"       desc={desc!r}")
    for s in strs: print(f"       str: {s!r}")
    print(f"       bl: {tgt}")
