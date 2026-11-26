#!/usr/bin/env python3
"""Tabla perfil -> error de video (codigo y sitio) -> ¿IFO cargado? + mapa de codigos.

Entrada: reports/evidence/logs-arnes-todos/<perfil>.log.txt e index.tsv
Salida:  perfil-error-ifo.md, mapa-codigos.md (en reports/evidence/logs-arnes-todos/)
"""
import csv
import re
from collections import defaultdict
from pathlib import Path

LOGS = Path(__file__).resolve().parents[3] / "reports/evidence/logs-arnes-todos"

IFO = re.compile(r"(mp4Ifo|xavcIfo) faild at (?P<src>\S+)\((?P<l>\d+)\) ErrCd: (?P<cod>0x[0-9A-F]{8})")
MMGR = re.compile(
    r"## ERROR\((?P<mod>[A-Z_]+)\):(?P<cod>0x[0-9A-F]{8}) ## (?P<src>[\w/]+\.cpp)\((?P<l>\d+)\) (?P<fn>\w+)"
)
CAPAS = re.compile(r"LoadSub : (?P<v>MP4|XAVC|AVCHD[^.]{0,10})")


def leer(p):
    return [
        bytes(c for c in raw if 32 <= c < 127).decode("ascii", "replace").strip()
        for raw in (LOGS / f"{p}.log.txt").read_bytes().split(b"\n")
    ]


sitio_cod = defaultdict(lambda: defaultdict(int))  # codigo -> sitio -> n
datos = {}
for f in csv.DictReader(open(LOGS / "index.tsv"), delimiter="\t"):
    p = f["perfil"]
    if p == "uilive":
        datos[p] = ([], [], [])
        continue
    ifos, mmgrs, capas = [], [], []
    for s in leer(p):
        if m := IFO.search(s):
            clave = f"{m['cod']}→{m['src'].split('/')[-1]}:{m['l']}"
            if clave not in ifos:
                ifos.append(clave)
            sitio_cod[m["cod"]][f"{m['src'].split('/')[-1]}:{m['l']}"] += 1
        if m := MMGR.search(s):
            if "IfoAcsr.cpp" in m["src"] or "IfoComposer.cpp" in m["src"]:
                if m["cod"] not in mmgrs:
                    mmgrs.append(f"{m['cod']}@{m['src'].split('/')[-1]}:{m['l']}")
                sitio_cod[m["cod"]][f"{m['src'].split('/')[-1]}:{m['l']}"] += 1
        if m := CAPAS.search(s):
            if m["v"] not in capas:
                capas.append(m["v"].split()[0])
    if f["codigos_ifo"] != "—":
        pass
    datos[p] = (ifos, mmgrs, capas)

av = {f["perfil"]: f["aviseq"] for f in csv.DictReader(open(LOGS / "index.tsv"), delimiter="\t")}
out = [
    "| perfil | IFO | capas | error IFO (código→sitio) | MMGR IFO | AviSeqPlay | IFO cargado |",
    "|---|---|---|---|---|---|---|",
]
for p in sorted(datos):
    ifos, mmgrs, capas = datos[p]
    if p == "uilive":
        out.append("| `uilive` | — | — | sin `estado.zst` | — | — | **no** |")
        continue
    out.append(
        f"| `{p}` | {'sí' if ifos else 'no'} | {'/'.join(capas) or '—'} | "
        f"{'<br>'.join(ifos) if ifos else '— (no llega)'} | {', '.join(mmgrs) or '—'} | "
        f"{av[p].replace(' ', '<br>') or '—'} | **no** |"
    )
(LOGS / "perfil-error-ifo.md").write_text("\n".join(out) + "\n", encoding="utf-8")

mapa = ["| código | sitios donde se imprime | perfiles |", "|---|---|---|"]
orden = sorted(sitio_cod.items(), key=lambda kv: -sum(kv[1].values()))
for cod, sitios in orden:
    mapa.append(
        f"| `{cod}` | {', '.join(f'`{s}`' for s in sitios)} | {sum(sitios.values())} |"
    )
(LOGS / "mapa-codigos.md").write_text("\n".join(mapa) + "\n", encoding="utf-8")
print("\n".join(mapa))
print(f"\nfilas tabla: {len(out) - 2}")
