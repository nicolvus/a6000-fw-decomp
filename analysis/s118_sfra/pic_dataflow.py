#!/usr/bin/env python3
"""S118 — resolución de referencias a cadenas `[SFRA]` con **flujo de datos**.

La regla "canónica" del repo (probar todos los `ldr` del registro dentro de 4 KB
y aceptar los destinos que caigan en el inicio de una cadena) produce falsos
positivos cuando el registro se reutiliza: p. ej. en `0x4398f06a` el `add r3, pc`
resuelve a una **tabla de contadores**, no a la traza
`[SFRA][CMD] ***SET_PATH(CLOSE)***` (`0x43ce5a50`), porque `r3` fue recargado en
`0x4398efb0`.

Este script mantiene la regla canónica (todos los `ldr` del registro en 4 KB) pero
añade un **kill analysis**: un candidato `ldr` deja de ser válido si entre el
`ldr` y el `add` hay alguna instrucción que **escriba** ese registro (la última
escritura gana).
"""
import json
import os
import struct
import sys

from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from extract_sfra import BASE, BIN, CODE_HI, CODE_LO, function_ranges  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
MAX_LDR_GAP = 4096


def string_starts(data):
    out = set()
    prev = False
    for i in range(len(data)):
        cur = 32 <= data[i] < 127
        if cur and not prev:
            out.add(BASE + i)
        prev = cur
    return out


def ldr_literal(data, addr):
    """(registro, valor W) si la instrucción en `addr` es un `ldr rX,[pc,#imm]`."""
    off = addr - BASE
    h = struct.unpack_from("<H", data, off)[0]
    if (h & 0xF800) == 0x4800:
        reg = (h >> 8) & 7
        lit = ((addr + 4) & ~3) + (h & 0xFF) * 4
    elif (h & 0xFF7F) == 0xF85F:
        h2 = struct.unpack_from("<H", data, off + 2)[0]
        reg = (h2 >> 12) & 0xF
        imm12 = (((h2 >> 8) & 0xF) << 8) | (h2 & 0xFF)
        lit = ((addr + 4) & ~3) + imm12
    else:
        return None
    if not (0 <= lit - BASE < len(data) - 4):
        return None
    return reg, struct.unpack_from("<I", data, lit - BASE)[0]


def add_pc_reg(data, addr):
    off = addr - BASE
    h = struct.unpack_from("<H", data, off)[0]
    if (h & 0xFF00) != 0x4400 or ((h >> 3) & 0xF) != 15:
        return None
    return (((h >> 7) & 1) << 3) | (h & 7)


def writes_reg(md, data, lo, hi, reg):
    """True si alguna instrucción en [lo, hi) escribe `reg` (número ARM 0..15).

    Se decodifica instrucción a instrucción (saltando 2 B si algo no decodifica)
    para no perder escrituras por un desalineamiento en un pool literal.
    """
    a = lo
    while a < hi:
        try:
            ins = next(md.disasm(data[a - BASE:a - BASE + 4], a, count=1))
        except StopIteration:
            a += 2
            continue
        if ins is None:
            a += 2
            continue
        try:
            _, wr = ins.regs_access()
        except Exception:
            wr = []
        for r in wr:
            if md.reg_name(r) == f"r{reg}":
                return True
        a += ins.size
    return False


def main():
    data = open(BIN, "rb").read()
    starts = string_starts(data)
    md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
    md.detail = True

    # ldr literales y adds por registro
    ldrs = {}
    adds = []
    a = CODE_LO
    while a < CODE_HI:
        lit = ldr_literal(data, a)
        if lit is not None:
            ldrs.setdefault(lit[0], []).append((a, lit[1]))
        r = add_pc_reg(data, a)
        if r is not None:
            adds.append((a, r))
        a += 2
    for v in ldrs.values():
        v.sort()

    refs = {}
    site_best = {}
    stats = {"sitios": 0, "candidatos": 0, "aceptados": 0, "muertos": 0, "multi": 0}
    for a, reg in adds:
        v = ldrs.get(reg)
        if not v:
            continue
        cands = []
        for la, w in reversed(v):
            if la > a:
                continue
            if a - la > MAX_LDR_GAP:
                break
            cands.append((la, w))
        if not cands:
            continue
        hits = []
        for la, w in cands:
            tgt = (w + (a + 4)) & 0xFFFFFFFF
            if tgt not in starts:
                continue
            stats["candidatos"] += 1
            killed = writes_reg(md, data, la + 2, a, reg)
            if killed:
                stats["muertos"] += 1
                continue
            stats["aceptados"] += 1
            hits.append((la, tgt))
        if hits:
            stats["sitios"] += 1
            if len(hits) > 1:
                stats["multi"] += 1
            hits.sort(key=lambda x: a - x[0])
            site_best[a] = [f"0x{t:x}" for _, t in hits]
            for la, tgt in hits:
                refs.setdefault(tgt, []).append(a)

    json.dump({f"0x{k:x}": sorted(set(v)) for k, v in sorted(refs.items())},
              open(os.path.join(HERE, "pic_refs_dataflow.json"), "w"), indent=0)
    json.dump({f"0x{k:x}": v for k, v in sorted(site_best.items())},
              open(os.path.join(HERE, "site_best.json"), "w"), indent=0)
    print("stats:", stats)

    texts = {}
    i = data.find(b"[SFRA")
    while i >= 0:
        e = i
        while e < len(data) and 32 <= data[e] < 127:
            e += 1
        texts[BASE + i] = data[i:e].decode("latin1")
        i = data.find(b"[SFRA", i + 1)

    canon = json.load(open(os.path.join(HERE, "pic_refs.json")))
    tot_df = tot_cn = 0
    sin_df = []
    extra_canon = []
    for va, t in sorted(texts.items()):
        k = f"0x{va:x}"
        d = refs.get(va, [])
        c = canon.get(k, [])
        tot_df += len(d)
        tot_cn += len(c)
        if not d:
            sin_df.append((k, t, c))
        for site in c:
            if site not in d:
                extra_canon.append((k, t, site))
    print("sitios con flujo de datos:", tot_df, "  sitios regla canónica:", tot_cn)
    print("cadenas [SFRA] sin referencia:", len(sin_df))
    for x in sin_df:
        print("   ", x)
    print("sitios sólo de la regla canónica (falsos positivos):", len(extra_canon))
    for x in extra_canon:
        print("   ", x)


if __name__ == "__main__":
    main()
