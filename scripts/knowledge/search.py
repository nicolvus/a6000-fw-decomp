#!/usr/bin/env python3
"""Búsqueda exacta (ripgrep) + textual (SQLite FTS5/BM25) sobre la documentación.

Uso:
  python3 scripts/knowledge/search.py exact "0x4383fd6c"
  python3 scripts/knowledge/search.py text "SilentShutter EFCS" [--limit 10]
"""

import argparse
import re
import sqlite3
import subprocess
import time
from pathlib import Path

from _paths import find_root

ROOT = find_root()
DEFAULT_DB = ROOT / ".knowledge-cache" / "knowledge.sqlite"
DOC_DIRS = ["docs", "reports", "analysis", "references", "research"]
RG_TIMEOUT_S = 10.0  # corta el proceso si rg tarda demasiado (p. ej. patrón costoso)
RG_MAX_SCAN = 5000  # tope de líneas LEÍDAS del pipe, no solo mostradas: evita materializar
# salidas de cientos de MB en memoria cuando hay muchísimas coincidencias.


def _doc_paths() -> list[str]:
    paths = [d for d in DOC_DIRS if (ROOT / d).exists()]
    for extra in ("README.md", "CONTEXT.md"):
        if (ROOT / extra).exists():
            paths.append(extra)
    return paths


def _rg_stream(query: str, paths: list[str], limit: int) -> tuple[list[str], int, bool]:
    """Ejecuta rg y lee su pipe línea a línea (sin `capture_output`, que bufferiza TODA la
    salida en memoria antes de devolver nada). Corta en cuanto se alcanza RG_MAX_SCAN o
    RG_TIMEOUT_S, para no materializar salidas de cientos de MB por unas pocas coincidencias.
    Devuelve (líneas mostradas hasta `limit`, total de líneas leídas, si se cortó por tope)."""
    proc = subprocess.Popen(
        ["rg", "--line-number", "--no-heading", "--fixed-strings", query, *paths],
        cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
    )
    assert proc.stdout is not None
    shown: list[str] = []
    total = 0
    start = time.monotonic()
    capped = False
    for line in proc.stdout:
        total += 1
        if len(shown) < limit:
            shown.append(line.rstrip("\n"))
        if total >= RG_MAX_SCAN or (time.monotonic() - start) > RG_TIMEOUT_S:
            capped = True
            proc.terminate()
            break
    proc.stdout.close()
    stderr = proc.stderr.read() if proc.stderr else ""
    if proc.stderr:
        proc.stderr.close()
    returncode = proc.wait(timeout=5)
    if not capped and returncode not in (0, 1):
        raise SystemExit(stderr)
    return shown, total, capped


def cmd_exact(query: str, limit: int) -> None:
    """Grep literal (símbolos, direcciones hex, rutas) sobre la documentación.
    `--max-count` de rg limita por ARCHIVO, no en total (con muchos archivos la salida
    combinada podía seguir siendo enorme); el límite real y global se aplica en streaming."""
    shown, total, capped = _rg_stream(query, _doc_paths(), limit)
    if not shown:
        print("Sin coincidencias exactas.")
        return
    print("\n".join(shown))
    if len(shown) < total or capped:
        suffix = "+" if capped else ""
        print(f"\n[{len(shown)}/{total}{suffix} líneas mostradas (límite global); "
              f"usa --limit para ampliar]")


def cmd_text(query: str, limit: int, db: str, offset: int = 0) -> None:
    db_path = Path(db)
    if not db_path.exists():
        raise SystemExit(f"No existe {db_path}. Ejecuta primero index_docs.py")
    conn = sqlite3.connect(db_path)
    fts_query = " OR ".join(re.findall(r"\w+", query)) or query
    rows = conn.execute(
        "SELECT path, heading, line_start, bm25(sections) AS rank, "
        "snippet(sections, 4, '[', ']', '...', 20) AS snip "
        "FROM sections WHERE sections MATCH ? ORDER BY rank LIMIT ? OFFSET ?",
        (fts_query, limit, offset),
    ).fetchall()
    conn.close()
    if not rows:
        print("Sin coincidencias textuales." if offset == 0 else "Sin más coincidencias (fin de la paginación).")
        return
    for path, heading, line_start, _, snip in rows:
        print(f"{path}:{line_start}  [{heading}]")
        print(f"  {snip}")
    print(f"\n[mostrando {offset + 1}-{offset + len(rows)}; usa --offset {offset + limit} "
          "para la siguiente página]")


