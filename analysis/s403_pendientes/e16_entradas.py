"""E16: entradas del grupo de rutinas que leen `[0x43eefb1c+0x60]` (CURTAINMODE): raíces del grafo de llamadores (REA, `procedure_callers`)
y referencias por puntero (palabras `dir|1` en la imagen). Argv[1] = socket REA. Salida: e16_entradas.json.
Límite: REA no cubre rutinas Thumb sembradas a mano; una raíz sin llamadores ni punteros puede ser alcanzada por una rutina no ubicada."""
import json
import struct
import sys
from pathlib import Path

import pic
import rq

HERE = Path(__file__).parent
LO, HI = 0x43841BF8, 0x43842440
DEPTH, MAX_NODES = 14, 800


def cluster(sock: str) -> list[int]:
    found = rq.norm(sock, [("search_procedures", {"pattern": "FUN_43841"}), ("search_procedures", {"pattern": "FUN_43842"})])
    return sorted({int(x["address"], 16) for lst in found for x in lst if LO <= int(x["address"], 16) <= HI})


def callers(sock: str, procs: list[int]) -> dict[int, list[int]]:
    res = rq.norm(sock, [("procedure_callers", {"procedure": hex(p)}) for p in procs])
    return {p: sorted({int(c if isinstance(c, str) else c["address"], 16) for c in (r if isinstance(r, list) else [])}) for p, r in zip(procs, res)}


def main(sock: str) -> None:
    blob = pic.load("a6000")
    words: dict[int, list[int]] = {}
    for o in range(0, len(blob) - 3, 4):
        w = struct.unpack_from("<I", blob, o)[0]
        if w & 1 and pic.BASE <= w < pic.BASE + len(blob):
            words.setdefault(w & ~1, []).append(pic.BASE + o)
    group = cluster(sock)
    seen, frontier, edges = set(group), list(group), {}
    for _ in range(DEPTH):
        if not frontier or len(seen) > MAX_NODES:
            break
        got = callers(sock, frontier)
        edges.update(got)
        frontier = sorted({c for cs in got.values() for c in cs} - seen)
        seen |= set(frontier)
    roots = sorted(p for p in seen if not edges.get(p))
    out = {"grupo": [hex(p) for p in group], "nodos": len(seen), "truncado": len(seen) > MAX_NODES,
           "raices": {hex(p): {"punteros": [hex(w) for w in words.get(p, [])]} for p in roots}}
    (HERE / "e16_entradas.json").write_text(json.dumps(out, indent=1) + "\n")
    print(len(group), "en el grupo;", len(seen), "nodos;", len(roots), "raíces;", sum(bool(words.get(p)) for p in roots), "con puntero")


if __name__ == "__main__":
    main(sys.argv[1])
