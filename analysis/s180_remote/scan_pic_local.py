#!/usr/bin/env python3
"""S180 - escaneo PIC local (regla estricta) en la region ACCY + verificacion a mano.

1) Reproduce el mapa global `pic_refs_strict_global.json` en la region de codigo ACCY
   (misma regla: `add rX,pc` emparejado con el `ldr rX,[pc,#imm]` MAS CERCANO por
   detras del mismo registro, ventana 4 KB).
2) Verifica a mano (capstone, detail=True) cada par (sitio, cadena) de las 32 cadenas
   [REMOTE]: (a) ldr mas cercano, (b) literal del pool, (c) destino, (d) el registro no
   se reescribe entre ldr y add.
"""
import json, struct, sys
from capstone import *
from capstone.arm import *

BASE = 0x43541000
BIN = "analysis/rea-independent/input/av-cam.bin"
GLOBAL = "analysis/s106_imaging_cap/pic_refs_strict_global.json"
REG_LO, REG_HI = 0x43562000, 0x43567400     # region de codigo ACCY
MAX_LDR_GAP = 4096

B = open(BIN, "rb").read()
N = len(B)
U16 = struct.Struct("<H").unpack_from
U32 = struct.Struct("<I").unpack_from


def string_starts(lo, hi):
    out = set()
    prev = False
    for i in range(max(0, lo - BASE), min(N, hi - BASE)):
        cur = 32 <= B[i] < 127
        if cur and not prev:
            out.add(BASE + i)
        prev = cur
    return out


def ldr_sites(lo, hi):
    out = []
    a = lo
    while a < hi:
        o = a - BASE
        if o < 0 or o > N - 8:
            a += 2
            continue
        h = U16(B, o)[0]
        reg = lit = None
        if (h & 0xF800) == 0x4800:
            reg = (h >> 8) & 7
            lit = ((a + 4) & ~3) + ((h & 0xFF) * 4)
        elif (h & 0xFF7F) == 0xF85F:
            h2 = U16(B, o + 2)[0]
            reg = (h2 >> 12) & 0xF
            lit = ((a + 4) & ~3) + ((((h2 >> 8) & 0xF) << 8) | (h2 & 0xFF))
        if reg is not None:
            o2 = lit - BASE
            if 0 <= o2 <= N - 4:
                out.append((a, reg, U32(B, o2)[0]))
        a += 2
    return out


def add_sites(lo, hi):
    out = []
    a = lo
    while a < hi:
        o = a - BASE
        if o < 0 or o > N - 4:
            a += 2
            continue
        h = U16(B, o)[0]
        if (h & 0xFF00) == 0x4400 and ((h >> 3) & 0xF) == 15:
            out.append((a, (((h >> 7) & 1) << 3) | (h & 7)))
        a += 2
    return out


def scan(lo, hi, starts):
    ldrs = ldr_sites(lo, hi)
    adds = add_sites(lo, hi)
    by_reg = {}
    for a, reg, w in ldrs:
        by_reg.setdefault(reg, []).append((a, w))
    for v in by_reg.values():
        v.sort()
    out = {}
    for a, reg in adds:
        v = by_reg.get(reg)
        if not v:
            continue
        la, w = v[bisect_right(v, (a, 0xFFFFFFFF)) - 1]
        if a - la > MAX_LDR_GAP:
            continue
        tgt = (w + (a + 4)) & 0xFFFFFFFF
        if tgt in starts:
            out.setdefault(tgt, []).append(a)
    return out


def bisect_right(v, x):
    lo, hi = 0, len(v)
    while lo < hi:
        mid = (lo + hi) // 2
        if v[mid] <= x:
            lo = mid + 1
        else:
            hi = mid
    return lo


def cstr(a):
    o = a - BASE
    e = o
    while e < len(B) and 32 <= B[e] < 127:
        e += 1
    return B[o:e].decode("latin1")


# ---------------------------------------------------------------- mapa local
starts = string_starts(0, 0xFFFFFFFF)
local = scan(REG_LO, REG_HI, starts)
glob = {int(k, 16): v for k, v in json.load(open(GLOBAL)).items()}
loc2 = {k: sorted(set(v)) for k, v in local.items()}
# subconjunto del mapa global con sitios dentro de la region
glob_sub = {k: [s for s in v if REG_LO <= s < REG_HI] for k, v in glob.items()}
glob_sub = {k: v for k, v in glob_sub.items() if v}
diff = 0
for k in set(loc2) | set(glob_sub):
    a, b = loc2.get(k, []), glob_sub.get(k, [])
    if a != b:
        diff += 1
        print(f"DISCREPANCIA 0x{k:x}: local={a} global={b}")
