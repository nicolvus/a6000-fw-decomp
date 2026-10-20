"""Atribuye direcciones de código a su función contenedora y, si es método virtual, a su clase.

Inicios de función = entradas de vtable (rtti_vtables.py) ∪ destinos bl/blx directos ∪ símbolos dinámicos.
Uso: python3 -I scripts/func_owner.py desensamblado.txt rtti.json lib.so [--calls SIMBOLO_PLT] [0xADDR ...]
shortcut: un inicio de función solo llamado por puntero y ausente de vtables/exports queda invisible;
la atribución es entonces la función previa — se marca con 'gap' (distancia al inicio) para revisar a mano."""
import bisect
import json
import re
import subprocess
import sys

BL = re.compile(r"^\s*([0-9a-f]+):\s+(?:bl|blx)\s+0x([0-9a-f]+)(?:\s+<([^>]+)>)?")


def load(dis_path: str, rtti_path: str, lib: str):
    rtti = json.load(open(rtti_path))
    starts = {int(e, 16): rtti["methods_by_entry"][e] for e in rtti["methods_by_entry"]}
    names = {}
    nm = subprocess.run(["llvm-nm", "-D", "--defined-only", "-C", lib], capture_output=True, text=True).stdout
    for line in nm.splitlines():
        p = line.split(maxsplit=2)
        if len(p) == 3 and p[1] in "Tt":
            names[int(p[0], 16) & ~1] = p[2]
    calls = []
    for line in open(dis_path):
        m = BL.match(line)
        if m:
            calls.append((int(m[1], 16), int(m[2], 16), m[3] or ""))
    fn_starts = set(starts) | set(names) | {t for _, t, sym in calls if "@plt" not in sym}
    return rtti, starts, names, sorted(fn_starts), calls


def owner(addr: int, ordered: list[int], starts: dict, names: dict) -> dict:
    s = ordered[bisect.bisect_right(ordered, addr) - 1]
    return {"addr": hex(addr), "func": hex(s), "gap": addr - s, "export": names.get(s),
            "virtual_of": starts.get(s, [])}


if __name__ == "__main__":
    dis, rtti_p, lib, *rest = sys.argv[1:]
    rtti, starts, names, ordered, calls = load(dis, rtti_p, lib)
    out = []
    if rest[:1] == ["--calls"]:
        sym, rest = rest[1], rest[2:]
        out += [dict(owner(a, ordered, starts, names), call=s) for a, _, s in calls if sym in s]
    out += [owner(int(a, 16), ordered, starts, names) for a in rest]
    print(json.dumps({"function_starts": len(ordered), "results": out}, indent=1))
