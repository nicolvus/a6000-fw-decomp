#!/usr/bin/env python3
"""Genera docs/CORRECTIONS.md y docs/OPEN-QUESTIONS.md a partir del grafo ya construido.

Documentos DERIVADOS y regenerables: no editar a mano, volver a correr este script
tras build_graph.py. Fuente única de verdad = tabla `relations` de la misma DB.
Uso: python3 scripts/knowledge/export_corrections.py [--db RUTA]
"""

import argparse
import sqlite3
from pathlib import Path

from _paths import find_root

ROOT = find_root()
DEFAULT_DB = ROOT / ".knowledge-cache" / "knowledge.sqlite"

HEADER = """# {label}

> **Generado automáticamente** por `scripts/knowledge/export_corrections.py` desde el
> grafo de conocimiento (`entities`/`relations` en `.knowledge-cache/knowledge.sqlite`).
> No editar a mano: reindexar con `index_docs.py` + `build_graph.py` y volver a ejecutar
> este script. Cada fila conserva su fuente exacta (archivo:línea) y cita textual.

"""


def export_corrections(conn: sqlite3.Connection, out: Path) -> int:
    rows = conn.execute(
        "SELECT type, status, src_id, dst_id, source_path, line_start, line_end, evidence "
        "FROM relations WHERE type IN ('CORRECTS', 'SUPERSEDES') "
        "ORDER BY source_path, line_start"
    ).fetchall()
    lines = [HEADER.format(label="Correcciones y relaciones superadas (CORRECTS / SUPERSEDES)")]
    lines.append(f"Total: {len(rows)} relaciones detectadas de forma determinista "
                  "(palabras clave del propio autor + enlace o referencia de sesión resuelta sin "
                  "ambigüedad). No implica que todas estén verificadas: ver columna `status`.\n")
    lines.append("| Tipo | Status | Corrige/supera a | Fuente | Evidencia |")
    lines.append("|---|---|---|---|---|")
    for type_, status, src, dst, source_path, line_start, line_end, evidence in rows:
        quote = evidence.strip().replace("\n", " ").replace("|", "\\|")[:160]
        lines.append(
            f"| {type_} | {status} | [{dst}]({_rel(dst)}) | "
            f"[{source_path}:{line_start}]({_rel(source_path)}) | {quote} |"
        )
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return len(rows)


def export_open_questions(conn: sqlite3.Connection, out: Path) -> int:
    """Antes esto buscaba por texto libre la palabra NO_VERIFICADO/CONFLICTO_PENDIENTE en
    cualquier sección (falso positivo: una sección que solo EXPLICA el vocabulario de status,
    p. ej. una tabla de referencia, se contaba como pregunta abierta). Ahora sale del grafo:
    relaciones reales con ese status, que afectan a un documento/afirmación concreto."""
    rows = conn.execute(
        "SELECT DISTINCT dst_id, type, status, source_path, line_start, evidence FROM relations "
        "WHERE status IN ('NO_VERIFICADO', 'CONFLICTO_PENDIENTE') "
        "ORDER BY source_path, line_start"
    ).fetchall()
    lines = [HEADER.format(label="Preguntas abiertas (relaciones NO_VERIFICADO / CONFLICTO_PENDIENTE)")]
    lines.append(f"Total: {len(rows)} relación(es) del grafo con status realmente abierto "
                  "(no secciones que solo mencionan la palabra en prosa).\n")
    lines.append("| Afecta a | Tipo | Status | Fuente | Evidencia |")
    lines.append("|---|---|---|---|---|")
    for dst, type_, status, source_path, line_start, evidence in rows:
        quote = evidence.strip().replace("\n", " ").replace("|", "\\|")[:160]
        lines.append(
            f"| [{dst}]({_rel(dst)}) | {type_} | {status} | "
            f"[{source_path}:{line_start}]({_rel(source_path)}) | {quote} |"
        )
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return len(rows)


def _rel(path: str) -> str:
    """Los documentos generados viven en docs/; path es relativo a la raíz del repo."""
    return "../" + path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", default=str(DEFAULT_DB))
    args = ap.parse_args()
    conn = sqlite3.connect(args.db)

    docs_dir = ROOT / "docs"
    docs_dir.mkdir(exist_ok=True)
    n_corr = export_corrections(conn, docs_dir / "CORRECTIONS.md")
    n_open = export_open_questions(conn, docs_dir / "OPEN-QUESTIONS.md")
    conn.close()
    print(f"docs/CORRECTIONS.md: {n_corr} filas.")
    print(f"docs/OPEN-QUESTIONS.md: {n_open} filas.")


if __name__ == "__main__":
    main()