print(f"mapa local (region ACCY): {len(loc2)} destinos; discrepancias vs mapa global: {diff}")

# ---------------------------------------------------------------- verificacion a mano
md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
md.detail = True
WRITES = {"mov", "movs", "mov.w", "movt", "movw", "mvn", "ldr", "ldr.w", "str", "str.w",
          "strb", "strh", "add", "adds", "add.w", "sub", "subs", "sub.w", "orr", "orrs",
          "and", "ands", "eor", "bic", "mul", "muls", "rsb", "lsl", "lsr", "asr", "uxtb",
          "uxth", "sxtb", "sxth", "pop", "pop.w", "ldm", "ldmia", "ldmia.w", "ldmdb", "ldm.w",
          "stm", "stmdb", "stm.w", "ldrex", "rev", "rrx"}


def dis(lo, hi):
    return list(md.disasm(B[lo - BASE:lo - BASE + (hi - lo)], lo))


def window(addsite):
    for off in range(160, 0, -2):
        ins = dis(addsite - off, addsite + 4)
        for i in ins:
            if i.address == addsite and i.mnemonic == "add" and len(i.operands) == 2 \
               and i.operands[1].type == ARM_OP_REG and i.operands[1].reg == ARM_REG_PC:
                return ins
    return []


def verify(addsite, expected):
    ins = window(addsite)
    add = None
    for i in ins:
        if i.address == addsite and i.mnemonic == "add" and len(i.operands) == 2 \
           and i.operands[1].type == ARM_OP_REG and i.operands[1].reg == ARM_REG_PC:
            add = i
    if add is None:
        return False, "no add rX,pc decodificable", None, None
    rd = add.operands[0].reg
    ldrs = []
    for i in ins:
        if i.address >= addsite:
            break
        if i.mnemonic.startswith("ldr") and len(i.operands) == 2 \
           and i.operands[1].type == ARM_OP_MEM and i.operands[1].mem.base == ARM_REG_PC \
           and i.operands[0].reg == rd:
            ldrs.append(i)
    if not ldrs:
        return False, "sin ldr del mismo registro", None, None
    ldr = ldrs[-1]
    lit = ((ldr.address + 4) & ~3) + ldr.operands[1].mem.disp
    W = U32(B, lit - BASE)[0]
    tgt = (W + (addsite + 4)) & 0xFFFFFFFF
    kill = None
    for i in ins:
        if i.address <= ldr.address or i.address >= addsite:
            continue
        if i.mnemonic in WRITES and i.operands and i.operands[0].type == ARM_OP_REG \
           and i.operands[0].reg == rd:
            kill = i
            break
    info = f"ldr=0x{ldr.address:08x} pool=0x{lit:08x} W=0x{W:08x} tgt=0x{tgt:08x} rd={rd}"
    return (tgt == expected), info, kill, ldr


def main():
    strings = json.load(open("analysis/s180_remote/pic_sites.json"))["strings"]
    res = []
    fails = kills = 0
    for r in strings:
        for site in r["pic_sites"]:
            ok, info, kill, ldr = verify(site, r["vaddr"])
            if not ok:
                fails += 1
            if kill is not None:
                kills += 1
            res.append({"site": hex(site), "target": hex(r["vaddr"]), "ok": ok,
                        "info": info, "kill": (hex(kill.address) if kill else None),
                        "ldr": (hex(ldr.address) if ldr else None), "texto": r["text"]})
            if not ok or kill is not None:
                print(f"  {'OK ' if ok else 'FAIL'} {hex(site)} -> {hex(r['vaddr'])}  {info}"
                      f"  kill={kill.address if kill else None}")
    json.dump(res, open("analysis/s180_remote/pic_verified.json", "w"), indent=1)
    print(f"pares verificados: {len(res)}  fallos: {fails}  reuso de registro: {kills}")
    json.dump({f"0x{k:x}": v for k, v in sorted(loc2.items())},
              open("analysis/s180_remote/pic_local.json", "w"), indent=0)


if __name__ == "__main__":
    main()
