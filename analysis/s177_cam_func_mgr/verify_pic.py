#!/usr/bin/env python3
"""S177 — verificación a mano de los pares PIC (regla estricta) de los sitios [CAM_FUNC_MGR].

Para cada `add rX,pc` (sitio) muestra:
  - el `ldr rX,[pc,#imm]` más cercano por detrás (regla estricta) y su pool,
  - el valor del pool (W),
  - el destino calculado = W + (add + 4),
  - el texto en el destino,
  - AVISO si entre el ldr y el add hay OTRA escritura a rX (reuso de registro).

La detección de escrituras usa Capstone en modo Thumb con `detail=True`
(registro destino real, no el mapeo `& 0xF` erroneo — ver S120).
"""
import bisect
import json
import os
import struct
import sys

from capstone import (CS_ARCH_ARM, CS_MODE_LITTLE_ENDIAN, CS_MODE_THUMB, Cs)
from capstone.arm import ARM_REG_PC, ARM_REG_SP, ARM_REG_LR

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BASE = 0x43541000
B = open(os.path.join(ROOT, "analysis/rea-independent/input/av-cam.bin"), "rb").read()
N = len(B)
U16 = struct.Struct("<H").unpack_from
U32 = struct.Struct("<I").unpack_from
MD = Cs(CS_ARCH_ARM, CS_MODE_THUMB | CS_MODE_LITTLE_ENDIAN)
MD.detail = True


def cstr(a):
    o = a - BASE
    if o < 0 or o >= N:
        return None
    e = B.find(b"\x00", o)
    if e < 0:
        return None
    try:
        return B[o:e].decode("utf-8")
    except UnicodeDecodeError:
        return None


def pic_ldr_sites(lo, hi):
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
        if reg is not None and 0 <= lit - BASE <= N - 4:
            out.append((a, reg, U32(B, lit - BASE)[0], lit))
        a += 2
    return out


def pic_add_sites(lo, hi):
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


def writes_to_reg(lo, hi, reg):
    """Instrucciones que escriben el registro `reg` en [lo,hi) (Thumb, capstone detail)."""
    out = []
    if hi <= lo:
        return out
    code = B[lo - BASE:hi - BASE]
    for ins in MD.disasm(code, lo):
        try:
            regs_written = ins.regs_access()[1]
        except Exception:
            regs_written = []
        # registros ARM: r0..r12 -> ids contiguos; se comparan por nombre
        names = []
        for r in regs_written:
            names.append(ins.reg_name(r))
        target = f"r{reg}"
        if target in names:
            out.append((ins.address, f"{ins.mnemonic} {ins.op_str}"))
    return out


def main():
    lo = int(sys.argv[1], 0) if len(sys.argv) > 1 else 0x43780000
    hi = int(sys.argv[2], 0) if len(sys.argv) > 2 else 0x43810000
    ldrs = pic_ldr_sites(lo, hi)
    adds = pic_add_sites(lo, hi)
    by_reg = {}
    for a, reg, w, lit in ldrs:
        by_reg.setdefault(reg, []).append((a, w, lit))
    for v in by_reg.values():
        v.sort()
    keys = {r: [x[0] for x in v] for r, v in by_reg.items()}
    out = []
    ok = 0
    for a, reg in adds:
        v = by_reg.get(reg)
        if not v:
            continue
        ks = keys[reg]
        i = bisect.bisect_left(ks, a) - 1
        if i < 0:
            continue
        la, w, lit = v[i]
        if a - la > 4096:
            continue
        dest = (w + (a + 4)) & 0xFFFFFFFF
        txt = cstr(dest)
        if txt is None or "[CAM_FUNC_MGR]" not in txt:
            continue
        between = writes_to_reg(la + 2, a, reg)
        flag = "RE-USA-REG" if between else "ok"
        if not between:
            ok += 1
        out.append({"sitio": hex(a), "reg": reg, "ldr": hex(la), "pool": hex(lit),
                    "W": hex(w), "dest": hex(dest), "texto": txt, "flag": flag,
                    "entre_medio": [(hex(x), n) for x, n in between]})
        print(f"{a:#x} reg=r{reg} ldr={la:#x} pool={lit:#x} W={w:#x} -> dest={dest:#x}  "
              f"{txt!r}  [{flag}]  entre={between}")
    print(f"\npares [CAM_FUNC_MGR] verificados: {len(out)}   sin reuso de registro: {ok}")
    json.dump(out, open(os.path.join(ROOT, "analysis/s177_cam_func_mgr/cfm_pic_verificado.json"),
                        "w"), indent=1)


if __name__ == "__main__":
    main()
