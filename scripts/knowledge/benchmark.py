#!/usr/bin/env python3
"""Benchmark reproducible: ripgrep crudo vs FTS5/BM25 vs grafo vs enrutador adaptativo (ask),
sobre consultas reales de la investigación Sony A6000 con verdad de referencia INDEPENDIENTE
del propio sistema (una subcadena ya confirmada en el documento fuente antes de este script,
no "lo que ask devolvió").

Mide latencia real (incluye arranque del intérprete, como en uso real por CLI/MCP) y conteo
de resultados/caracteres. Los "tokens" son SIEMPRE una estimación (caracteres/4), marcada como
tal — no hay tokenizador real disponible en este entorno.

Uso: python3 scripts/knowledge/benchmark.py [--out knowledge/benchmarks/report.md]
"""

import argparse
import json
import subprocess
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path

from _paths import find_root

ROOT = find_root()
SEARCH = ROOT / "scripts" / "knowledge" / "search.py"
PY = sys.executable

# Cada entrada: verdad de referencia verificada manualmente en esta sesión ANTES de
# escribir este benchmark (ver knowledge/PROGRESS.md fases 3-5 para la cita original).
REFERENCE_QUERIES = [
    {"id": "setimagewrited-addr", "kind": "identifier", "query": "0x932a44",
     "expect": "SetImageWrited",
     "note": "docs/capture/pool-write-completion.md:27 (verificado manualmente)"},
    {"id": "setimagewrited-code", "kind": "identifier", "query": "0x1007",
     "expect": "SetImageWrited",
     "note": "README.md:91 (corrección vs 0x1009, verificada manualmente)"},
    {"id": "gpio-curtain", "kind": "concept", "query": "GPIO cortinillas curtain",
     "expect": "1ST_CURTAIN_MG",
     "note": "docs/capture/fm3-gpio-shutter-mapping.md (verificado manualmente)"},
    {"id": "efcs-selector", "kind": "concept", "query": "EFCS selector captura IMX210",
     "expect": "efcs-capture-selector",
     "note": "docs/capture/efcs-capture-selector.md (coincidencia de ruta esperada)"},
    {"id": "darwin-rom-base", "kind": "concept", "query": "Darwin base ROM corrección crítica",
     "expect": "4200",
     "note": "CONTEXT.md / docs/history (corrección Darwin base 0x4200, verificada manualmente)"},
    {"id": "a6300-comparison", "kind": "concept", "query": "A6300 comparación estática silent",
     "expect": "a6300-silent-comparison",
     "note": "docs/capture/a6300-silent-comparison.md (coincidencia de ruta esperada)"},
    {"id": "s27-correction", "kind": "doc", "query": "docs/capture/s27-effect-postprocess-rewire.md",
     "expect": "CORRECTS",
     "note": "docs/capture/README.md:16 corrige S27 (verificado manualmente en Fase 3)"},
]


@dataclass
class Result:
    query_id: str
    method: str
    latency_s: float
    result_lines: int
    chars: int
    approx_tokens_estimate: int
    hit: bool


def run(cmd: list[str]) -> tuple[str, float]:
    start = time.perf_counter()
    proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, check=False)
    elapsed = time.perf_counter() - start
    return proc.stdout, elapsed


def bench_one(item: dict) -> list[Result]:
    results = []
    kind, query, expect = item["kind"], item["query"], item["expect"]

    if kind == "identifier":
        methods = {
            "rg_crudo": ["rg", "--line-number", "--no-heading", "--fixed-strings", query, "."],
            "search_exact": [PY, str(SEARCH), "exact", query],
            "ask": [PY, str(SEARCH), "ask", query, "--budget", "1000"],
        }
    elif kind == "concept":
        methods = {
            "rg_crudo_todas_palabras": ["rg", "--line-number", "--no-heading", "-i",
                                          "|".join(query.split()), "."],
            "search_text_fts5": [PY, str(SEARCH), "text", query, "--limit", "10"],
            "ask": [PY, str(SEARCH), "ask", query, "--budget", "1000"],
        }
    else:  # doc
        methods = {
            "search_graph": [PY, str(SEARCH), "graph", "--doc", query, "--direction", "in"],
            "search_claim": [PY, str(SEARCH), "claim", query],
            "ask": [PY, str(SEARCH), "ask", query, "--budget", "1000"],
        }

    for method, cmd in methods.items():
        out, elapsed = run(cmd)
        # El snippet de BM25 resalta coincidencias insertando '[' ']' DENTRO de los
        # tokens (p. ej. "1ST_[CURTAIN]_MG"); quitarlos antes de comparar o un acierto
        # real se contaría como fallo por culpa del marcado, no de la recuperación.
        normalized = out.lower().replace("[", "").replace("]", "")
        results.append(Result(
            query_id=item["id"], method=method, latency_s=round(elapsed, 4),
            result_lines=len(out.strip().splitlines()) if out.strip() else 0,
            chars=len(out), approx_tokens_estimate=round(len(out) / 4),
            hit=expect.lower() in normalized,
        ))
    return results


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(ROOT / "knowledge" / "benchmarks" / "report.md"))
    args = ap.parse_args()

    all_results: list[Result] = []
    for item in REFERENCE_QUERIES:
        all_results.extend(bench_one(item))

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    json_path = out_path.with_suffix(".json")
    json_path.write_text(
        json.dumps([asdict(r) for r in all_results], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    lines = [
        "# Benchmark de recuperación — Sony A6000 (generado, no editar a mano)",
        "",
        ("Verdad de referencia fijada MANUALMENTE antes de ejecutar este script (ver `note` "
         "de cada consulta en `scripts/knowledge/benchmark.py`), no generada por el propio "
         "sistema. `approx_tokens_estimate` = caracteres/4, SIEMPRE una aproximación: no hay "
         "tokenizador real disponible en este entorno."),
        "",
        "| Consulta | Método | Latencia (s) | Líneas | Chars | Tokens (aprox.) | Acierto |",
        "|---|---|---:|---:|---:|---:|---|",
    ]
    for r in all_results:
        lines.append(
            f"| {r.query_id} | {r.method} | {r.latency_s} | {r.result_lines} | {r.chars} | "
            f"{r.approx_tokens_estimate} | {'✓' if r.hit else '✗'} |"
        )
    hits = sum(1 for r in all_results if r.hit)
    lines.append(f"\nAciertos: {hits}/{len(all_results)} comparaciones método×consulta.")
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"{out_path} y {json_path} escritos. Aciertos: {hits}/{len(all_results)}.")


if __name__ == "__main__":
    main()
