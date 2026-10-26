"""E8: de los 14 sitios que leen el objeto `0x43f72d02`, cuáles cuelgan (por llamadores, hasta 7 niveles) de las raíces de captura
`0x437b5b14` (origen del bloque B), `0x438c7800` y `0x438c828c` (llamadores de SetExposure). Necesita un demonio REA abierto (argv[1] = socket).
Salida: e8_alcance.json. Límite: el grafo de llamadores de REA no cubre rutinas Thumb sembradas a mano (`not_in_procedure`)."""
import json
import sys
from pathlib import Path

import rq

HERE = Path(__file__).parent
ROOTS = {"0x437b5b14", "0x438c7800", "0x438c828c"}
DEPTH = 7
MAX_VISITED = 400


def callers_of(sock: str, procs: list[str]) -> list[list[str]]:
    out = []
    for r in rq.norm(sock, [("procedure_callers", {"procedure": p}) for p in procs]):
        items = r if isinstance(r, list) else []
        out.append([c if isinstance(c, str) else c.get("address") for c in items])
    return out


def reach(sock: str, start: str) -> tuple[list[str], int]:
    seen, frontier = {start}, [start]
    for _ in range(DEPTH):
        if not frontier or len(seen) > MAX_VISITED:
            break
        fresh = {c for cs in callers_of(sock, frontier) for c in cs if c and c not in seen}
        seen |= fresh
        frontier = sorted(fresh)
    return sorted(seen & ROOTS), len(seen)


def main(sock: str) -> None:
    sites = [s["sitio"] for s in json.loads((HERE / "static_findings.json").read_text())["E7"]["sitios"]]
    containing = rq.norm(sock, [("resolve_containing_procedure", {"address": a}) for a in sites])
    result = {}
    for site, info in zip(sites, containing):
        proc = (info.get("procedure") or {}).get("address") if isinstance(info, dict) else None
        roots, visited = reach(sock, proc) if proc else ([], 0)
        result[site] = {"proc": proc, "raices": roots, "visitados": visited}
    (HERE / "e8_alcance.json").write_text(json.dumps(result, indent=1) + "\n")
    for site, v in result.items():
        print(site, v)


if __name__ == "__main__":
    main(sys.argv[1])
