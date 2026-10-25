"""Rutas de emisión estáticas por traza (logger local + logger global 0x43902718) para S605–S627 y S515/S516/S628–S630."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import pic

GLOBAL_LOGGER = 0x43902718
MAX_GAP = 0x300  # separación máxima (bytes) entre la carga local y la global dentro de una misma rutina


def index(refs):
    idx: dict[int, list[dict]] = {}
    for r in refs:
        idx.setdefault(r["target"], []).append(r)
    return idx


def trace_paths(blob, idx, vaddr, text):
    """Para una cadena: referencias al inicio (local) y a desplazamientos interiores (global) con su siguiente llamada."""
    local = []
    for r in idx.get(vaddr, []):
        c = pic.next_call(blob, r["add"] + 2)
        local.append({"ldr": r["ldr"], "add": r["add"], "reg": r["reg"], "call": c})
    inner = []
    for k in range(1, len(text) + 1):
        for r in idx.get(vaddr + k, []):
            c = pic.next_call(blob, r["add"] + 2)
            inner.append({"ldr": r["ldr"], "add": r["add"], "reg": r["reg"], "offset": k, "call": c})
    dual = []
    for lo in local:
        for gl in inner:
            if gl["call"] and gl["call"][1] == GLOBAL_LOGGER and lo["call"] and abs(gl["ldr"] - lo["ldr"]) <= MAX_GAP:
                dual.append((lo, gl))
    return local, inner, dual


def hexify(x):
    if isinstance(x, dict):
        return {k: hexify(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [hexify(v) for v in x]
    return hex(x) if isinstance(x, int) and x > 0xFFF else x


def main():
    blob = pic.load("a6000")
    idx = index(pic.pic_refs(blob))
    root = Path(__file__).resolve().parents[1]
    summary = {}
    for p in sorted(root.glob("s6[0-2][0-9]_*/*.json")):
        sid = p.parent.name[:4].upper()
        if not 605 <= int(sid[1:]) <= 627:
            continue
        d = json.loads(p.read_text())
        if "trace_strings" not in d:
            continue
        res = []
        for t in d["trace_strings"]:
            lo, inn, du = trace_paths(blob, idx, int(t["vaddr"], 16), t["text"])
            res.append({"vaddr": t["vaddr"], "local": len(lo), "inner": len(inn), "dual": len(du)})
        summary[sid] = res
    out = {k: {"traces": len(v), "con_local": sum(1 for r in v if r["local"]), "con_global": sum(1 for r in v if r["inner"]),
               "dual": sum(1 for r in v if r["dual"])} for k, v in summary.items()}
    print(json.dumps(out, indent=0))


if __name__ == "__main__":
    main()
