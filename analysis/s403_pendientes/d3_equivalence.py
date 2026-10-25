#!/usr/bin/env python3
"""D3 (equivalencia funcional/de código): para las trazas S605–S627 cuyo texto núcleo existe también en A7S/A6300, compara la
rutina A6000 que referencia la cadena con la(s) rutina(s) homóloga(s) del otro modelo (flujo alcanzable normalizado, igual motor
que el cierre S402: llamadas locales emparejadas por posición, solo cambian números de línea → equivalente).

Funciones identificadas con REA (una sesión por modelo, cerrada al terminar). Límite: llamadas indirectas y limpieza de
excepciones no se comparan; igualdad del flujo no es equivalencia física ni de datos en ejecución."""
import json
import sys
from pathlib import Path

import dual_scan
import pic
import rq

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "analysis/s402_static_closure"))
import fw
import rawfw

SOCK = {"a6000": ROOT / "analysis/rea-independent/run/pend-a6.sock", "a7s": ROOT / "analysis/rea-independent/run/pend-a7.sock"}
OUT = Path(__file__).with_name("d3_equivalence.json")
rawfw.IMAGES["A6300"] = pic.FIRMWARE["a6300"]


def find_all(blob: bytes, core: str) -> list[int]:
    pat, out, i = core.encode() + b"\0", [], 0
    while (i := blob.find(pat, i)) >= 0:
        out.append(pic.BASE + i)
        i += 1
    return out


def refs(idx, start, span):
    return sorted({r["add"] for k in range(span + 1) for r in idx.get(start + k, [])})


def functions(model: str, sites: list[int]) -> dict[int, int | None]:
    res = rq.norm(str(SOCK[model]), [("resolve_containing_procedure", {"address": hex(s)}) for s in sites]) if sites else []
    return {s: (int(x["procedure"]["address"], 16) if isinstance(x, dict) and x.get("found") else None) for s, x in zip(sites, res)}


def compare(a: rawfw.RawLib, b: rawfw.RawLib, pa: int, pb: int) -> dict:
    pairs = fw.closure(a, b, pa, pb, max_depth=3)
    root = pairs[(pa, pb)]
    return {"len": root["len"], "root_igual_salvo_lineas": not root["residue"], "pares": len(pairs),
            "con_diferencias": sum(bool(v["residue"]) for v in pairs.values())}


def main() -> None:
    A, C, D = (pic.load(m) for m in ("a6000", "a7s", "a6300"))
    idx = {"a6000": dual_scan.index(pic.pic_refs(A)), "a7s": dual_scan.index(pic.pic_refs(C)), "a6300": dual_scan.index(pic.pic_refs(D))}
    libs = {"a7s": rawfw.RawLib("A7S"), "a6000": rawfw.RawLib("A6000")}
    results = []
    for p in sorted((ROOT / "analysis").glob("s6[0-2][0-9]_*/*.json")):
        sid = p.parent.name[:4].upper()
        if not 605 <= int(sid[1:]) <= 627:
            continue
        d = json.loads(p.read_text())
        for t in d.get("trace_strings", []):
            core = (t.get("core_text") or t["text"].removeprefix(d.get("prefix", ""))).strip()
            hom = {m: find_all(blob, core) for m, blob in (("a7s", C), ("a6300", D)) if len(core) >= 6}
            if not any(hom.values()):
                continue
            ra = refs(idx["a6000"], int(t["vaddr"], 16), len(t["text"]))
            fa = {f for f in functions("a6000", ra).values() if f}
            row = {"ficha": sid, "nucleo": core[:60], "a6000_funciones": sorted(map(hex, fa)), "modelos": {}}
            r7 = sorted({x for h in hom["a7s"] for x in refs(idx["a7s"], h, len(core) + 40)})
            f7 = {f for f in functions("a7s", r7).values() if f}
            best = None
            for pa in fa:
                for pb in f7:
                    c = compare(libs["a6000"], libs["a7s"], pa, pb)
                    c.update({"a6000": hex(pa), "a7s": hex(pb)})
                    if best is None or (c["root_igual_salvo_lineas"], -c["con_diferencias"]) > (best["root_igual_salvo_lineas"], -best["con_diferencias"]):
                        best = c
            row["modelos"]["a7s"] = {"homologos": len(hom["a7s"]), "funciones": sorted(map(hex, f7)), "mejor": best}
            row["modelos"]["a6300"] = {"homologos": len(hom["a6300"])}
            results.append(row)
    OUT.write_text(json.dumps(results, indent=1) + "\n")
    for r in results:
        b = r["modelos"]["a7s"]["mejor"]
        print(r["ficha"], r["nucleo"][:32], r["a6000_funciones"][:2], "->", None if b is None else (b["root_igual_salvo_lineas"], b["con_diferencias"], b["pares"]))


if __name__ == "__main__":
    main()
