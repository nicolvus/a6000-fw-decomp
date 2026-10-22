#!/usr/bin/env python3
"""S167 — verificación a mano de los pares PIC (regla estricta) de las 49 trazas [SAD].

Para cada sitio (instrucción `add rX,pc`) comprueba:
  (a) el `ldr rX,[pc,#imm]` MÁS CERCANO por detrás es el que aporta el valor;
  (b) el literal del pool es el esperado;
  (c) destino = literal + (dirección_del_add + 4) == inicio de la cadena [SAD];
  (d) el registro NO se reescribe entre el `ldr` y el `add` (si se reescribe, el
      `add` usaría otro valor y la regla estricta fallaría en ese punto).
"""
import bisect, json, struct
BASE = 0x43541000
B = open("analysis/rea-independent/input/av-cam.bin", "rb").read()
N = len(B)
U16 = struct.Struct("<H").unpack_from
U32 = struct.Struct("<I").unpack_from
GM = {int(k, 16): sorted(set(v)) for k, v in
      json.load(open("analysis/s106_imaging_cap/pic_refs_strict_global.json")).items()}

def cstr(a):
    o = a - BASE
    e = B.find(b"\x00", o)
    return B[o:e].decode("latin1")

def ldr_sites(lo, hi):
    out = []
    a = lo
    while a < hi:
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
            out.append((a, reg, U32(B, lit - BASE)[0], lit))
        a += 2
    return out

def add_sites(lo, hi):
    out = []
    a = lo
    while a < hi:
        o = a - BASE
        h = U16(B, o)[0]
        if (h & 0xFF00) == 0x4400 and ((h >> 3) & 0xF) == 15:
            out.append((a, (((h >> 7) & 1) << 3) | (h & 7)))
        a += 2
    return out

def writes_to_reg(lo, hi, reg):
    """Escrituras al registro `reg` en [lo,hi) -> (addr, etiqueta)."""
    out = []
    a = lo
    while a < hi:
        o = a - BASE
        h = U16(B, o)[0]
        note = None
        if (h & 0xF800) == 0x4800 and ((h >> 8) & 7) == reg:
            note = "ldr-lit"
        elif (h & 0xFF7F) == 0xF85F and ((U16(B, o + 2)[0] >> 12) & 0xF) == reg:
            note = "ldr.w-lit"
        elif (h & 0xF800) == 0x6800 and ((h >> 8) & 7) == reg:
            note = "ldr-mem"
        elif (h & 0xF800) == 0x9800 and ((h >> 8) & 7) == reg:
            note = "ldr-mem.w"
        elif 0x2000 <= (h & 0xF800) <= 0x3800 and ((h >> 8) & 7) == reg:
            note = "movs-imm"
        elif (h & 0xFC00) == 0x4000 and ((h & 7) | ((h >> 4) & 8)) == reg:
            note = "alu-reg"
        elif (h & 0xFF00) == 0x4400 and ((h >> 3) & 0xF) == 15 and \
                ((((h >> 7) & 1) << 3) | (h & 7)) == reg:
            note = "add-pc"
        elif (h & 0xFE00) == 0x6000 and ((h >> 8) & 7) == reg:
            note = "str-imm"
        elif (h & 0xFE00) == 0x7000 and ((h >> 8) & 7) == reg:
            note = "strb-imm"
        elif (h & 0xFE00) == 0x8000 and ((h >> 8) & 7) == reg:
            note = "strh-imm"
        elif (h & 0xF800) == 0x5000 and ((h >> 8) & 7) == reg:
            note = "ldr-reg"
        elif (h & 0xFE00) == 0x5200 and ((h >> 8) & 7) == reg:
            note = "str-reg"
        if note:
            out.append((a, note))
        a += 2
    return out

def main():
    sad = {a for a in GM if cstr(a).startswith("[SAD]")}
    sites = []
    for dest in sorted(sad):
        for s in GM[dest]:
            sites.append((s, dest))
    sites.sort()
    lo, hi = 0x43990000, 0x439a2000
    ldrs = ldr_sites(lo, hi)
    adds = dict(add_sites(lo, hi))
    by_reg = {}
    for a, reg, w, lit in ldrs:
        by_reg.setdefault(reg, []).append((a, w, lit))
    for v in by_reg.values():
        v.sort()
    keys = {r: [x[0] for x in v] for r, v in by_reg.items()}
    ok = bad = 0
    rows = []
    for s, dest in sites:
        reg = adds[s]
        v = by_reg[reg]
        ks = keys[reg]
        i = bisect.bisect_left(ks, s) - 1
        la, w, lit = v[i]
        calc = (w + (s + 4)) & 0xFFFFFFFF
        between = writes_to_reg(la + 2, s, reg)
        good = (calc == dest) and not between and (s - la <= 4096)
        ok += good
        bad += (not good)
        rows.append({"sitio": f"0x{s:x}", "reg": f"r{reg}", "ldr": f"0x{la:x}",
                     "pool": f"0x{lit:x}", "literal": f"0x{w:x}",
                     "destino_calculado": f"0x{calc:x}", "destino_cadena": f"0x{dest:x}",
                     "reescrituras": [[f"0x{x:x}", n] for x, n in between],
                     "verificado": bool(good)})
    print(f"pares PIC verificados: {ok}/{len(sites)}  fallidos: {bad}")
    for r in rows:
        if not r["verificado"]:
            print("  FALLO", r)
    json.dump(rows, open("analysis/s167_sad/sad_pic_verificado.json", "w"), indent=1)
    return rows

if __name__ == "__main__":
    main()
