"""Revisión paralela de los informes .md: estado real de cada afirmación, errores y pendientes sin marcar.

Un proceso por núcleo lee los informes (fase map); el proceso principal cruza los resultados (fase reduce):
  - cerrables:  NO_VERIFICADO cuyas direcciones aparecen como VERIFICADO en otro informe.
  - añadibles:  líneas pendientes ("falta", "por hacer"…) sin marca NO_VERIFICADO.
  - errores:    enlaces relativos rotos, rutas de scripts/tests citadas que no existen,
                VERIFICADO sin evidencia (sin dirección ni bytes) y VERIFICADO+NO_VERIFICADO sobre la misma dirección.
Salida: analysis/review_reports/review.json y RESUMEN.md. No modifica ningún informe.

shortcut: heurística léxica por líneas, no semántica; cada hallazgo es un candidato a revisar a mano.
"""
import json
import os
import re
from collections import Counter, defaultdict
from multiprocessing import Pool
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis/review_reports"
SCAN = ("docs/capture", "analysis", "wiki", "reports")
SKIP = ("analysis/review_reports", "analysis/rea-independent/manifests", "analysis/s178_census/pendientes.md")

OPEN = re.compile(r"NO[ _]VERIFICADO", re.IGNORECASE)
DONE = re.compile(r"(?<!NO )(?<!NO_)\bVERIFICADO(?:_ESTATICO)?\b")
ADDR = re.compile(r"\b0x[0-9a-fA-F]{6,8}\b")
PENDING = re.compile(r"\b(falta[n]?|por hacer|pendiente de|habr[íi]a que|sin verificar|no se ha (?:verificado|comprobado|identificado))\b",
                     re.IGNORECASE)
LINK = re.compile(r"\]\(([\w./-]+\.(?:md|py|json|png|svg|txt|csv))(?:#[^)]*)?\)")
PATH = re.compile(r"`((?:analysis|scripts|tests|docs)/[\w./-]+\.(?:py|md|json))`")
STATUS = ("NO_VERIFICADO", "VERIFICADO", "INFERENCIA", "HIPÓTESIS", "CONFLICTO_PENDIENTE", "NEGATIVO",
          "REFUTADO", "CORREGIDO", "SUPERADO", "BLOQUEADO")
EVIDENCE = re.compile(r"0x[0-9a-fA-F]{4,}|bytes?|instrucci|\bbl\b|ldr|desensambl|xref|SHA-256|test_\w+|\.json", re.IGNORECASE)


def review(rel: str) -> dict:
    """Fase map: analiza un informe."""
    path = ROOT / rel
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    out = {"file": rel, "status": Counter(), "open": [], "done": [], "pending": [], "errors": []}
    text = "\n".join(lines)
    for word in STATUS:
        out["status"][word] = len(re.findall(re.escape(word), text, re.IGNORECASE))
    for n, line in enumerate(lines, 1):
        addrs = sorted({a.lower() for a in ADDR.findall(line)})
        short = re.sub(r"\s+", " ", line.strip())[:200]
        is_open, is_done = bool(OPEN.search(line)), bool(DONE.search(line))
        if is_open:
            out["open"].append({"line": n, "addrs": addrs, "text": short})
        elif is_done:
            out["done"].append({"line": n, "addrs": addrs, "text": short})
            if not EVIDENCE.search(line) and not EVIDENCE.search(" ".join(lines[max(0, n - 7):n + 6])):
                out["errors"].append({"kind": "VERIFICADO sin evidencia", "line": n, "text": short})
        elif PENDING.search(line) and not line.lstrip().startswith("#"):
            out["pending"].append({"line": n, "text": short})
    for n, line in enumerate(lines, 1):
        for target in LINK.findall(line):
            if "://" in target or target.startswith(("mailto:", "/")):
                continue
            if not (path.parent / target).resolve().exists():
                out["errors"].append({"kind": "enlace roto", "line": n, "text": target})
        for target in PATH.findall(line):
            if not (ROOT / target).exists():
                out["errors"].append({"kind": "ruta citada inexistente", "line": n, "text": target})
    out["status"] = dict(out["status"])
    return out


def files() -> list[str]:
    found = []
    for top in SCAN:
        for path in sorted((ROOT / top).rglob("*.md")):
            rel = path.relative_to(ROOT).as_posix()
            if not rel.startswith(SKIP):
                found.append(rel)
    return found


def words(text: str) -> set[str]:
    """Palabras de contenido (sin direcciones ni marcas de estado) para medir solapamiento entre líneas."""
    text = ADDR.sub(" ", OPEN.sub(" ", DONE.sub(" ", text)))
    return {w for w in re.findall(r"[a-záéíóúñ_]{5,}", text.lower())}