def cmd_tree(db: str, subsystem: str | None, doc: str | None) -> None:
    """Navegación jerárquica Subsistema -> Documento -> Sección (sin cargar el cuerpo)."""
    conn = sqlite3.connect(db)
    if doc:
        rows = conn.execute(
            "SELECT id, level, heading, line_start, line_end FROM nodes "
            "WHERE doc_id = ? ORDER BY seq", (doc,),
        ).fetchall()
        for nid, level, heading, line_start, line_end in rows:
            print(f"{'  ' * level}[{nid}] {heading}  ({line_start}-{line_end})")
    else:
        query = "SELECT id, path, subsystem, title FROM documents"
        params: tuple = ()
        if subsystem:
            query += " WHERE subsystem = ?"
            params = (subsystem,)
        for doc_id, path, subs, title in conn.execute(query + " ORDER BY path", params):
            print(f"[{subs}] {path} — {title}  (doc_id={doc_id})")
    conn.close()


def cmd_section(db: str, node_id: str, subtree: bool = False) -> None:
    """Recupera el texto original (desde el archivo) de un nodo por id estable.
    --subtree amplía el fragmento: por defecto line_end es solo el contenido PROPIO de la
    sección (hasta su primer sub-encabezado, si tiene); con --subtree se extiende hasta el
    siguiente encabezado del mismo nivel o superior (incluye todos los descendientes)."""
    conn = sqlite3.connect(db)
    row = conn.execute(
        "SELECT doc_id, heading, level, line_start, line_end, seq FROM nodes WHERE id = ?",
        (node_id,),
    ).fetchone()
    if not row:
        conn.close()
        raise SystemExit(f"Nodo no encontrado: {node_id}")
    doc_id, heading, level, line_start, line_end, seq = row
    if subtree:
        next_sibling_or_higher = conn.execute(
            "SELECT line_start FROM nodes WHERE doc_id = ? AND seq > ? AND level <= ? "
            "ORDER BY seq LIMIT 1", (doc_id, seq, level),
        ).fetchone()
        if next_sibling_or_higher:
            line_end = next_sibling_or_higher[0] - 1
        else:
            total = len((ROOT / doc_id).read_text(encoding="utf-8", errors="replace").splitlines())
            line_end = total
    conn.close()
    lines = (ROOT / doc_id).read_text(encoding="utf-8", errors="replace").splitlines()
    print(f"# {doc_id}:{line_start}-{line_end}  [{heading}]" + ("  (subárbol completo)" if subtree else ""))
    print("\n".join(lines[line_start - 1:line_end]))


def cmd_graph(db: str, doc: str | None, rel_type: str | None, direction: str) -> None:
    """Consulta el grafo: qué corrige/es corregido por un documento, con evidencia."""
    conn = sqlite3.connect(db)
    col_self, col_other = ("src_id", "dst_id") if direction == "out" else ("dst_id", "src_id")
    query = f"SELECT type, status, {col_other}, source_path, line_start, line_end, evidence FROM relations"
    clauses, params = [], []
    if doc:
        clauses.append(f"{col_self} = ?")
        params.append(doc)
    if rel_type:
        clauses.append("type = ?")
        params.append(rel_type)
    if clauses:
        query += " WHERE " + " AND ".join(clauses)
    for type_, status, other, source_path, line_start, line_end, evidence in conn.execute(
        query + " ORDER BY source_path, line_start", params
    ):
        print(f"[{status}] {type_} -> {other}")
        print(f"  fuente: {source_path}:{line_start}-{line_end}")
        print(f"  evidencia: {evidence.strip()[:200]}")
    conn.close()


