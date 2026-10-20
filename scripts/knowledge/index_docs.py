#!/usr/bin/env python3
"""Indexa docs/reports/analysis/references/research (+README/CONTEXT) en SQLite FTS5.

Incremental por hash SHA-256 de archivo: solo reprocesa lo que cambió.
Uso: python3 scripts/knowledge/index_docs.py [--db RUTA] [--rebuild]
"""

import argparse
import hashlib
import re
import sqlite3
from pathlib import Path

from _paths import find_root

ROOT = find_root()
DEFAULT_DB = ROOT / ".knowledge-cache" / "knowledge.sqlite"
DOC_DIRS = ["docs", "reports", "analysis", "references", "research"]
ROOT_FILES = ["README.md", "CONTEXT.md"]

SCHEMA = """
CREATE TABLE IF NOT EXISTS files (
    path TEXT PRIMARY KEY,
    sha256 TEXT NOT NULL,
    mtime REAL NOT NULL
);
CREATE VIRTUAL TABLE IF NOT EXISTS sections USING fts5(
    path, heading, level, line_start, body, tokenize='porter unicode61'
);
CREATE TABLE IF NOT EXISTS documents (
    id TEXT PRIMARY KEY,
    path TEXT NOT NULL,
    subsystem TEXT NOT NULL,
    title TEXT
);
CREATE TABLE IF NOT EXISTS nodes (
    id TEXT PRIMARY KEY,
    doc_id TEXT NOT NULL REFERENCES documents(id),
    parent_id TEXT REFERENCES nodes(id),
    level INTEGER NOT NULL,
    heading TEXT NOT NULL,
    line_start INTEGER NOT NULL,
    line_end INTEGER NOT NULL,
    seq INTEGER NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_nodes_doc ON nodes(doc_id);
CREATE INDEX IF NOT EXISTS idx_nodes_parent ON nodes(parent_id);
"""


def subsystem_of(rel_path: str) -> str:
    """Repositorio -> Subsistema: los dos primeros componentes de la ruta, o '.' en la raíz."""
    parts = Path(rel_path).parts
    return "/".join(parts[:2]) if len(parts) > 1 else "."


def node_id(rel_path: str, heading: str, occurrence: int) -> str:
    """Identificador estable: no depende de orden global ni de contenido, solo de ruta+encabezado."""
    raw = f"{rel_path}::{heading}::{occurrence}"
    return hashlib.sha1(raw.encode("utf-8")).hexdigest()[:16]


def build_tree(rel_path: str, sections: list[tuple[str, int, int, str]], total_lines: int):
    """Construye nodos jerárquicos (parent = encabezado de nivel inmediatamente superior previo)."""
    occurrences: dict[str, int] = {}
    stack: list[tuple[int, str]] = []  # (level, node_id)
    nodes: list[tuple[str, str | None, int, str, int, int, int]] = []
    for idx, (heading, level, line_start, body) in enumerate(sections):
        occurrences[heading] = occurrences.get(heading, -1) + 1
        nid = node_id(rel_path, heading, occurrences[heading])
        line_end = (sections[idx + 1][2] - 1) if idx + 1 < len(sections) else total_lines
        if heading == "(preámbulo)":
            # nunca es ancestro de un encabezado real: no se empuja a la pila de niveles
            nodes.append((nid, None, level, heading, line_start, line_end, idx))
            continue
        while stack and stack[-1][0] >= level:
            stack.pop()
        parent_id = stack[-1][1] if stack else None
        nodes.append((nid, parent_id, level, heading, line_start, line_end, idx))
        stack.append((level, nid))
    return nodes


