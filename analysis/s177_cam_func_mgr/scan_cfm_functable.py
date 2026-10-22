#!/usr/bin/env python3
"""S177 — reconstruye la tabla de funciones del gestor (origin/nombre/id).

La tabla vive en .data en 0x43ff17b8 con entradas de 12 B:
    { const char *origin; const char *name; u32 id; }
`origin` y `name` se inicializan en runtime (la función de init en 0x43787d88
escribe `origin`); `name` e `id` están inicializados en el fichero.

Este script:
  1. lee `name` e `id` del fichero,
  2. simula la función de init (0x43787d88..0x43787e90) para obtener `origin`.
"""
import bisect
import json
import os
import re
import struct

from capstone import CS_ARCH_ARM, CS_MODE_LITTLE_ENDIAN, CS_MODE_THUMB, Cs

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BASE = 0x43541000
B = open(os.path.join(ROOT, "analysis/rea-independent/input/av-cam.bin"), "rb").read()
N = len(B)
U16 = struct.Struct("<H").unpack_from
U32 = struct.Struct("<I").unpack_from
MD = Cs(CS_ARCH_ARM, CS_MODE_THUMB | CS_MODE_LITTLE_ENDIAN)

TABLE_BASE = 0x43ff17b8
STRIDE = 12
INIT_LO, INIT_HI = 0x43787d88, 0x43787e90


def cstr(a):
    o = a - BASE
    if o < 0 or o >= N:
        return None
    e = B.find(b"\x00", o)
    if e < 0 or e - o > 120:
        return None
    try:
        s = B[o:e].decode("utf-8")
    except UnicodeDecodeError:
        return None
    return s if all(32 <= ord(c) < 127 for c in s) else None


def pic_targets():
    """{addr_add: (dest, reg)} para los `add rX,pc` de la zona."""
    ldrs = []
    a = INIT_LO
    while a < INIT_HI:
        o = a - BASE
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
            ldrs.append((a, reg, U32(B, lit - BASE)[0], lit))
        a += 2
    by_reg = {}
    for a, reg, w, lit in ldrs:
        by_reg.setdefault(reg, []).append((a, w, lit))
    for v in by_reg.values():
        v.sort()
    keys = {r: [x[0] for x in v] for r, v in by_reg.items()}
    out = {}
    a = INIT_LO
    while a < INIT_HI:
        o = a - BASE
        h = U16(B, o)[0]
        if (h & 0xFF00) == 0x4400 and ((h >> 3) & 0xF) == 15:
            reg = (((h >> 7) & 1) << 3) | (h & 7)
            v = by_reg.get(reg)
            if v:
                ks = keys[reg]
                i = bisect.bisect_left(ks, a) - 1
                if i >= 0:
                    la, w, lit = v[i]
                    if a - la <= 4096:
                        out[a] = ((w + a + 4) & 0xFFFFFFFF, reg)
        a += 2
    return out


def simulate():
    """Devuelve [(addr, base_reg, offset, destino_string)] de los `str` de la init."""
    pic = pic_targets()
    regs = {}          # reg -> (kind, valor)  kind: 'str' puntero a cadena, 'num'
    base_reg = None
    out = []
    for ins in MD.disasm(B[INIT_LO - BASE:INIT_HI - BASE], INIT_LO):
        mn, ops = ins.mnemonic, ins.op_str
        if ins.address in pic:
            dest, reg = pic[ins.address]
            regs[reg] = ("str", dest)
        elif mn == "mov" and ops.startswith("r"):
            m = re.match(r"r(\d+), r(\d+)", ops)
            if m:
                regs[int(m.group(1))] = regs.get(int(m.group(2)), ("num", 0))
        elif mn in ("str", "str.w") and ops.startswith("r"):
            m = re.match(r"r(\d+), \[r(\d+)(?:, #(-?0x[0-9a-f]+|\d+))?\]", ops)
            if m:
                rs, rb, off = int(m.group(1)), int(m.group(2)), m.group(3)
                if rb in regs and regs[rb][0] == "str":
                    addr = regs[rb][1] + (int(off, 0) if off else 0)
                    out.append((ins.address, regs[rb][1], int(off, 0) if off else 0, addr,
                                cstr(regs[rs][1]) if regs.get(rs, ("", 0))[0] == "str" else None))
    return out


def main():
    # 1) nombre e id del fichero
    entries = []
    k = 0
    while True:
        a = TABLE_BASE + STRIDE * k
        if a + STRIDE > N + BASE:
            break
        o_ptr, n_ptr, idv = struct.unpack_from("<III", B, a - BASE)
        name = cstr(n_ptr)
        if name is None:
            break
        entries.append({"k": k, "slot": hex(a), "nombre": name, "id": idv,
                        "id_hex": hex(idv), "origin": None})
        k += 1
    # 2) origin por simulación de la init
    for addr, basereg, off, dest, s in simulate():
        if s is None:
            continue
        # dest = base del store (dirección real) -> registro de la entrada
        kk = (dest - TABLE_BASE) // STRIDE
        if 0 <= kk < len(entries) and (dest - TABLE_BASE) % STRIDE == 0:
            entries[kk]["origin"] = s
            entries[kk]["origin_ptr"] = hex(dest)
    print(f"entradas: {len(entries)}  base={TABLE_BASE:#x}  stride={STRIDE}")
    for e in entries:
        print(f"k={e['k']:2d} {e['slot']}  id={e['id_hex']:<8} origin={e['origin']!r:<18} "
              f"name={e['nombre']!r}")
    json.dump({"base": hex(TABLE_BASE), "stride": STRIDE, "entradas": entries},
              open(os.path.join(ROOT, "analysis/s177_cam_func_mgr/cfm_functable.json"), "w"),
              indent=1)


if __name__ == "__main__":
    main()
