"""S72-10: grafo de dependencias entre módulos a partir de las cadenas de traza de av-cam.bin.
Arista A->B si una cadena con prefijo [A] menciona el nombre del módulo B como palabra completa."""
import collections
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
data = (ROOT / "analysis/rea-independent/input/av-cam.bin").read_bytes()
mods = set(json.loads((ROOT / "analysis/s79_modules/module_map.json").read_text())["A6000"])
GENERICOS = {"ERR", "ERROR", "INT_ERROR", "INFO", "DEBUG", "PARAM", "DBGCMD", "STK", "CMP"}  # palabras comunes que además son prefijo de módulo
strs = [m.group().decode("ascii", "replace") for m in re.finditer(rb"[\x20-\x7e]{6,}", data)]
edges = collections.Counter()
for s in strs:
    m = re.match(r"\[([A-Z][A-Z0-9_]+)\]", s)
    if not m or m.group(1) not in mods:
        continue
    a = m.group(1)
    for tok in set(re.findall(r"[A-Z][A-Z0-9_]{2,}", s[m.end():])):
        if tok in mods and tok != a and tok not in GENERICOS:
            edges[(a, tok)] += 1
out = {"nodos": sorted(mods), "aristas": [[a, b, n] for (a, b), n in edges.most_common()]}
(ROOT / "analysis/s101_shutter_type/graph/module_graph.json").write_text(json.dumps(out, indent=1))
print(len(mods), "módulos;", len(edges), "aristas")
for (a, b), n in edges.most_common(25):
    print(f"{a} -> {b} ({n})")
