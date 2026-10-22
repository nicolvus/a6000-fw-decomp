#!/usr/bin/env python3
"""S120 — clasifica cada sitio PIC por el calleo que sigue (message bus vs consola).

Para cada `ldr rX,[pc,#imm]` + `add rX,pc` que materializa una cadena `[IDT_OPD]` o
`[IDT]`, se busca el `bl` siguiente (en la misma función) y se anota el destino.
Sirve para responder "quién escribe/lee" y para separar las dos variantes del módulo.
"""
import collections
import json
import os
import struct

BASE = 0x43541000
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BIN = os.path.join(ROOT, "analysis/rea-independent/input/av-cam.bin")
PIC = "/tmp/opencode/pic_refs_v2.json"
_MD = None


def u16(b, a):
    return struct.unpack_from("<H", b, a - BASE)[0]


def u32(b, a):
    return struct.unpack_from("<I", b, a - BASE)[0]


def resolve_sites(data, targets):
    """Para cada dirección de string objetivo, devuelve (ldr, add, valor_resuelto)."""
    n = len(data)
    res = collections.defaultdict(list)
    a = BASE
    while a < BASE + n - 4:
        h = u16(data, a)
        reg = lit = None
        if (h & 0xF800) == 0x4800:
            reg = (h >> 8) & 7
            lit = ((a + 4) & ~3) + ((h & 0xFF) * 4)
        elif (h & 0xFF7F) == 0xF85F:
            h2 = u16(data, a + 2)
            reg = h2 >> 12
            lit = ((a + 4) & ~3) + ((((h2 >> 8) & 0xF) << 8) | (h2 & 0xFF))
            a += 4
            continue
        if reg is not None and lit is not None and BASE <= lit < BASE + n - 4:
            w = u32(data, lit)
            res[reg].append((a, w))
        a += 2
    return res


def main():
    data = open(BIN, "rb").read()
    refs = json.load(open(PIC))
    # strings de interés
    want = {}
    for key, pref in (("IDT_OPD", b"[IDT_OPD]"), ("IDT", b"[IDT]")):
        idx = 0
        while True:
            i = data.find(pref, idx)
            if i < 0:
                break
            idx = i + 1
            e = data.find(b"\x00", i)
            want[f"0x{BASE + i:x}"] = (key, data[i:e].decode("latin1"))

    # add rX,pc
    adds = collections.defaultdict(list)
    a = BASE
    while a < BASE + len(data) - 2:
        h = u16(data, a)
        if (h & 0xFF00) == 0x4400 and ((h >> 3) & 0xF) == 15:
            rd = ((h >> 7) & 1) << 3 | (h & 7)
            adds[rd].append(a)
        a += 2

    rows = []
    for dest, sites in refs.items():
        if dest not in want:
            continue
        key, text = want[dest]
        for site in sites:
            a = int(site, 16) if isinstance(site, str) else int(site)
            # el escáner v2 reporta la dirección del `add rX,pc`; el `bl` siguiente
            # es la llamada que consume la cadena
            callee = _next_bl(data, a)
            rows.append({"site": f"0x{a:x}", "vaddr": dest, "mod": key,
                         "text": text, "callee": f"0x{callee:x}" if callee else None})
    json.dump(rows, open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                      "sites_by_callee.json"),
                         "w"), indent=1, ensure_ascii=False)
    tab = collections.Counter((r["mod"], r["callee"]) for r in rows)
    for (m, c), n in tab.most_common(30):
        print(f"{m:8s} {c}  {n}")
    print("sitios:", len(rows))


def _next_bl(data, a):
    """Primer `bl` (16 o 32 bits) después de `a`, decodificado con capstone."""
    from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs
    global _MD
    if _MD is None:
        _MD = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
        _MD.detail = True
    off = a - BASE
    for ins in _MD.disasm(data[off:off + 96], a):
        if ins.address == a:
            continue
        if ins.mnemonic in ("bl", "blx"):
            return ins.operands[0].imm if ins.operands[0].type == 2 else None
        if ins.mnemonic in ("b", "bx", "b.w", "pop", "bx lr", "push"):
            # un salto no condicional antes del bl: la heurística deja de ser fiable
            if ins.mnemonic in ("b", "b.w"):
                return None
    return None


if __name__ == "__main__":
    main()
