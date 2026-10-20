#!/usr/bin/env python3
"""Servidor MCP local, de solo lectura, sobre el sistema de conocimiento Sony A6000.

No reimplementa la lógica de búsqueda: cada herramienta reutiliza las mismas
funciones que la CLI (`search.py`), capturando su salida formateada. Una única
base de conocimiento (`.knowledge-cache/knowledge.sqlite`) para Claude Code y Codex.

Ejecutar (stdio, el transporte que ambos clientes MCP usan localmente):
  source .venv/bin/activate && python3 scripts/knowledge/mcp_server.py
"""

import contextlib
import io
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import search
from mcp.server.mcpserver import MCPServer

DB = str(search.DEFAULT_DB)
ROOT = search.ROOT
server = MCPServer(
    name="sony-a6000-knowledge",
    instructions=(
        "Conocimiento técnico del proyecto Sony A6000 (ingeniería inversa de firmware). "
        "Solo lectura. Usa search_exact para direcciones/símbolos exactos, search_documents "
        "para conceptos, search_hybrid cuando no sepas cuál usar, query_graph/find_corrections "
        "para relaciones CORRECTS/SUPERSEDES verificables, get_document_section para texto "
        "original citable, get_open_questions para hallazgos NO_VERIFICADO/CONFLICTO_PENDIENTE, "
        "get_current_state para el resumen operativo vigente."
    ),
)


MCP_MAX_CHARS = 20000  # límite global y efectivo de salida por llamada a herramienta MCP:
# antes cada tool reenviaba la salida de la CLI sin tope propio, así que un --limit/--budget
# grande (o pedido por un cliente MCP que no respeta los defaults de la CLI) podía devolver
# una respuesta arbitrariamente grande igualmente.


def _cap_chars(out: str, offset: int = 0) -> str:
    """Tope global de caracteres, con paginación por `offset`: antes get_current_state
    devolvía el archivo completo sin ningún límite (bug de la auditoría, Fase 12.2.D)."""
    out = out[offset:]
    if len(out) > MCP_MAX_CHARS:
        return (out[:MCP_MAX_CHARS]
                + f"\n[truncado a {MCP_MAX_CHARS} caracteres desde offset={offset} "
                  f"(límite MCP); usa offset={offset + MCP_MAX_CHARS} para continuar]")
    return out


def _captured(fn, *args, **kwargs) -> str:
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        try:
            fn(*args, **kwargs)
        except SystemExit as exc:
            return str(exc)
    return _cap_chars(buf.getvalue() or "Sin resultados.")


@server.tool()
def search_exact(query: str, limit: int = 20) -> str:
    """Búsqueda exacta (ripgrep) de una dirección hexadecimal, símbolo o ruta literal."""
    return _captured(search.cmd_exact, query, limit)


@server.tool()
def search_documents(query: str, limit: int = 10) -> str:
    """Búsqueda textual BM25 sobre las secciones Markdown indexadas (conceptos, no símbolos)."""
    return _captured(search.cmd_text, query, limit, DB)


@server.tool()
def search_hybrid(query: str, budget: int = 2000) -> str:
    """Recuperación adaptativa: clasifica la consulta (identificador/documento/concepto) y
    combina los métodos pertinentes, recortando al presupuesto de caracteres dado."""
    return _captured(search.cmd_ask, DB, query, budget)


@server.tool()
def find_symbol(symbol: str, limit: int = 20) -> str:
    """Alias de search_exact para direcciones o nombres de función/símbolo."""
    return _captured(search.cmd_exact, symbol, limit)


@server.tool()
def get_document_section(node_id: str, subtree: bool = False) -> str:
    """Recupera el texto ORIGINAL (desde el archivo fuente) de una sección por su id estable
    (obtenido de query_graph o de recorrer el árbol documental con la CLI `tree`).
    subtree=False (por defecto): solo el contenido propio de la sección, sin sub-encabezados.
    subtree=True: la sección completa, incluidos todos sus descendientes."""
    return _captured(search.cmd_section, DB, node_id, subtree)


@server.tool()
def check_index_freshness() -> str:
    """Comprueba si el índice SQLite corresponde a la versión ACTUAL de los archivos
    Markdown (por hash SHA-256), o si hay archivos editados/añadidos/eliminados desde el
    último index_docs.py que invalidarían los resultados de las demás herramientas."""
    return _captured(search.cmd_freshness, DB)


@server.tool()
def query_graph(doc: str | None = None, rel_type: str | None = None, direction: str = "out") -> str:
    """Consulta relaciones del grafo (CALLS/CORRECTS/SUPERSEDES) con procedencia y evidencia.
    direction='out': lo que `doc` corrige/supera/llama. direction='in': lo que corrige a `doc`."""
    return _captured(search.cmd_graph, DB, doc, rel_type, direction)


@server.tool()
def trace_relations(
    start: str, direction: str = "out", rel_type: str | None = None, max_hops: int = 3,
) -> str:
    """Consulta técnica multietapa: recorre relaciones reales desde `start` hasta
    `max_hops` saltos (p. ej. llamadores de llamadores, o cadenas CORRECTS/SUPERSEDES
    encadenadas), con evidencia y procedencia de cada salto. No inventa saltos sin
    relación registrada en el grafo."""
    return _captured(search.cmd_trace, DB, start, direction, max_hops, rel_type)


@server.tool()
def find_corrections(doc: str) -> str:
    """Qué corrige o supera a `doc`, y qué `doc` corrige o supera — conclusión vigente."""
    return _captured(search.cmd_claim, DB, doc)


@server.tool()
def get_open_questions(limit: int = 50, offset: int = 0) -> str:
    """Lista de preguntas abiertas (NO_VERIFICADO/CONFLICTO_PENDIENTE) desde docs/OPEN-QUESTIONS.md."""
    path = ROOT / "docs" / "OPEN-QUESTIONS.md"
    if not path.exists():
        return "docs/OPEN-QUESTIONS.md no existe. Ejecuta export_corrections.py primero."
    lines = path.read_text(encoding="utf-8").splitlines()
    out = "\n".join(lines[:limit + 8])  # +8: cabecera + fila de totales + encabezado de tabla
    return _cap_chars(out, offset)


@server.tool()
def get_current_state(offset: int = 0) -> str:
    """Estado vigente del proyecto (docs/STATE.md): conclusión general, correcciones críticas
    y restricciones activas. `offset` pagina si el documento supera el límite MCP."""
    path = ROOT / "docs" / "STATE.md"
    if not path.exists():
        return "docs/STATE.md no existe."
    return _cap_chars(path.read_text(encoding="utf-8"), offset)


if __name__ == "__main__":
    server.run()
