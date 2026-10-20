#!/usr/bin/env python3
"""Benchmark rediseñado (Fase 12.6): verdad de referencia ESTRUCTURADA por consulta
(knowledge/benchmarks/reference_queries_v2.json), fijada ANTES de ejecutar este script y
sin usar el propio grafo/ask para generarla (ver cada 'note' con su cita manual original).

Compara 4 métodos con presupuestos EQUIVALENTES sobre el mismo corpus:
  rg       -> ripgrep crudo (sin recorte: mide el costo real de "sin motor")
  fts5     -> search.py text/exact (BM25 sobre Markdown indexado)
  graph    -> search.py graph/trace (relaciones CALLS/CORRECTS/SUPERSEDES verificables)
  ask      -> search.py ask (enrutador adaptativo, presupuesto 1000 chars)

A diferencia del benchmark anterior (knowledge/benchmarks/baseline-*.md, conservado SIN
modificar como línea base "antes"), la puntuación no es "¿aparece la subcadena esperada?":
  - exact/conceptual/historical: acierto exige la afirmación Y su fuente (ruta de archivo).
  - relational/multietapa: acierto exige la arista/cadena CALLS exacta (grafo es el único
    método capaz de esto por diseño; rg/fts5 se incluyen para medir dónde SÍ o NO alcanzan).
  - negative: acierto = el método NO afirma el hecho fabricado (no hay "VERIFICADO" ni cita
    de evidencia para algo que no existe).
  - ambiguous: acierto = el método expone >=2 fuentes distintas, no una sola respuesta falsa.
  - partial: acierto = el método se abstiene (resultado vacío o explícitamente "sin ruta
    verificable"), no inventa una relación para una familia de evidencia insuficiente.

Memoria: aproximada vía diferencia de resource.getrusage(RUSAGE_CHILDREN).ru_maxrss entre
llamadas sucesivas (Linux); es un pico ACUMULADO entre hijos, puede subestimar si una
llamada previa ya alcanzó un pico mayor. Tokens: SIEMPRE estimados (caracteres/4, tiktoken
no disponible en este entorno) — nunca se declaran como tokens reales del agente.

Uso: python3 scripts/knowledge/benchmark_v2.py [--out knowledge/benchmarks/report-v2.md]
"""

import argparse
import json
import resource
import subprocess
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path

from _paths import find_root

ROOT = find_root()
SEARCH = ROOT / "scripts" / "knowledge" / "search.py"
PY = sys.executable
REFERENCE_PATH = ROOT / "knowledge" / "benchmarks" / "reference_queries_v2.json"


@dataclass
class Result:
    query_id: str
    category: str
    subsystem: str
    method: str
    latency_s: float
    chars: int
    bytes_: int
    approx_tokens_estimate: int
    rss_delta_kb: int
    hit: bool
    note: str = ""


def run(cmd: list[str]) -> tuple[str, float, int]:
    rss_before = resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss
    start = time.perf_counter()
    proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, check=False)
    elapsed = time.perf_counter() - start
    rss_after = resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss
    return proc.stdout, elapsed, max(0, rss_after - rss_before)


def normalize(out: str) -> str:
    # El resaltado BM25 inserta '[' ']' dentro de los tokens coincidentes.
    return out.lower().replace("[", "").replace("]", "")


def distinct_sources(out: str) -> int:
    """Cuenta rutas de archivo distintas mencionadas (heurística: tokens con '/' y '.md'
    o '.json'), para el criterio de la categoría 'ambiguous'."""
    paths = set()
    for tok in out.replace(":", " ").split():
        if ("/" in tok or tok.endswith((".md", ".json"))) and "." in tok:
            paths.add(tok.strip(",()[]"))
    return len(paths)


def methods_for(item: dict) -> dict[str, list[str]]:
    q = item["query"]
    cat = item["category"]
    methods: dict[str, list[str]] = {
        "rg": ["rg", "--line-number", "--no-heading", "-i", q, "."],
    }
    if cat in ("exact", "negative"):
        methods["fts5"] = [PY, str(SEARCH), "exact", q]
    else:
        methods["fts5"] = [PY, str(SEARCH), "text", q, "--limit", "10"]

    if "graph_start" in item:
        methods["graph"] = [
            PY, str(SEARCH), "trace", item["graph_start"],
            "--max-hops", str(item.get("graph_max_hops", 3)),
        ]
        if item.get("graph_rel_type"):
            methods["graph"] += ["--type", item["graph_rel_type"]]
    elif "graph_doc" in item:
        methods["graph"] = [PY, str(SEARCH), "graph", "--doc", item["graph_doc"], "--direction", "in"]
    # si no hay nodo/documento de grafo aplicable, 'graph' se omite (no se simula con otro
    # método bajo la misma etiqueta: eso falsearía la comparación)

    methods["ask"] = [PY, str(SEARCH), "ask", q, "--budget", "1000"]
    return methods


def score(item: dict, method: str, out: str) -> bool:
    cat = item["category"]
    normalized = normalize(out)
    empty = not out.strip() or "sin resultados" in normalized or "sin relaciones" in normalized

    if cat in ("exact", "conceptual", "historical"):
        claim_ok = item["expect_claim"].lower() in normalized
        path = item.get("expect_source_path")
        path_ok = path is None or path.lower() in normalized
        return claim_ok and path_ok

    if cat == "relational":
        return item["expect_claim"].lower() in normalized

    if cat == "multietapa":
        if item["expect_abstain"]:
            return empty  # debe reconocer que no hay ruta verificable, no inventarla
        return item["expect_claim"].lower() in normalized

    if cat == "negative":
        return empty  # no debe afirmar el hecho fabricado

    if cat == "ambiguous":
        return distinct_sources(out) >= item.get("min_distinct_sources", 2)

    if cat == "partial":
        return empty

    return False