def cmd_trace(db: str, start: str, direction: str, max_hops: int, rel_type: str | None = None) -> None:
    """Consulta multietapa (Fase 12.5): recorre relaciones reales desde `start` hasta
    `max_hops` saltos (BFS, sin ciclos), imprimiendo cada arista con su evidencia y
    procedencia. Nunca inventa un salto: si no hay relación registrada en el grafo, el
    recorrido simplemente no avanza por esa rama."""
    conn = sqlite3.connect(db)
    col_self, col_other = ("src_id", "dst_id") if direction == "out" else ("dst_id", "src_id")
    visited = {start}
    frontier = [start]
    total_edges = 0
    for depth in range(max_hops):
        next_frontier = []
        for node in frontier:
            query = (f"SELECT type, status, {col_other}, source_path, line_start, evidence "
                     f"FROM relations WHERE {col_self} = ?")
            params: list[str] = [node]
            if rel_type:
                query += " AND type = ?"
                params.append(rel_type)
            for type_, status, other, source_path, line_start, evidence in conn.execute(query, params):
                if other in visited:
                    continue  # evita ciclos: cada nodo se visita una sola vez en el recorrido
                visited.add(other)
                indent = "  " * depth
                print(f"{indent}[salto {depth + 1}] [{status}] {node} --{type_}--> {other}")
                print(f"{indent}  fuente: {source_path}:{line_start}")
                print(f"{indent}  evidencia: {evidence.strip()[:150]}")
                next_frontier.append(other)
                total_edges += 1
        frontier = next_frontier
        if not frontier:
            break
    if total_edges == 0:
        print(f"Sin relaciones desde {start} en esa dirección (0 saltos): el grafo actual "
              "no conecta este nodo con nada más, no es evidencia de que no exista relación.")
    conn.close()


def cmd_claim(db: str, doc: str) -> None:
    """Conclusión vigente de un documento: lo que lo corrige/supera (entrante) tiene prioridad."""
    conn = sqlite3.connect(db)
    incoming = conn.execute(
        "SELECT type, status, src_id, source_path, line_start, evidence FROM relations "
        "WHERE dst_id = ? ORDER BY line_start", (doc,),
    ).fetchall()
    conn.close()
    if not incoming:
        print(f"Sin correcciones registradas sobre {doc} en el grafo actual. Esto NO demuestra "
              "que la fuente esté vigente: solo significa que ningún otro documento indexado "
              "la corrige explícitamente todavía (puede no estar reindexado, o la corrección "
              "puede existir en prosa sin enlace/referencia de sesión resoluble).")
        return
    print(f"{doc} tiene {len(incoming)} relación(es) entrante(s) (más reciente puede no ser la última):")
    for type_, status, src, source_path, line_start, evidence in incoming:
        print(f"  [{status}] {src} --{type_}--> este documento")
        print(f"    fuente: {source_path}:{line_start}")
        print(f"    evidencia: {evidence.strip()[:200]}")


IDENTIFIER_RE = re.compile(r"^(0x[0-9a-fA-F]+|[A-Za-z_][\w:]*\(?\)?)$")
DOC_PATH_RE = re.compile(r"^[\w./-]+\.md$")


def classify_query(query: str) -> str:
    """identifier (dirección/símbolo exacto) | doc (ruta .md) | concept (texto libre)."""
    query = query.strip()
    if DOC_PATH_RE.match(query):
        return "doc"
    if IDENTIFIER_RE.match(query):
        return "identifier"
    return "concept"


def _budget_print(blocks: list[str], budget: int) -> None:
    used, shown = 0, 0
    for block in blocks:
        if used + len(block) > budget:
            if shown == 0:
                # el primer resultado por sí solo supera el presupuesto: antes se imprimía
                # entero igualmente (el presupuesto quedaba sin efecto); se trunca para que
                # ningún caso pueda superarlo.
                remaining = max(0, budget - used)
                print(block[:remaining] + ("\n[...truncado por --budget]" if remaining < len(block) else ""))
                used += remaining
                shown += 1
            break
        print(block)
        used += len(block)
        shown += 1
    print(f"\n[{shown}/{len(blocks)} resultado(s) mostrados, ~{used}/{budget} caracteres de "
          f"presupuesto; usa --budget para ampliar]")