def cross(results: list[dict]) -> dict:
    """Fase reduce: cruza direcciones entre informes."""
    verified: dict[str, set[str]] = defaultdict(set)
    for r in results:
        for item in r["done"]:
            for a in item["addrs"]:
                verified[a].add(r["file"])
    closable, conflicts = [], []
    texts: dict[str, list[tuple[str, set[str]]]] = defaultdict(list)
    for r in results:
        for item in r["done"]:
            for a in item["addrs"]:
                texts[a].append((r["file"], words(item["text"])))
    for r in results:
        for item in r["open"]:
            others = {a: sorted(verified[a] - {r["file"]}) for a in item["addrs"] if verified[a] - {r["file"]}}
            if item["addrs"] and len(others) == len(item["addrs"]):
                mine = words(item["text"])
                best = max((len(mine & w) / max(1, len(mine | w)) for a in item["addrs"] for f, w in texts[a] if f != r["file"]),
                           default=0.0)
                closable.append({"file": r["file"], "line": item["line"], "text": item["text"], "overlap": round(best, 2),
                                 "tier": "A" if best >= 0.3 else "B",
                                 "verified_in": {a: f[:3] for a, f in others.items()}})
        same = {a for i in r["open"] for a in i["addrs"]} & {a for i in r["done"] for a in i["addrs"]}
        if same:
            conflicts.append({"file": r["file"], "addrs": sorted(same)[:8]})
    return {"closable": closable, "conflicts": conflicts}


def summary(results: list[dict], crossed: dict, workers: int) -> str:
    total = Counter()
    for r in results:
        total.update(r["status"])
    errors = Counter(e["kind"] for r in results for e in r["errors"])
    top_open = sorted(results, key=lambda r: -len(r["open"]))[:15]
    top_pending = sorted(results, key=lambda r: -len(r["pending"]))[:10]
    lines = ["# Revisión automática de informes", "",
             (f"Generado por `scripts/review_reports.py` con {workers} procesos sobre {len(results)} informes "
             f"(`{', '.join(SCAN)}`). Heurística léxica: cada hallazgo es un candidato, no un veredicto."), "",
             "## Resumen", "",
             f"- Líneas `NO_VERIFICADO`: **{sum(len(r['open']) for r in results)}**; `VERIFICADO`: **{sum(len(r['done']) for r in results)}**.",
             (f"- **Cerrables (reducen pendientes):** {len(crossed['closable'])} líneas abiertas cuyas direcciones constan como VERIFICADO en otro informe; "
             f"**{sum(c['tier'] == 'A' for c in crossed['closable'])} de nivel A** (además comparten palabras de contenido con la línea verificada, solapamiento ≥ 0,3) y el resto de nivel B (misma dirección, otro asunto)."),
             f"- **Añadibles (aumentan pendientes):** {sum(len(r['pending']) for r in results)} líneas con «falta/por hacer/sin verificar» y sin marca `NO_VERIFICADO`.",
             f"- **Conflictos:** {len(crossed['conflicts'])} informes con la misma dirección en VERIFICADO y NO_VERIFICADO.",
             f"- **Errores:** {sum(errors.values())} ({', '.join(f'{k}: {v}' for k, v in errors.most_common())}).", "",
             "## Palabras de estado (menciones totales)", ""]
    lines += [f"- `{k}`: {v}" for k, v in total.most_common()]
    lines += ["", "## Informes con más líneas NO_VERIFICADO", ""]
    lines += [f"- `{r['file']}`: {len(r['open'])} abiertas, {len(r['done'])} verificadas" for r in top_open]
    lines += ["", "## Informes con más pendientes sin marcar (a añadir)", ""]
    lines += [f"- `{r['file']}`: {len(r['pending'])}" for r in top_pending]
    lines += ["", "## Cerrables de nivel A (revisar y retirar la marca)", ""]
    lines += [f"- `{c['file']}:{c['line']}` (solap. {c['overlap']}) → verificado en {', '.join(sorted({f for v in c['verified_in'].values() for f in v})[:2])}"
              for c in crossed["closable"] if c["tier"] == "A"][:40]
    lines += ["", "Detalle completo en `review.json`.", ""]
    return "\n".join(lines)


def main() -> None:
    targets = files()
    workers = os.cpu_count() or 1
    with Pool(workers) as pool:
        results = pool.map(review, targets, chunksize=8)
    crossed = cross(results)
    OUT.mkdir(parents=True, exist_ok=True)
    data = {"workers": workers, "files": len(results), **crossed,
            "pending_unmarked": [{"file": r["file"], **p} for r in results for p in r["pending"]],
            "errors": [{"file": r["file"], **e} for r in results for e in r["errors"]],
            "status_by_file": {r["file"]: r["status"] for r in results if any(r["status"].values())}}
    (OUT / "review.json").write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    (OUT / "RESUMEN.md").write_text(summary(results, crossed, workers), encoding="utf-8")
    print(f"{len(results)} informes, {workers} procesos; cerrables {len(crossed['closable'])}, "
          f"añadibles {len(data['pending_unmarked'])}, errores {len(data['errors'])}, conflictos {len(crossed['conflicts'])}")


if __name__ == "__main__":
    main()
