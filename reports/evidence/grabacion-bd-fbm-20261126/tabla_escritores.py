#!/usr/bin/env python3
"""Los 11 llamantes de BackupMgr::EntryWriteBaseDataFunction (0x2B1DEC):
reconstruye (userID r0, fn r1, arg r2, mediaID r3) justo antes del `bl`.
Resuelve `ldr rX,[pc,#imm]` contra el pool de literales del .text.
"""
import re
import sys

sys.path.insert(0, "reports/evidence/fbm-sector31-consola-20261126/evidencia")
import mprdis as M
from capstone import Cs, CS_ARCH_ARM, CS_MODE_THUMB

TEXT = M.sec(".text")
md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
CALLEES = {0x2B1DEC: "EntryWriteBaseDataFunction"}

LLAMANTES = [0x2b51d8, 0x2b55b0, 0x2b55c4, 0x2b55e6, 0x2b55fc,
             0x38096e, 0x380990, 0x3ac5ae, 0x3b0466, 0x520230, 0x5c9b06]


def decode_regs(call):
    r = {0: "?", 1: "?", 2: "?", 3: "?"}
    for a in range(call - 0x40, call, 2):
        ins = next(md.disasm(M.rd(a, 4), a), None)
        if not ins:
            continue
        m, op = ins.mnemonic, ins.op_str
        if m in ("mov", "movs", "mov.w") and re.match(r"^r[0-3], ", op):
            d, s = [x.strip() for x in op.split(",", 1)]
            if s.startswith("#"):
                r[int(d[1])] = s
            elif s in ("r4", "r5", "r6", "r7", "r8", "sb", "sl", "fp", "r0", "r1", "r2", "r3"):
                r[int(d[1])] = s
        elif m in ("ldr", "ldr.w", "ldrb", "ldrh") and re.match(r"^r[0-3], \[r[0-9a-z]+, #", op):
            d = int(op[1])
            r[d] = "mem(" + op.split(", ", 1)[1].lstrip("[").rstrip("]") + ")"
        elif m in ("ldr", "ldr.w") and re.match(r"^r[0-3], \[pc", op):
            d = int(op[1])
            try:
                imm = int(op.split("#")[-1].rstrip("]"), 0)
            except ValueError:
                continue
            pool = ((ins.address + 4) & ~3) + imm
            v = M.rd32(pool)
            if v is not None:
                note = ""
                if v > 0x1000 and (v & ~1) < 0x9D8400:
                    f = v & ~1
                    note = f" -> fn {f:#x} (Thumb)" if f & 1 == 0 else f" -> {f:#x}"
                    nm = M.SYM.get(f)
                    if nm:
                        note += f" {nm}"
                r[d] = f"{v:#x}{note}"
    return r


print("# llamantes de BackupMgr::EntryWriteBaseDataFunction 0x2B1DEC")
print("# r0=userID  r1=fn  r2=arg  r3=mediaID\n")
for c in LLAMANTES:
    ins = next(md.disasm(M.rd(c, 4), c), None)
    tgt = int(ins.op_str[1:], 0) & ~1
    r = decode_regs(c)
    print(f"{c:#x}: bl {CALLEES.get(tgt, hex(tgt))}")
    for k in (0, 1, 2, 3):
        print(f"    r{k} = {r[k]}")
    print()
