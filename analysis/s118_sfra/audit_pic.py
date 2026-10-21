#!/usr/bin/env python3
"""S118 — auditoría del esquema PIC **restringida a las trazas `[SFRA]`**.

Para cada sitio `add rX, pc` que (según `scan_pic_refs.py`) apunta a una traza
`[SFRA]`, lista TODOS los `ldr` del mismo registro dentro de 4 KB y marca cuáles
resuelven a un inicio de cadena. Sirve para detectar ambigüedades del esquema
PIC y para separar referencias reales de coincidencias.
"""
import json
import os
import struct

BASE = 0x43541000
BIN = "analysis/rea-independent/input/av-cam.bin"
HERE = os.path.dirname(os.path.abspath(__file__))
MAX_LDR_GAP = 4096
CODE_LO, CODE_HI = 0x43900000, 0x439C0000


def main():
    data = open(BIN, "rb").read()
    n = len(data)
    refs = json.load(open(os.path.join(HERE, "pic_refs.json")))
    sfra = set(int(k, 16) for k in refs)
    # sólo las 100 trazas [SFRA]
    texts = {}
    i = data.find(b"[SFRA")
    while i >= 0:
        e = i
        while e < len(data) and 32 <= data[e] < 127:
            e += 1
        texts[BASE + i] = data[i:e].decode("latin1")
        i = data.find(b"[SFRA", i + 1)
    sfra &= set(texts)

    starts = set()
    prev = False
    for i in range(n):
        cur = 32 <= data[i] < 127
        if cur and not prev:
            starts.add(BASE + i)
        prev = cur

    ldrs = {}
    adds = []
    a = CODE_LO
    while a < CODE_HI:
        o = a - BASE
        h = struct.unpack_from("<H", data, o)[0]
        lit = reg = None
        if (h & 0xF800) == 0x4800:
            reg = (h >> 8) & 7
            lit = ((a + 4) & ~3) + (h & 0xFF) * 4
        elif (h & 0xFF7F) == 0xF85F:
            h2 = struct.unpack_from("<H", data, o + 2)[0]
            reg = (h2 >> 12) & 0xF
            imm12 = (((h2 >> 8) & 0xF) << 8) | (h2 & 0xFF)
            lit = ((a + 4) & ~3) + imm12
        if reg is not None and 0 <= lit - BASE < n - 4:
            ldrs.setdefault(reg, []).append((a, struct.unpack_from("<I", data, lit - BASE)[0]))
        if (h & 0xFF00) == 0x4400 and ((h >> 3) & 0xF) == 15:
            adds.append((a, (((h >> 7) & 1) << 3) | (h & 7)))
        a += 2
    for v in ldrs.values():
        v.sort()

    rows = []
    for a, reg in adds:
        v = ldrs.get(reg)
        if not v:
            continue
        cand = []
        # se recorren los `ldr` del registro **hacia atrás** desde el más cercano
        for la, w in reversed(v):
            if la > a:
                continue
            if a - la > MAX_LDR_GAP:
                break
            tgt = (w + (a + 4)) & 0xFFFFFFFF
            cand.append({"ldr": f"0x{la:x}", "dist": a - la, "tgt": f"0x{tgt:x}",
                         "is_string": tgt in starts})
        hits = [c for c in cand if c["is_string"]]
        if not hits:
            continue
        sfra_hits = [c for c in hits if int(c["tgt"], 16) in sfra]
        if not sfra_hits:
            continue
        rows.append({"site": f"0x{a:x}", "reg": reg, "n_cand": len(cand),
                     "n_hits": len(hits),
                     "nearest_dist": cand[0]["dist"],
                     "nearest_is_hit": cand[0]["is_string"],
                     "sfra_hits": sfra_hits,
                     "other_hits": [c for c in hits if c not in sfra_hits]})

    json.dump(rows, open(os.path.join(HERE, "pic_audit.json"), "w"), indent=1)
    print("sitios que (según el escáner) apuntan a una traza [SFRA]:", len(rows))
    amb = [r for r in rows if len(r["sfra_hits"]) > 1]
    print("  con >1 traza [SFRA] candidata (AMBIGUOS):", len(amb))
    print("  con otra cadena no-[SFRA] también candidata:", sum(1 for r in rows if r["other_hits"]))
    print("  donde el `ldr` más cercano NO resuelve a cadena:",
          sum(1 for r in rows if not r["nearest_is_hit"]))
    print("  distancia del `ldr` más cercano: min %d max %d" % (
        min(r["nearest_dist"] for r in rows), max(r["nearest_dist"] for r in rows)))
    for r in amb:
        print("   AMB", r["site"], [(h["ldr"], h["dist"], h["tgt"]) for h in r["sfra_hits"]])
    # el sitio canónico: el `ldr` más cercano que resuelve a una traza [SFRA]
    canon = {}
    for r in rows:
        h = sorted(r["sfra_hits"], key=lambda x: x["dist"])[0]
        canon.setdefault(int(h["tgt"], 16), []).append(r["site"])
    print("cadenas [SFRA] con >=1 sitio canónico:", len(canon), "de", len(sfra))
    faltan = sorted(sfra - set(canon))
    print("sin sitio canónico:", [hex(x) for x in faltan])


if __name__ == "__main__":
    main()
