#!/usr/bin/env python3
"""S180 - generar las tablas markdown del informe (para no transcribir a mano)."""
import json

HERE = "analysis/s180_remote"
d = json.load(open(f"{HERE}/remote.json"))

print("| # | addr | nivel | linea | texto | n | sitio(s) | funcion(es) |")
print("|---|---|---|---|---|---|---|---|")
for i, s in enumerate(d["strings"], 1):
    txt = s["text"]
    txt = txt.replace("|", "\\|")
    print(f"| {i} | `{hex(s['vaddr'])}` | {s['nivel']} | {s['linea_fuente']} | `{txt}` | "
          f"{s['n_pic_sites']} | {', '.join('`'+x+'`' for x in s['pic_sites'])} | "
          f"{', '.join('`'+x+'`' for x in s['funciones'])} |")

print()
print("### funcion -> traza")
for f, items in sorted(d["funciones"].items()):
    print(f"\n* **`{f}`**")
    for it in items:
        print(f"  * `{it['site']}` -> `{it['dest']}` (linea {it['linea_fuente']}): `{it['text']}`")