def sha256_of(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def split_sections(text: str) -> list[tuple[str, int, int, str]]:
    """Devuelve (heading, level, line_start, body) por cada encabezado Markdown."""
    lines = text.splitlines()
    heads = [(i, m.group(2), len(m.group(1)))
             for i, line in enumerate(lines)
             if (m := re.match(r"^(#{1,6})\s+(.*)$", line))]
    if not heads:
        return [("(sin encabezado)", 0, 0, text)]
    sections = []
    if heads[0][0] > 0:  # texto antes del primer encabezado: se perdía, ahora se conserva
        preamble = "\n".join(lines[:heads[0][0]]).strip()
        if preamble:
            # level -1: nunca debe quedar como padre de un encabezado real (nivel >= 1) en
            # build_tree, que hace pop de la pila mientras stack[-1].level >= level.
            sections.append(("(preámbulo)", -1, 1, preamble))
    for idx, (line_no, heading, level) in enumerate(heads):
        end = heads[idx + 1][0] if idx + 1 < len(heads) else len(lines)
        body = "\n".join(lines[line_no:end])
        sections.append((heading, level, line_no + 1, body))
    return sections


def iter_doc_files():
    for name in ROOT_FILES:
        p = ROOT / name
        if p.exists():
            yield p
    for d in DOC_DIRS:
        base = ROOT / d
        if base.exists():
            yield from base.rglob("*.md")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", default=str(DEFAULT_DB))
    ap.add_argument("--rebuild", action="store_true", help="Reindexa todo, ignorando hashes")
    args = ap.parse_args()

    db_path = Path(args.db)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.executescript(SCHEMA)

    known = dict(conn.execute("SELECT path, sha256 FROM files"))
    seen = set()
    changed = 0
    for fpath in iter_doc_files():
        rel = str(fpath.relative_to(ROOT))
        seen.add(rel)
        digest = sha256_of(fpath)
        if not args.rebuild and known.get(rel) == digest:
            continue
        changed += 1
        text = fpath.read_text(encoding="utf-8", errors="replace")
        total_lines = len(text.splitlines())
        sections = split_sections(text)

        conn.execute("DELETE FROM sections WHERE path = ?", (rel,))
        for heading, level, line_start, body in sections:
            conn.execute(
                "INSERT INTO sections (path, heading, level, line_start, body) VALUES (?,?,?,?,?)",
                (rel, heading, level, line_start, body),
            )

        conn.execute("DELETE FROM nodes WHERE doc_id = ?", (rel,))
        conn.execute("DELETE FROM documents WHERE id = ?", (rel,))
        titled_sections = [s for s in sections if s[0] != "(preámbulo)"]
        title = (titled_sections[0][0] if titled_sections and titled_sections[0][1] <= 1
                 else Path(rel).stem)
        conn.execute(
            "INSERT INTO documents (id, path, subsystem, title) VALUES (?,?,?,?)",
            (rel, rel, subsystem_of(rel), title),
        )
        for nid, parent_id, level, heading, line_start, line_end, seq in build_tree(
            rel, sections, total_lines
        ):
            conn.execute(
                "INSERT INTO nodes (id, doc_id, parent_id, level, heading, line_start, "
                "line_end, seq) VALUES (?,?,?,?,?,?,?,?)",
                (nid, rel, parent_id, level, heading, line_start, line_end, seq),
            )

        conn.execute(
            "INSERT INTO files (path, sha256, mtime) VALUES (?,?,?) "
            "ON CONFLICT(path) DO UPDATE SET sha256=excluded.sha256, mtime=excluded.mtime",
            (rel, digest, fpath.stat().st_mtime),
        )

    removed = set(known) - seen
    for rel in removed:
        conn.execute("DELETE FROM sections WHERE path = ?", (rel,))
        conn.execute("DELETE FROM nodes WHERE doc_id = ?", (rel,))
        conn.execute("DELETE FROM documents WHERE id = ?", (rel,))
        conn.execute("DELETE FROM files WHERE path = ?", (rel,))

    conn.commit()
    total_files = conn.execute("SELECT COUNT(*) FROM files").fetchone()[0]
    total_sections = conn.execute("SELECT COUNT(*) FROM sections").fetchone()[0]
    conn.close()
    print(f"Indexado: {changed} archivo(s) actualizado(s), {len(removed)} eliminado(s).")
    print(f"Total: {total_files} archivos, {total_sections} secciones. DB: {db_path}")


if __name__ == "__main__":
    main()
