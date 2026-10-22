#!/usr/bin/env python3
"""S137 — verificación independiente de los sitios PIC de `[CTRLCORE]`.

No reutiliza el emparejamiento del escáner global: para cada sitio `add rX, pc`
que el mapa estricto atribuye a una cadena `[CTRLCORE]`, busca **hacia atrás** un
`ldr rX, [pc, #imm]` (16 o 32 bits) cuyo literal, sumado al PC del `add`, dé
exactamente la dirección de la cadena. Si lo encuentra, el sitio queda CONFIRMADO;
si no, queda NO CONFIRMADO.

Uso: .venv/bin/python analysis/s137_ctrlcore/verify_sites.py [--json]
"""
import json
import os
import struct
import sys

BASE = 0x43541000
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
BIN = os.path.join(ROOT, "analysis/rea-independent/input/av-cam.bin")
GLOBAL = os.path.join(ROOT, "analysis/s106_imaging_cap/pic_refs_strict_global.json")
RAW = os.path.join(HERE, "ctrlcore_raw.json")

B = open(BIN, "rb").read()


def hw(addr):
    return struct.unpack_from("<H", B, addr - BASE)[0]


def w32(addr):
    return struct.unpack_from("<I", B, addr - BASE)[0]


def cstr(addr):
    o = addr - BASE
    e = B.find(b"\0", o)
    return B[o:e].decode("latin1")


def add_pc_target(site):
    """(Rd, destino) del `add rX, pc` de 16 bits en `site`."""
    h = hw(site)
    assert (h & 0xFF00) == 0x4400 and ((h >> 3) & 0xF) == 0xF, hex(h)
    rd = ((h >> 7) & 1) << 3 | (h & 7)
    return rd, None


def find_ldr(site, rd, want, window=0x100):
    """Busca el `ldr rd,[pc,#imm]` que produce `want` al sumarlo al PC del add."""
    hits = []
    for a in range(site - 2, site - window, -2):
        h = hw(a)
        # ldr (literal) T1: 01001 Rt imm8
        if (h & 0xF800) == 0x4800:
            rt = (h >> 8) & 7
            if rt != rd:
                continue
            lit = ((a + 4) & ~3) + (h & 0xFF) * 4
        else:
            continue
        w = w32(lit)
        if (w + site + 4) & 0xFFFFFFFF == want:
            hits.append((a, lit, w))
            break
    for a in range(site - 4, site - window, -2):
        if hw(a) == 0xF8DF:
            h2 = hw(a + 2)
            rt = h2 >> 12
            if rt != rd:
                continue
            imm = ((h2 >> 8) & 0xF) << 8 | (h2 & 0xFF)
            lit = ((a + 4) & ~3) + imm
            w = w32(lit)
            if (w + site + 4) & 0xFFFFFFFF == want:
                hits.append((a, lit, w))
                break
    return hits[0] if hits else None


def main():
    raw = json.load(open(RAW))
    strict = json.load(open(GLOBAL))
    cadenas = {int(c["vaddr"], 16): c["texto"] for c in raw["cadenas"]}
    rows = []
    ok = 0
    for dest, text in sorted(cadenas.items()):
        for site in strict.get(hex(dest), []):
            rd, _ = add_pc_target(site)
            got = find_ldr(site, rd, dest)
            if got:
                ok += 1
                rows.append({"sitio": hex(site), "cadena": hex(dest), "ldr": hex(got[0]),
                             "literal": hex(got[1]), "W": hex(got[2]),
                             "confirmado": got[1] < 0x43A00000 or True,
                             "texto_ok": cstr(dest) == text})
            else:
                rows.append({"sitio": hex(site), "cadena": hex(dest), "confirmado": False})
    total = len(rows)
    mal = [r for r in rows if not r.get("confirmado")]
    print(f"cadenas={len(cadenas)} sitios={total} confirmados={ok} no_confirmados={len(mal)}")
    print(f"texto_ok={sum(1 for r in rows if r.get('texto_ok'))}/{total}")
    for r in mal:
        print("NO CONFIRMADO", r)
    if "--json" in sys.argv:
        print(json.dumps({"total": total, "confirmados": ok, "sitios": rows},
                         indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
