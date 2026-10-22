#!/usr/bin/env python3
"""S122 — diferencial de las 127 trazas `[CAMERA_MAIN_TC]` frente a A7S fw3.20 y A6300 fw2.01.

Hecho verificado: ni la A7S fw3.20 ni la A6300 fw2.01 contienen el token
`[CAMERA_MAIN_TC]` (0 apariciones). Lo que se compara es el **texto interior** de cada
traza de la A6000 (lo que queda tras `[CAMERA_MAIN_TC]: `), que sí existe en las otras
dos versiones como literal suelto.

Para cada versión:
  * localiza el texto interior en el binario (subcadena, todas las apariciones),
  * aplica la **regla PIC estricta** canónica (mismo `ldr rX,[pc,#imm]` más cercano por
    detrás, ventana 4 KB; solo destinos que sean inicio de cadena imprimible),
  * cuenta los sitios de referencia a ese literal.

Salida: diff_versions.json
Uso: scan_diff_versions.py
"""
import bisect
import json
import os
import struct

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
BASE = 0x43541000
A6000 = os.path.join(ROOT, "analysis/rea-independent/input/av-cam.bin")
A7S = os.path.join(
    ROOT,
    "firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/"
    "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin",
)
A6300 = os.path.join(
    ROOT,
    "firmware/extracted/a6300-fw201/payload/firmware.tar_unpacked/"
    "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin",
)
MAX_GAP = 4096
U16 = struct.Struct("<H").unpack_from
U32 = struct.Struct("<I").unpack_from


def strict_refs(data):
    """{vaddr_destino: [vaddr_add]} con la regla PIC estricta (canónica)."""
    n = len(data)
    # inicios de cadena imprimible en toda la imagen
    starts = set()
    prev = False
    for i in range(n):
        cur = 32 <= data[i] < 127
        if cur and not prev:
            starts.add(BASE + i)
        prev = cur
    ldrs, adds = [], []
    a = BASE
    while a < BASE + n - 8:
        o = a - BASE
        h = U16(data, o)[0]
        if (h & 0xF800) == 0x4800:
            reg = (h >> 8) & 7
            lit = ((a + 4) & ~3) + (h & 0xFF) * 4
            o2 = lit - BASE
            if 0 <= o2 <= n - 4:
                ldrs.append((a, reg, U32(data, o2)[0]))
        elif (h & 0xFF7F) == 0xF85F:
            h2 = U16(data, o + 2)[0]
            reg = (h2 >> 12) & 0xF
            lit = ((a + 4) & ~3) + ((((h2 >> 8) & 0xF) << 8) | (h2 & 0xFF))
            o2 = lit - BASE
            if 0 <= o2 <= n - 4:
                ldrs.append((a, reg, U32(data, o2)[0]))
        if (h & 0xFF00) == 0x4400 and ((h >> 3) & 0xF) == 15:
            adds.append((a, ((h >> 7) & 1) << 3 | (h & 7)))
        a += 2
    by_reg = {}
    for a, reg, w in ldrs:
        by_reg.setdefault(reg, []).append((a, w))
    keys = {r: [x[0] for x in v] for r, v in by_reg.items()}
    out = {}
    for a, reg in adds:
        v = by_reg.get(reg)
        if not v:
            continue
        i = bisect.bisect_left(keys[reg], a) - 1
        if i < 0:
            continue
        la, w = v[i]
        if a - la > MAX_GAP:
            continue
        tgt = (w + a + 4) & 0xFFFFFFFF
        if tgt in starts:
            out.setdefault(tgt, []).append(a)
    return out


def main():
    strings = json.load(open(os.path.join(HERE, "strings_raw.json")))["strings"]
    res = {}
    for name, path in (("a7s_fw320", A7S), ("a6300_fw201", A6300)):
        data = open(path, "rb").read()
        refs = strict_refs(data)
        rows, n_found, n_ref, n_sites, exact = [], 0, 0, 0, 0
        for s in strings:
            inner = s["text"].split("]: ", 1)[-1]
            if not inner.strip():
                rows.append({"vaddr": s["vaddr"], "inner": inner,
                             "found": False, "why": "texto interior vacío"})
                continue
            hits = []
            i = data.find(inner.encode())
            while i >= 0:
                hits.append(BASE + i)
                i = data.find(inner.encode(), i + 1)
            if not hits:
                rows.append({"vaddr": s["vaddr"], "inner": inner,
                             "found": False, "why": "no aparece"})
                continue
            n_found += 1
            # literal exacto = el texto interior empieza en un inicio de cadena
            va = [h for h in hits if h in refs] or hits
            v = va[0]
            sit = refs.get(v, [])
            if v in refs and (v - BASE == 0 or not (32 <= data[v - BASE - 1] < 127)):
                exact += 1
            if sit:
                n_ref += 1
                n_sites += len(sit)
            rows.append({"vaddr": s["vaddr"], "inner": inner,
                         "found": True, "vaddr_other": f"0x{v:x}",
                         "n_hits": len(hits), "sites": [f"0x{x:x}" for x in sit]})
        res[name] = {
            "bin": os.path.relpath(path, ROOT),
            "token_camera_main_tc": data.count(b"[CAMERA_MAIN_TC]"),
            "texts_found": n_found,
            "texts_ref_pic": n_ref,
            "pic_sites": n_sites,
            "texts_exact_literal": exact,
            "rows": rows,
        }
        print(name, {k: v for k, v in res[name].items() if k != "rows"})
    json.dump(res, open(os.path.join(HERE, "diff_versions.json"), "w"),
              indent=1, ensure_ascii=False)


if __name__ == "__main__":
    main()
