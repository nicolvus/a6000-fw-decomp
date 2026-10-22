#!/usr/bin/env python3
"""S139 — recupera el **número de línea del fuente** de cada traza `[ENCSEQCTRL]`.

Convención de llamada del logger (verificada desensamblando 0x43a4e534):
    log(logger /*r0*/, module_id /*r1*/, level /*r2*/, format /*r3*/, varargs en pila)
El `Line:%d` de la macro es una **constante de compilación** (`movw r3,#imm` +
`str r3,[sp,#k]`), de modo que se puede recuperar la línea del `.cpp` de cada traza.

El script es **estricto**: sólo acepta una llamada si los argumentos de pila que
la macro exige están donde deben y valen lo que deben:
  * "File:%s, Func:%s() ,Line:%d"  → ranura 0 = fichero, 4 = método, 8 = línea
  * "Func:%s() ,Line:%d, ..."        → ranura 0 = método, 4 = línea

Uso: .venv/bin/python analysis/s139_encseqctrl/line_numbers.py [LO] [HI]
"""
import json
import os
import re
import struct
import sys

from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs

BASE = 0x43541000
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
B = open(os.path.join(ROOT, "analysis/rea-independent/input/av-cam.bin"), "rb").read()
md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
md.detail = True

LOGGERS = {0x43a4e534, 0x43a4e4e8}
FILE_STR = 0x43c4BD0F          # "seqCtrl/mcAvcEncSeqCtrl.cpp"


def hw(a):
    return struct.unpack_from("<H", B, a - BASE)[0]


def w32(a):
    return struct.unpack_from("<I", B, a - BASE)[0]


def cstr(va):
    o = va - BASE
    e = B.find(b"\0", o)
    return B[o:e].decode("latin1")


def resolve_add(site, window=0x200):
    """Resuelve un `add rX, pc` de 16 bits → (reg, destino)."""
    h = hw(site)
    if (h & 0xFF00) != 0x4400 or ((h >> 3) & 0xF) != 0xF:
        return None
    rd = ((h >> 7) & 1) << 3 | (h & 7)
    for a in range(site - 2, site - window, -2):
        h1 = hw(a)
        if (h1 & 0xF800) == 0x4800 and ((h1 >> 8) & 7) == rd:
            lit = ((a + 4) & ~3) + (h1 & 0xFF) * 4
            return rd, (w32(lit) + site + 4) & 0xFFFFFFFF
    for a in range(site - 4, site - window, -2):
        if hw(a) == 0xF8DF:
            h2 = hw(a + 2)
            if (h2 >> 12) != rd:
                continue
            imm = ((h2 >> 8) & 0xF) << 8 | (h2 & 0xFF)
            lit = ((a + 4) & ~3) + imm
            return rd, (w32(lit) + site + 4) & 0xFFFFFFFF
    return None


def is_pretty(va):
    try:
        t = cstr(va)
    except Exception:
        return False
    return "::" in t and t[:1].isupper()


def main():
    lo = int(sys.argv[1], 0) if len(sys.argv) > 1 else 0x435d6ad0
    hi = int(sys.argv[2], 0) if len(sys.argv) > 2 else 0x435d9300
    P = []
    a = lo
    while a < hi:
        h = hw(a)
        if (h & 0xFF00) == 0xB500 and (h & 0x0100):
            P.append(a)
            a += 2
            continue
        if h == 0xE92D:
            h2 = hw(a + 2)
            if h2 & 0x4000:
                P.append(a)
        a += 2
    P.append(hi)

    rows = []
    for k in range(len(P) - 1):
        f0, f1 = P[k], P[k + 1]
        insns = list(md.disasm(B[f0 - BASE:f1 - BASE], f0))
        for n, i in enumerate(insns):
            if i.mnemonic != "bl" or not i.op_str.startswith("#0x"):
                continue
            if int(i.op_str[1:], 16) not in LOGGERS:
                continue
            fmt = None
            regval = {}          # reg → (tipo, valor)
            slots = {}           # offset de pila → (tipo, valor)
            for ins in insns[max(0, n - 30):n]:
                m = ins.mnemonic
                if m == "add" and ins.op_str.endswith(", pc"):
                    r = resolve_add(ins.address)
                    if r:
                        regval["r%d" % r[0]] = ("ptr", r[1])
                elif m in ("movw", "mov", "movs") and "#" in ins.op_str:
                    p = ins.op_str.split(",")
                    try:
                        regval[p[0].strip()] = ("imm", int(p[1].split("#")[1], 0))
                    except (IndexError, ValueError):
                        pass
                elif m == "str" and "[sp" in ins.op_str:
                    reg = ins.op_str.split(",")[0].strip()
                    mo = re.search(r"#(0x[0-9a-fA-F]+|\d+)\]", ins.op_str)
                    off = int(mo.group(1), 0) if mo else 0
                    if reg in regval:
                        slots[off] = regval[reg]
            if "r3" not in regval:
                continue
            fmt = regval["r3"][1]
            if regval["r3"][0] != "ptr":
                continue
            try:
                txt = cstr(fmt)
            except Exception:
                continue
            if not txt.startswith("[ENCSEQCTRL]"):
                continue
            line = None
            # posición de "Line:%d" en el formato → número de especificadores previos
            mi = txt.find("Line:%d")
            if mi >= 0:
                nspec = len(re.findall(r"%[-#0-9.lh]*[a-zA-Z]", txt[:mi]))
                lv = slots.get(4 * nspec)
                # validación: los args anteriores deben ser el fichero y/o el método
                prev = [slots.get(4 * k) for k in range(nspec)]
                okprev = all(v is not None for v in prev) and all(
                    v[0] == "ptr" and (v[1] == FILE_STR or is_pretty(v[1])) for v in prev)
                if lv and lv[0] == "imm" and okprev:
                    line = lv[1]
            rows.append({"fn": hex(f0), "log_call": hex(i.address), "fmt": hex(fmt),
                         "line": line, "texto": txt})
    print(json.dumps(rows, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
