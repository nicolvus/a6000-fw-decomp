#!/usr/bin/env python3
"""G23 — extrae el árbol de menú de Picture Profile de un `CautionConfig.so` (A6300 fw2.01 o A7S fw3.20), solo lectura.

Nodo = símbolo `cmnViewSettingNode…`; propiedades = `cmnViewSettingPropertyList<nombre sin Root>`; hijos = array `cmnViewSettingNodes<nombre sin Root>Default`
(relocaciones R_ARM_ABS32 por entrada, cuenta en `…NodesNumOf…Default`). Resuelve textos con un `string_english.uxc` si se da.
Uso: pp_menu_extract.py CautionConfig.so [string_english.uxc] > arbol.json
"""
import json
import re
import struct
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import uxc_strings

P = "cmnViewSettingNode"


def load(lib: Path):
    d = lib.read_bytes()
    out = subprocess.run(["readelf", "-lW", str(lib)], capture_output=True, text=True, check=True).stdout
    segs = [(int(x[1], 16), int(x[2], 16), int(x[4], 16)) for x in (l.split() for l in out.splitlines()) if x and x[0] == "LOAD"]

    def rd(va, n=1):
        for off, v, sz in segs:
            if v <= va < v + sz:
                return struct.unpack_from(f"<{n}I", d, va - v + off)
        raise KeyError(hex(va))

    sym = {}
    for l in subprocess.run(["nm", "-D", "-S", str(lib)], capture_output=True, text=True, check=True).stdout.splitlines():
        f = l.split()
        if len(f) == 4:
            sym[f[3]] = (int(f[0], 16), int(f[1], 16))
    rel = {}
    for l in subprocess.run(["readelf", "-rW", str(lib)], capture_output=True, text=True, check=True).stdout.splitlines():
        f = l.split()
        if len(f) >= 5 and f[2] == "R_ARM_ABS32":
            rel[int(f[0], 16)] = f[4]
    return rd, sym, rel


def tree(lib: Path, uxc: Path | None = None, prefix: str = "PictureProfile"):
    rd, sym, rel = load(lib)
    recs = uxc_strings.parse(uxc.read_bytes())[2] if uxc else {}

    def props(name):
        k = f"cmnViewSettingPropertyList{name}"
        if k not in sym:
            return None
        va, sz = sym[k]
        t = [rd(va + 12 * i, 3) for i in range(sz // 12)]
        out = {}
        for p, _, v in t:
            out[p] = v
        for p in (0, 6):
            if p in out and (out[p] >> 16) == 0x0204:
                out[f"txt{p}"] = recs.get(out[p] & 0xFFFF)
        return out

    def kids(name):
        k = f"{P}s{name}Default"
        if k not in sym:
            return []
        va, sz = sym[k]
        return [rel[va + 4 * i].removeprefix(P) for i in range(sz // 4) if va + 4 * i in rel]

    def walk(node, seen):
        base = node.removeprefix("Root")
        pr = props(base) or props(node)
        r = {"nodo": node, "props": pr}
        ks = kids(base)
        if ks and node not in seen:
            r["hijos"] = [walk(c, seen | {node}) for c in ks]
        return r

    roots = sorted(n.removeprefix(P) for n in sym if n.startswith(f"{P}Root{prefix}") or n == f"{P}{prefix}")
    return [walk(n, frozenset()) for n in roots]


if __name__ == "__main__":
    lib = Path(sys.argv[1])
    uxc = Path(sys.argv[2]) if len(sys.argv) > 2 else None
    print(json.dumps(tree(lib, uxc), indent=1, ensure_ascii=False, default=str))