def cmd_ask(db: str, query: str, budget: int) -> None:
    """Enrutador de recuperación adaptativa: elige método(s) según el tipo de consulta,
    deduplica por (ruta, línea) y recorta al presupuesto de caracteres indicado."""
    kind = classify_query(query)
    print(f"[router] consulta clasificada como: {kind}")
    conn = sqlite3.connect(db)
    blocks: list[str] = []
    seen: set[tuple[str, int]] = set()

    def add(path: str, line: int, text: str) -> None:
        key = (path, line)
        if key in seen:
            return
        seen.add(key)
        blocks.append(text)

    if kind == "doc":
        try:
            doc_relations = conn.execute(
                "SELECT type, status, src_id, source_path, line_start, evidence FROM relations "
                "WHERE dst_id = ? ORDER BY line_start", (query,),
            ).fetchall()
        except sqlite3.OperationalError:
            doc_relations = []
        for type_, status, src, source_path, line_start, evidence in doc_relations:
            add(source_path, line_start,
                f"[{status}] {src} --{type_}--> {query}\n  fuente: {source_path}:{line_start}\n"
                f"  evidencia: {evidence.strip()[:200]}")
        for nid, level, heading, line_start, line_end in conn.execute(
            "SELECT id, level, heading, line_start, line_end FROM nodes "
            "WHERE doc_id = ? ORDER BY seq", (query,),
        ):
            add(query, line_start, f"{'  ' * level}[{nid}] {heading}  ({line_start}-{line_end})")

    elif kind == "identifier":
        shown, _total, _capped = _rg_stream(query, _doc_paths(), limit=20)
        for line in shown:
            m = re.match(r"^([^:]+):(\d+):(.*)$", line)
            if m:
                add(m.group(1), int(m.group(2)), line)

    else:  # concept
        fts_query = " OR ".join(re.findall(r"\w+", query)) or query
        for path, heading, line_start, _, snip in conn.execute(
            "SELECT path, heading, line_start, bm25(sections) AS rank, "
            "snippet(sections, 4, '[', ']', '...', 20) AS snip "
            "FROM sections WHERE sections MATCH ? ORDER BY rank LIMIT 15", (fts_query,),
        ):
            add(path, line_start, f"{path}:{line_start}  [{heading}]\n  {snip}")
            try:
                corrections = conn.execute(
                    "SELECT type, status, src_id, source_path, line_start FROM relations "
                    "WHERE dst_id = ? LIMIT 3", (path,),
                ).fetchall()
            except sqlite3.OperationalError:
                corrections = []  # build_graph.py no se ha ejecutado todavía: degradar sin fallar
            for type_, status, src, source_path, cline in corrections:
                add(source_path, cline,
                    f"  [corrección relacionada] [{status}] {src} --{type_}--> {path}")

    conn.close()
    if not blocks:
        print("Sin resultados.")
        return
    _budget_print(blocks, budget)