def bench_one(item: dict) -> list[Result]:
    results = []
    for method, cmd in methods_for(item).items():
        out, elapsed, rss_delta = run(cmd)
        results.append(Result(
            query_id=item["id"], category=item["category"], subsystem=item["subsystem"],
            method=method, latency_s=round(elapsed, 4), chars=len(out),
            bytes_=len(out.encode("utf-8")), approx_tokens_estimate=round(len(out) / 4),
            rss_delta_kb=rss_delta, hit=score(item, method, out), note=item["note"],
        ))
    return results


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(ROOT / "knowledge" / "benchmarks" / "report-v2.md"))
    ap.add_argument("--reference", default=str(REFERENCE_PATH))
    args = ap.parse_args()

    items = json.loads(Path(args.reference).read_text(encoding="utf-8"))
    all_results: list[Result] = []
    for item in items:
        all_results.extend(bench_one(item))

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    json_path = out_path.with_suffix(".json")
    json_path.write_text(
        json.dumps([asdict(r) for r in all_results], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    # Precision@k por método = aciertos / consultas aplicables a ese método (k=1 aquí: una
    # sola respuesta evaluada por consulta, no una lista rankeada).
    by_method: dict[str, list[Result]] = {}
    for r in all_results:
        by_method.setdefault(r.method, []).append(r)

    lines = [
        "# Benchmark v2 — verdad de referencia estructurada (Fase 12.6)",
        "",
        ("Línea base PRE-rediseño conservada sin cambios en "
         "knowledge/benchmarks/baseline-2026-10-18-pre-12.6.md. Este reporte usa criterios "
         "de acierto distintos (afirmación+fuente, arista exacta, abstención correcta, "
         "cobertura de ambigüedad) y por tanto NO es comparable número-a-número con la línea "
         "base; compara la CAPACIDAD de cada método, no una métrica idéntica."),
        "",
        "## Precision@1 por método (todas las categorías)",
        "",
        "| Método | Aciertos | Total | Precision@1 | Latencia media (s) | Tokens aprox. medios |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for method, rs in sorted(by_method.items()):
        hits = sum(1 for r in rs if r.hit)
        lines.append(
            f"| {method} | {hits} | {len(rs)} | {hits / len(rs):.2f} | "
            f"{sum(r.latency_s for r in rs) / len(rs):.4f} | "
            f"{sum(r.approx_tokens_estimate for r in rs) / len(rs):.0f} |"
        )

    lines += ["", "## Por categoría", "",
              "| Categoría | Método | Consulta | Acierto | Latencia (s) | Chars | RSS Δ (KB) |",
              "|---|---|---|---|---:|---:|---:|"]
    for r in all_results:
        lines.append(
            f"| {r.category} | {r.method} | {r.query_id} | {'✓' if r.hit else '✗'} | "
            f"{r.latency_s} | {r.chars} | {r.rss_delta_kb} |"
        )

    lines += [
        "", "## Limitaciones conocidas del criterio de puntuación (no ajustadas a propósito)", "",
        ("- **partial**: el acierto exige salida VACÍA. Un método que devuelve texto no "
         "distingue aquí entre 'afirmé una relación falsa' y 'listé archivos reales sin "
         "resolver ninguna relación concreta' (p. ej. rg encontrando literalmente la cadena "
         "'CautionConfig' en archivos que existen). Es un criterio conservador que probablemente "
         "subestima el acierto real de rg/fts5 en esta categoría; no se relajó para no ajustar "
         "el benchmark en busca de resultados favorables."),
        ("- **rg sin presupuesto**: en consultas genéricas ('callback', 'init') ripgrep "
         "recorre TODO el repositorio (incluye analysis/, binarios de evidencia, logs) sin "
         "ningún recorte, generando decenas de millones de caracteres. Esto es intencional "
         "(mide el costo real de 'sin motor'), no un error de medición; infla fuertemente el "
         "promedio de tokens estimados de la fila 'rg' en la tabla de Precision@1 — leer esa "
         "fila junto con la tabla por categoría, no aislada."),
        ("- **memoria (RSS Δ)**: aproximada por diferencia de "
         "resource.getrusage(RUSAGE_CHILDREN).ru_maxrss entre llamadas sucesivas; es un pico "
         "ACUMULADO entre procesos hijo del mismo padre, puede mostrar 0 si una llamada previa "
         "ya alcanzó un pico mayor que la actual. No es una medición aislada por proceso."),
        ("- **tokens**: SIEMPRE una estimación (caracteres/4). No hay tokenizador real ni "
         "reporte de uso de un agente real disponible en este entorno; estos números NO deben "
         "citarse como ahorro de tokens real de Claude Code o Codex."),
        "",
        "## Notas de verdad de referencia", "",
    ]
    seen_notes = set()
    for item in items:
        if item["id"] not in seen_notes:
            lines.append(f"- **{item['id']}** ({item['category']}/{item['subsystem']}): {item['note']}")
            seen_notes.add(item["id"])

    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    total_hits = sum(1 for r in all_results if r.hit)
    print(f"{out_path} y {json_path} escritos. {total_hits}/{len(all_results)} comparaciones método×consulta con acierto.")


if __name__ == "__main__":
    main()
