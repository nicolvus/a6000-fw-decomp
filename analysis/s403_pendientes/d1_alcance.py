"""D1: cuáles de las 226 etiquetas pendientes del censo se emiten desde código alcanzable (llamadas directas) desde las raíces de captura.
Grafo propio sobre bytes de A6000: inicios de función = destinos de BL/B.W y prólogos `push {..,lr}`; aristas = BL/B.W a un inicio.
Calibración: de los 14 sitios del objeto de estado (E8) debe reproducir los 7 que REA sitúa bajo las raíces. Salida: d1_alcance.json.
shortcut: sin llamadas indirectas (BLX reg, vtables, colas OSAL) ni funciones sin prólogo `push lr`; el alcance es un mínimo, no una cota superior."""
import bisect
import json
import struct
import sys
from collections import deque
from pathlib import Path

import pic

HERE = Path(__file__).parent
ROOTS = (0x437B5B14, 0x438C7800, 0x438C828C)
STRICT = len(sys.argv) > 1 and sys.argv[1] == "estricto"  # solo destinos con prólogo `push lr`
CENSUS = HERE.parents[0] / "s178_census/pendientes_auditados.json"


def scan(blob: bytes) -> tuple[list[int], list[tuple[int, int]], set[int]]:
    """(inicios de función ordenados, aristas (sitio, destino) de BL/B.W)."""
    starts, edges, pushes = set(), [], set()
    o = 0
    while o < len(blob) - 3:
        h1, h2 = struct.unpack_from("<HH", blob, o)
        step = 4 if h1 & 0xF800 in (0xE800, 0xF000, 0xF800) else 2  # barrido por instrucción: sin falsos BL en la 2.ª mitad
        if h1 & 0xFE00 == 0xB400 and h1 & 0x0100 or h1 == 0xE92D and h2 & 0x4000:  # push {…, lr}
            starts.add(pic.BASE + o)
            pushes.add(pic.BASE + o)
        if h1 & 0xF800 == 0xF000 and h2 & 0xD000 in (0xD000, 0x9000):
            r = pic.next_call(blob, pic.BASE + o, 1)
            if r:
                edges.append(r)
                if h2 & 0xD000 == 0xD000:
                    starts.add(r[1])
        o += step
    return sorted(starts), edges, pushes


def path(parent: dict[int, int], node: int) -> list[int]:
    out = [node]
    while out[-1] in parent:
        out.append(parent[out[-1]])
    return out[::-1]


def main() -> None:
    blob = pic.load("a6000")
    starts, edges, pushes = scan(blob)
    owner = lambda a: starts[bisect.bisect_right(starts, a) - 1]
    known = pushes if STRICT else set(starts)
    out_edges: dict[int, set[int]] = {}
    for site, target in edges:
        if target in known:
            out_edges.setdefault(owner(site), set()).add(target)
    depth = {r: 0 for r in ROOTS}
    parent: dict[int, int] = {}
    queue = deque(ROOTS)
    while queue:
        f = queue.popleft()
        for t in out_edges.get(f, ()):
            if t not in depth:
                depth[t] = depth[f] + 1
                parent[t] = f
                queue.append(t)
    sites = [int(s["sitio"], 16) for s in json.loads((HERE / "static_findings.json").read_text())["E7"]["sitios"]]
    calibration = {hex(s): (hex(owner(s)), depth.get(owner(s))) for s in sites}
    census = json.loads(CENSUS.read_text())
    rows = []
    for e in census["etiquetas"]:
        if e["estado_censo"] != "pendiente":
            continue
        refs = sorted({int(r, 16) for o in e["ocurrencias"] for r in o["referencias_pic_candidatas"]})
        hosts = sorted({owner(r) for r in refs})
        reached = [h for h in hosts if h in depth]
        rows.append({"etiqueta": e["etiqueta"], "veredicto": e["veredicto"], "sitios": len(refs), "funciones": len(hosts),
                     "alcanzadas": [{"funcion": hex(h), "profundidad": depth[h], "camino": [hex(x) for x in path(parent, h)]}
                                    for h in reached]})
    res = {"funciones_detectadas": len(starts), "aristas": len(edges), "alcanzables_desde_raices": len(depth),
           "calibracion_e8": calibration, "etiquetas": rows}
    (HERE / ("d1_alcance_estricto.json" if STRICT else "d1_alcance.json")).write_text(json.dumps(res, indent=1) + "\n")
    hit = [r for r in rows if r["alcanzadas"]]
    print(len(starts), len(edges), len(depth), "etiquetas con emisor alcanzable:", len(hit), "de", len(rows))
    print({k: v for k, v in calibration.items()})
    for r in hit:
        print(r["etiqueta"], r["veredicto"], r["sitios"], r["funciones"], [(a["funcion"], a["profundidad"]) for a in r["alcanzadas"]][:4])


if __name__ == "__main__":
    main()