def cmd_freshness(db: str) -> None:
    """Compara el hash SHA-256 actual de cada doc contra el guardado en la tabla files:
    detecta archivos editados/añadidos/eliminados desde el último index_docs.py."""
    import index_docs  # mismo directorio; import tardío para no acoplar módulos en el resto de comandos
    index_docs.ROOT = ROOT  # evita que una versión cacheada de index_docs (import previo con
    # otro cwd) use un ROOT obsoleto; este módulo es la única fuente de verdad en tiempo de uso

    db_path = Path(db)
    if not db_path.exists():
        raise SystemExit(f"No existe {db_path}. Ejecuta primero index_docs.py")
    conn = sqlite3.connect(db_path)
    known = dict(conn.execute("SELECT path, sha256 FROM files"))
    conn.close()

    seen = set()
    changed, added = [], []
    for fpath in index_docs.iter_doc_files():
        rel = str(fpath.relative_to(ROOT))
        seen.add(rel)
        digest = index_docs.sha256_of(fpath)
        if rel not in known:
            added.append(rel)
        elif known[rel] != digest:
            changed.append(rel)
    removed = sorted(set(known) - seen)

    if not changed and not added and not removed:
        print("Índice al día: coincide con los archivos actuales.")
        return
    print("Índice DESACTUALIZADO. Ejecuta index_docs.py antes de confiar en los resultados:")
    for rel in sorted(added):
        print(f"  + nuevo sin indexar: {rel}")
    for rel in sorted(changed):
        print(f"  ~ modificado desde el último índice: {rel}")
    for rel in removed:
        print(f"  - eliminado pero sigue en el índice: {rel}")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="mode", required=True)

    p_exact = sub.add_parser("exact", help="grep literal (símbolos, direcciones, rutas)")
    p_exact.add_argument("query")
    p_exact.add_argument("--limit", type=int, default=50)

    p_text = sub.add_parser("text", help="búsqueda textual BM25 sobre secciones indexadas")
    p_text.add_argument("query")
    p_text.add_argument("--limit", type=int, default=10)
    p_text.add_argument("--offset", type=int, default=0, help="paginación: saltar N resultados")
    p_text.add_argument("--db", default=str(DEFAULT_DB))

    p_tree = sub.add_parser("tree", help="navega Subsistema->Documento->Sección")
    p_tree.add_argument("--subsystem", default=None)
    p_tree.add_argument("--doc", default=None, help="path relativo del documento (doc_id)")
    p_tree.add_argument("--db", default=str(DEFAULT_DB))

    p_section = sub.add_parser("section", help="recupera el texto original de un nodo por id")
    p_section.add_argument("node_id")
    p_section.add_argument("--subtree", action="store_true",
                            help="incluye todos los sub-encabezados descendientes, no solo el contenido propio")
    p_section.add_argument("--db", default=str(DEFAULT_DB))

    p_graph = sub.add_parser("graph", help="consulta relaciones CALLS/CORRECTS/SUPERSEDES")
    p_graph.add_argument("--doc", default=None, help="documento o entidad de origen/destino")
    p_graph.add_argument("--type", dest="rel_type", default=None)
    p_graph.add_argument("--direction", choices=["out", "in"], default="out")
    p_graph.add_argument("--db", default=str(DEFAULT_DB))

    p_trace = sub.add_parser("trace", help="consulta multietapa: recorre relaciones N saltos desde un nodo")
    p_trace.add_argument("start", help="id de entidad o documento de partida")
    p_trace.add_argument("--direction", choices=["out", "in"], default="out")
    p_trace.add_argument("--type", dest="rel_type", default=None)
    p_trace.add_argument("--max-hops", type=int, default=3)
    p_trace.add_argument("--db", default=str(DEFAULT_DB))

    p_claim = sub.add_parser("claim", help="conclusión vigente de un documento y qué lo corrige")
    p_claim.add_argument("doc")
    p_claim.add_argument("--db", default=str(DEFAULT_DB))

    p_ask = sub.add_parser("ask", help="recuperación adaptativa: elige método según el tipo de consulta")
    p_ask.add_argument("query")
    p_ask.add_argument("--budget", type=int, default=2000, help="presupuesto en caracteres")
    p_ask.add_argument("--db", default=str(DEFAULT_DB))

    p_fresh = sub.add_parser("freshness", help="compara el índice contra los archivos actuales")
    p_fresh.add_argument("--db", default=str(DEFAULT_DB))

    args = ap.parse_args()
    if args.mode == "exact":
        cmd_exact(args.query, args.limit)
    elif args.mode == "text":
        cmd_text(args.query, args.limit, args.db, args.offset)
    elif args.mode == "tree":
        cmd_tree(args.db, args.subsystem, args.doc)
    elif args.mode == "section":
        cmd_section(args.db, args.node_id, args.subtree)
    elif args.mode == "graph":
        cmd_graph(args.db, args.doc, args.rel_type, args.direction)
    elif args.mode == "trace":
        cmd_trace(args.db, args.start, args.direction, args.max_hops, args.rel_type)
    elif args.mode == "claim":
        cmd_claim(args.db, args.doc)
    elif args.mode == "ask":
        cmd_ask(args.db, args.query, args.budget)
    elif args.mode == "freshness":
        cmd_freshness(args.db)


if __name__ == "__main__":
    main()
