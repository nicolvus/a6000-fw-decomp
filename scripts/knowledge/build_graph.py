#!/usr/bin/env python3
"""Grafo de conocimiento verificable: entidades Function + relaciones CALLS/CORRECTS/SUPERSEDES.

Fuentes, ambas deterministas (sin inferencia de LLM):
  1. JSON de funciones con forma {binary, sha256, address_space, symbol_value, original_name,
     outgoing}: crea entidades Function y relaciones CALLS solo cuando el destino en
     'outgoing' coincide por nombre con otra entidad del MISMO binario (misma sha256).
     Si no hay coincidencia exacta, se descarta (no se inventan destinos).
  2. Markdown indexado (tabla nodes de index_docs.py): busca palabras clave de corrección
     escritas por los propios investigadores ('CORRECCIÓN', 'corrige', 'SUPERADO', 'supera')
     y, dentro de la misma sección, un enlace Markdown a otro documento o una referencia de
     sesión ('sesión N' / 'SN') que resuelva a un documento existente por nombre de archivo.

Cada relación conserva: owner_source (archivo que la genera; reindexar/eliminar ese archivo
regenera/elimina solo sus relaciones), source_path, rango de líneas, cita textual (evidence)
y un status del vocabulario controlado (VERIFICADO/PARCIAL/NO_VERIFICADO/INFERENCIA/
DESCARTADO/SUPERADO/CONFLICTO_PENDIENTE), tomado del propio texto si está presente,
NO_VERIFICADO por defecto en caso contrario.

Requiere haber corrido antes index_docs.py (usa sus tablas documents/nodes).
Uso: python3 scripts/knowledge/build_graph.py [--db RUTA]
"""

import argparse
import hashlib
import json
import re
import sqlite3
from pathlib import Path

from _paths import find_root

ROOT = find_root()
DEFAULT_DB = ROOT / ".knowledge-cache" / "knowledge.sqlite"
FUNCTION_JSON_GLOB = ["analysis/**/*.json"]

STATUS_VOCAB = [
    "CONFLICTO_PENDIENTE", "NO_VERIFICADO", "VERIFICADO", "PARCIAL",
    "INFERENCIA", "DESCARTADO", "SUPERADO",
]
CORRECTION_RE = re.compile(r"CORRECCI[OÓ]N|corrig(e|i[oó]|iendo)", re.IGNORECASE)
SUPERSEDE_RE = re.compile(r"superad[ao]|\bsupera\b", re.IGNORECASE)
MD_LINK_RE = re.compile(r"\[[^\]]*\]\(([^)\s]+\.md)[^)]*\)")
SESSION_REF_RE = re.compile(r"[sS]esi[oó]n\s+(\d+)|\bS(\d+)\b")
NEGATION_RE = re.compile(r"\b(no|nunca|jam[aá]s|tampoco)\b", re.IGNORECASE)
# fin de oración real (. o ; seguido de espacio o fin de línea): un punto dentro de un
# nombre de archivo como "old.md" no debe cortar la oración a mitad de camino.
SENTENCE_END_RE = re.compile(r"[.;](?=\s|$)")


def is_negated(line: str, match_start: int) -> bool:
    """Caso reproducido por la auditoría: 'esta revisión no corrige [...]' generaba CORRECTS
    VERIFICADO pese a la negación. Busca una partícula negativa en TODA la oración que
    contiene la coincidencia (acotada por . o ; en ambos lados), no solo en una ventana
    corta de palabras previas: la auditoría señaló que un recorte arbitrario (p. ej. 4
    palabras) no demuestra que toda negación quede cubierta. Esto sigue siendo un filtro
    léxico determinista, no semántico: no reconoce negaciones dobles ni ironía; una
    construcción adversativa compleja puede seguir sin detectarse (ver limitación
    documentada en PROGRESS.md)."""
    prefix = line[:match_start]
    starts = [m.end() for m in SENTENCE_END_RE.finditer(prefix)]
    prefix = prefix[starts[-1]:] if starts else prefix
    end_match = SENTENCE_END_RE.search(line, match_start)
    suffix_end = end_match.start() if end_match else len(line)
    clause = prefix + line[match_start:suffix_end]
    return bool(NEGATION_RE.search(clause))

GRAPH_SCHEMA = """
CREATE TABLE IF NOT EXISTS entities (
    id TEXT PRIMARY KEY,
    kind TEXT NOT NULL,
    name TEXT,
    binary TEXT,
    binary_sha256 TEXT,
    address_space TEXT,
    address TEXT,
    owner_source TEXT NOT NULL,
    extra TEXT
);
CREATE TABLE IF NOT EXISTS entity_sources (
    entity_id TEXT NOT NULL REFERENCES entities(id),
    owner_source TEXT NOT NULL,
    original_name TEXT,
    confidence TEXT,
    PRIMARY KEY (entity_id, owner_source)
);
CREATE INDEX IF NOT EXISTS idx_entity_sources_entity ON entity_sources(entity_id);
CREATE TABLE IF NOT EXISTS relations (
    id TEXT PRIMARY KEY,
    src_id TEXT NOT NULL,
    dst_id TEXT NOT NULL,
    type TEXT NOT NULL,
    status TEXT NOT NULL,
    extraction_method TEXT NOT NULL,
    owner_source TEXT NOT NULL,
    source_path TEXT NOT NULL,
    line_start INTEGER,
    line_end INTEGER,
    evidence TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_relations_src ON relations(src_id);
CREATE INDEX IF NOT EXISTS idx_relations_dst ON relations(dst_id);
CREATE INDEX IF NOT EXISTS idx_relations_owner ON relations(owner_source);
CREATE INDEX IF NOT EXISTS idx_entities_owner ON entities(owner_source);
CREATE TABLE IF NOT EXISTS relation_sources (
    relation_id TEXT NOT NULL REFERENCES relations(id),
    owner_source TEXT NOT NULL,
    source_path TEXT NOT NULL,
    line_start INTEGER,
    line_end INTEGER,
    evidence TEXT NOT NULL,
    extraction_method TEXT NOT NULL,
    PRIMARY KEY (relation_id, owner_source)
);
CREATE INDEX IF NOT EXISTS idx_relation_sources_relation ON relation_sources(relation_id);
"""


def function_id(binary_sha256: str, address_space: str, symbol_value: str) -> str:
    raw = f"Function::{binary_sha256}::{address_space}::{symbol_value}"
    return hashlib.sha1(raw.encode("utf-8")).hexdigest()[:16]


def relation_id(src: str, dst: str, rel_type: str, source_path: str, line_start: int) -> str:
    raw = f"{src}::{dst}::{rel_type}::{source_path}::{line_start}"
    return hashlib.sha1(raw.encode("utf-8")).hexdigest()[:16]


def _upsert_call_relation(
    conn: sqlite3.Connection, src: str, dst: str, extraction_method: str,
    owner_source: str, source_path: str, evidence: str,
) -> bool:
    """Una sola relación CALLS por (origen, destino), aunque varias sesiones/archivos
    reanalicen el mismo binario y reporten la misma llamada: se deduplica por destino real
    (mismo patrón que entity_sources para funciones), registrando cada archivo que la
    respalda en relation_sources sin perder procedencia. Devuelve True si crea una
    relación nueva (para no inflar el conteo con duplicados)."""
    rid = relation_id(src, dst, "CALLS", "", 0)
    cur = conn.execute(
        "INSERT OR IGNORE INTO relations (id, src_id, dst_id, type, status, "
        "extraction_method, owner_source, source_path, line_start, line_end, evidence) "
        "VALUES (?,?,?,?,?,?,?,?,?,?,?)",
        (rid, src, dst, "CALLS", "PARCIAL", extraction_method, owner_source,
         source_path, None, None, evidence),
    )
    is_new = cur.rowcount > 0
    conn.execute(
        "INSERT OR REPLACE INTO relation_sources (relation_id, owner_source, source_path, "
        "line_start, line_end, evidence, extraction_method) VALUES (?,?,?,?,?,?,?)",
        (rid, owner_source, source_path, None, None, evidence, extraction_method),
    )
    return is_new


def method_name(original_name: str) -> str | None:
    """'ns::Clase::metodo()' -> 'metodo'. None si no hay forma reconocible."""
    match = re.search(r"([A-Za-z_][A-Za-z0-9_]*)\s*\(", original_name)
    return match.group(1) if match else None


def qualified_name(original_name: str) -> str | None:
    """'ns::Clase::metodo()' -> 'ns::Clase::metodo' (conserva el calificador). None si no
    hay forma reconocible. Se usa para desambiguar cuando dos clases del mismo binario
    comparten el mismo nombre de método corto (ver bug reproducido: X::caller() llama a
    A::run() pero el nombre corto 'run' también existe en B::run(), del mismo binario)."""
    match = re.search(r"([A-Za-z_][A-Za-z0-9_:]*)\s*\(", original_name)
    return match.group(1) if match else None


def _upsert_function_entity(
    conn: sqlite3.Connection, eid: str, name: str, binary: str | None, binary_sha256: str,
    address_space: str, address: str, owner_source: str, confidence: str | None,
    extra: str | None,
) -> bool:
    """Inserta la entidad Function si es nueva (primera fuente = nombre canónico); si ya
    existe con OTRO nombre para la misma identidad técnica, registra el conflicto en vez de
    sobrescribir. Siempre registra la procedencia en entity_sources (idempotente: una
    fuente puede volver a aportar la misma entidad sin duplicarla ni fallar). Devuelve True
    si creó una entidad nueva."""
    existing_name = conn.execute("SELECT name FROM entities WHERE id = ?", (eid,)).fetchone()
    created = False
    if existing_name is None:
        conn.execute(
            "INSERT INTO entities (id, kind, name, binary, binary_sha256, address_space, "
            "address, owner_source, extra) VALUES (?,?,?,?,?,?,?,?,?)",
            (eid, "Function", name, binary, binary_sha256, address_space, address,
             owner_source, extra),
        )
        created = True
    elif existing_name[0] != name:
        conn.execute(
            "UPDATE entities SET extra = ? WHERE id = ?",
            (json.dumps({"name_conflict": [existing_name[0], name],
                         "conflicting_source": owner_source}, ensure_ascii=False), eid),
        )
    conn.execute(
        "INSERT INTO entity_sources (entity_id, owner_source, original_name, confidence) "
        "VALUES (?,?,?,?) ON CONFLICT(entity_id, owner_source) DO UPDATE SET "
        "original_name=excluded.original_name, confidence=excluded.confidence",
        (eid, owner_source, name, confidence),
    )
    return created


def load_function_dossiers() -> list[tuple[str, list[dict]]]:
    """Localiza JSON con forma {binary, sha256, address_space, symbol_value, original_name,
    outgoing} bajo analysis/. No asume una ruta fija: filtra por forma, no por nombre de archivo."""
    found = []
    for pattern in FUNCTION_JSON_GLOB:
        for path in ROOT.glob(pattern):
            if "codex-logs" in path.parts:
                continue
            try:
                data = json.loads(path.read_text(encoding="utf-8", errors="replace"))
            except (json.JSONDecodeError, UnicodeDecodeError):
                continue
            if not isinstance(data, list):
                continue
            items = [d for d in data if isinstance(d, dict)
                     and {"binary", "sha256", "address_space", "symbol_value",
                          "original_name"} <= d.keys()]
            if items:
                found.append((str(path.relative_to(ROOT)), items))
    return found


GHIDRA_FUNCTIONS_GLOB = "analysis/**/*.json"
GHIDRA_CALL_RE = re.compile(r"FUN_([0-9a-fA-F]+)\s*\(")
GHIDRA_ADDR_FIELDS = ("entry", "query", "elf_entry", "ghidra_entry", "address")
GHIDRA_EXTRA_FIELDS = ("firmware_profile", "rom_base", "raw_base", "base", "method",
                       "language", "image_bias")


def load_ghidra_function_files() -> list[tuple[str, dict]]:
    """Localiza JSON con forma {source_sha256: str, functions: [...]} bajo analysis/: el
    formato dominante de los exports de Ghidra (confirmado por scripts/knowledge/
    inventory_json.py: ~430 archivos comparten esta forma bajo distintos nombres de
    investigación). Filtra por FORMA, no por ruta ni nombre de archivo."""
    found = []
    for path in ROOT.glob(GHIDRA_FUNCTIONS_GLOB):
        if "codex-logs" in path.parts:
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8", errors="replace"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            continue
        if (isinstance(data, dict) and isinstance(data.get("functions"), list)
                and isinstance(data.get("source_sha256"), str)):
            found.append((str(path.relative_to(ROOT)), data))
    return found


def _normalize_hex(raw: str) -> str:
    raw = raw.strip().lower()
    return raw.removeprefix("0x")


def _resolve_ghidra_address(item: dict) -> str | None:
    """Varios exports de Ghidra usan nombres de campo distintos para la misma dirección
    (entry/query/elf_entry/ghidra_entry/address); no hay un campo único consistente entre
    archivos (ver inventory_json.py). Se usa el primero presente, en este orden de
    preferencia ('query' puede ser solo el término buscado en casos de error, por eso va
    después de 'entry')."""
    for field in GHIDRA_ADDR_FIELDS:
        value = item.get(field)
        if isinstance(value, str) and value.strip():
            return _normalize_hex(value)
    return None


def build_ghidra_function_graph(
    conn: sqlite3.Connection, ghidra_files: list[tuple[str, dict]]
) -> tuple[int, int]:
    """Entidades Function desde pseudocódigo decompilado de Ghidra, y relaciones CALLS
    desde llamadas `FUN_<dirección>(...)` dentro del MISMO binario (binary_sha256). No se
    inventa address_space (Ghidra no lo reporta aquí): se usa 'unknown' explícito, nunca
    ARM/Thumb adivinado. Solo se crean entidades para funciones con status='decompiled'
    (ausencia de evidencia decompilada no se convierte en una entidad)."""
    n_entities = 0
    pseudo_by_owner: dict[str, list[tuple[str, str, str]]] = {}  # owner -> [(eid, sha256, pseudo)]

    for rel_path, data in ghidra_files:
        conn.execute("DELETE FROM entity_sources WHERE owner_source = ?", (rel_path,))
        conn.execute("DELETE FROM relation_sources WHERE owner_source = ?", (rel_path,))
        binary_sha256 = data["source_sha256"]
        extra_fields = {k: data[k] for k in GHIDRA_EXTRA_FIELDS if k in data}
        extra = json.dumps(extra_fields, ensure_ascii=False) if extra_fields else None
        pseudo_list: list[tuple[str, str, str]] = []
        for item in data["functions"]:
            if not isinstance(item, dict) or item.get("status") != "decompiled":
                continue  # sin decompilación real no hay evidencia de que la función exista así
            address = _resolve_ghidra_address(item)
            if not address:
                continue
            symbol_value = f"0x{address}"
            eid = function_id(binary_sha256, "unknown", symbol_value)
            name = f"FUN_{address}"
            if _upsert_function_entity(
                conn, eid, name, None, binary_sha256, "unknown", symbol_value,
                rel_path, None, extra,
            ):
                n_entities += 1
            pseudo = item.get("pseudo_code")
            if isinstance(pseudo, str) and pseudo.strip():
                pseudo_list.append((eid, binary_sha256, pseudo))
        pseudo_by_owner[rel_path] = pseudo_list

    n_relations = 0
    for rel_path, pseudo_list in pseudo_by_owner.items():
        for eid, binary_sha256, pseudo in pseudo_list:
            targets_seen: set[str] = set()
            for m in GHIDRA_CALL_RE.finditer(pseudo):
                target_hex = m.group(1).lower()
                if target_hex in targets_seen:
                    continue
                targets_seen.add(target_hex)
                rows = conn.execute(
                    "SELECT id FROM entities WHERE binary_sha256 = ? AND address = ? "
                    "AND kind = 'Function'",
                    (binary_sha256, f"0x{target_hex}"),
                ).fetchall()
                if len(rows) != 1:
                    continue  # 0 (sin evidencia en el corpus) o >1 (ambiguo): se descarta
                dst_id = rows[0][0]
                if dst_id == eid:
                    continue
                method = ("ghidra:pseudo_code_call_same_binary_via_thunk" if _is_thunk_call(pseudo, m.start())
                          else "ghidra:pseudo_code_call_same_binary")
                if _upsert_call_relation(
                    conn, eid, dst_id, method, rel_path, rel_path, pseudo.strip()[:400],
                ):
                    n_relations += 1
    return n_entities, n_relations


def _is_thunk_call(pseudo: str, match_start: int) -> bool:
    """Ghidra nombra el trampolín (stub de salto) en una dirección como 'thunk_FUN_<addr>':
    sigue siendo una llamada real a esa dirección, pero indirecta a través del trampolín,
    no una llamada directa al cuerpo de la función. Se distingue en extraction_method en
    vez de fusionarla silenciosamente con una llamada directa."""
    return pseudo[max(0, match_start - 6):match_start] == "thunk_"


REA_ADDRESS_COMMENT_RE = re.compile(r"/\*\s*([A-Za-z_][\w:]*)\s*\(\s*\)\s*\*/")
NAMED_CALL_RE = re.compile(r"\b([A-Za-z_][A-Za-z0-9_]*)\s*\(")


def load_rea_evidence_files() -> list[tuple[str, dict]]:
    """Localiza JSON con forma {subject: {digest: {sha256}}, operation, normalized_result}
    bajo analysis/: evidencia REA (herramienta de decompilación por evidencia), confirmada
    por inventory_json.py en 5 archivos bajo dos operaciones distintas:
    'procedure_pseudo_code' (una función, normalized_result=str) y 'batch_decompile'
    (varias funciones nombradas, normalized_result={'items': [...]})."""
    found = []
    for path in ROOT.glob(GHIDRA_FUNCTIONS_GLOB):
        if "codex-logs" in path.parts:
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8", errors="replace"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            continue
        subject = data.get("subject") if isinstance(data, dict) else None
        if (isinstance(subject, dict) and isinstance(subject.get("digest"), dict)
                and isinstance(subject["digest"].get("sha256"), str)
                and "normalized_result" in data and "operation" in data):
            found.append((str(path.relative_to(ROOT)), data))
    return found


def _rea_functions_from_file(data: dict) -> list[tuple[str, str, str]]:
    """Devuelve [(address_hex_sin_0x, name, pseudocode)] normalizando las dos formas REA
    conocidas. Solo incluye funciones con evidencia de decompilación real (status 'ok'/
    'resolved' en batch_decompile; cualquier texto no vacío en procedure_pseudo_code)."""
    out = []
    nr = data.get("normalized_result")
    if isinstance(nr, dict) and isinstance(nr.get("items"), list):
        for item in nr["items"]:
            if not isinstance(item, dict) or item.get("status") != "ok":
                continue
            proc = item.get("procedure")
            pseudocode = item.get("pseudocode")
            if not isinstance(proc, dict) or proc.get("status") != "resolved":
                continue
            address = proc.get("address")
            name = proc.get("name")
            if isinstance(address, str) and isinstance(name, str) and isinstance(pseudocode, str):
                out.append((_normalize_hex(address), name, pseudocode))
    elif isinstance(nr, str) and nr.strip() and data.get("operation") == "procedure_pseudo_code":
        address = None
        for loc in data.get("locations", []) if isinstance(data.get("locations"), list) else []:
            if isinstance(loc, dict) and loc.get("kind") == "address" and isinstance(loc.get("address"), str):
                address = loc["address"]
                break
        if address:
            comment = REA_ADDRESS_COMMENT_RE.search(nr)
            name = comment.group(1) if comment else f"FUN_{_normalize_hex(address)}"
            out.append((_normalize_hex(address), name, nr))
    return out


def build_rea_evidence_graph(
    conn: sqlite3.Connection, rea_files: list[tuple[str, dict]]
) -> tuple[int, int]:
    """Entidades Function desde evidencia REA (misma política de identidad parcial que el
    extractor Ghidra: address_space='unknown' explícito, nunca inventado) y relaciones
    CALLS desde llamadas por dirección (FUN_<hex>) o por NOMBRE (función ya resuelta en el
    mismo binario), descartando toda coincidencia ambigua."""
    n_entities = 0
    pseudo_by_owner: dict[str, list[tuple[str, str, str]]] = {}

    for rel_path, data in rea_files:
        conn.execute("DELETE FROM entity_sources WHERE owner_source = ?", (rel_path,))
        conn.execute("DELETE FROM relation_sources WHERE owner_source = ?", (rel_path,))
        binary_sha256 = data["subject"]["digest"]["sha256"]
        extra_fields = {"source_binary_name": data["subject"].get("name"),
                        "provider": (data.get("provider") or {}).get("name"),
                        "evidence_id": data.get("evidence_id")}
        extra = json.dumps({k: v for k, v in extra_fields.items() if v}, ensure_ascii=False)
        pseudo_list: list[tuple[str, str, str]] = []
        for address, name, pseudocode in _rea_functions_from_file(data):
            symbol_value = f"0x{address}"
            eid = function_id(binary_sha256, "unknown", symbol_value)
            if _upsert_function_entity(
                conn, eid, name, data["subject"].get("name"), binary_sha256, "unknown",
                symbol_value, rel_path, None, extra,
            ):
                n_entities += 1
            pseudo_list.append((eid, binary_sha256, pseudocode))
        pseudo_by_owner[rel_path] = pseudo_list

    n_relations = 0
    for rel_path, pseudo_list in pseudo_by_owner.items():
        for eid, binary_sha256, pseudo in pseudo_list:
            targets_seen: set[str] = set()
            for m in GHIDRA_CALL_RE.finditer(pseudo):
                target_hex = m.group(1).lower()
                if target_hex in targets_seen:
                    continue
                targets_seen.add(target_hex)
                rows = conn.execute(
                    "SELECT id FROM entities WHERE binary_sha256 = ? AND address = ? "
                    "AND kind = 'Function'", (binary_sha256, f"0x{target_hex}"),
                ).fetchall()
                if len(rows) != 1 or rows[0][0] == eid:
                    continue
                method = ("rea:pseudo_code_call_same_binary_via_thunk" if _is_thunk_call(pseudo, m.start())
                          else "rea:pseudo_code_call_same_binary")
                if _upsert_call_relation(
                    conn, eid, rows[0][0], method, rel_path, rel_path, pseudo.strip()[:400],
                ):
                    n_relations += 1
            names_seen: set[str] = set(targets_seen)  # no reintentar FUN_<hex> como nombre
            for m in NAMED_CALL_RE.finditer(pseudo):
                target_name = m.group(1)
                if target_name.startswith("FUN_") or target_name in names_seen:
                    continue
                names_seen.add(target_name)
                rows = conn.execute(
                    "SELECT id FROM entities WHERE binary_sha256 = ? AND name = ? "
                    "AND kind = 'Function'", (binary_sha256, target_name),
                ).fetchall()
                if len(rows) != 1 or rows[0][0] == eid:
                    continue
                if _upsert_call_relation(
                    conn, eid, rows[0][0], "rea:pseudo_code_named_call_same_binary",
                    rel_path, rel_path, pseudo.strip()[:400],
                ):
                    n_relations += 1
    return n_entities, n_relations


def build_function_graph(conn: sqlite3.Connection) -> tuple[int, int]:
    n_entities = n_relations = 0
    dossiers = load_function_dossiers()
    ghidra_files = load_ghidra_function_files()
    rea_files = load_rea_evidence_files()
    existing_sources = ({rel_path for rel_path, _ in dossiers}
                        | {rel_path for rel_path, _ in ghidra_files}
                        | {rel_path for rel_path, _ in rea_files})
    orphan_owners = {
        row[0] for row in conn.execute("SELECT DISTINCT owner_source FROM entity_sources")
    } - existing_sources
    for owner in orphan_owners:
        conn.execute("DELETE FROM entity_sources WHERE owner_source = ?", (owner,))
        conn.execute("DELETE FROM relation_sources WHERE owner_source = ?", (owner,))
    # una entidad solo se elimina cuando ningún dossier vivo sigue aportándola: puede
    # provenir de varios JSON (misma función reanalizada o exportada por dos herramientas).
    conn.execute(
        "DELETE FROM entities WHERE kind = 'Function' AND id NOT IN "
        "(SELECT DISTINCT entity_id FROM entity_sources)"
    )

    for rel_path, items in dossiers:
        conn.execute("DELETE FROM entity_sources WHERE owner_source = ?", (rel_path,))
        conn.execute("DELETE FROM relation_sources WHERE owner_source = ?", (rel_path,))

        # Índice por nombre calificado completo (desambigua entre clases distintas del mismo
        # binario) y, aparte, un CONTEO por nombre corto: si el nombre corto no es único en
        # el binario, una coincidencia por nombre corto es ambigua y se descarta en vez de
        # apuntar arbitrariamente a "el último insertado" (ese era el bug reproducido).
        by_qualified_in_binary: dict[tuple[str, str], str] = {}
        by_short_in_binary: dict[tuple[str, str], list[str]] = {}
        rows = []
        for item in items:
            eid = function_id(item["sha256"], item["address_space"], item["symbol_value"])
            qualified = qualified_name(item["original_name"]) or item["original_name"]
            short = method_name(item["original_name"]) or item["original_name"]
            rows.append((eid, item, qualified, short))
            by_qualified_in_binary[(item["sha256"], qualified)] = eid
            by_short_in_binary.setdefault((item["sha256"], short), []).append(eid)

        for eid, item, _qualified, _short in rows:
            if _upsert_function_entity(
                conn, eid, item["original_name"], item["binary"], item["sha256"],
                item["address_space"], item["symbol_value"], rel_path,
                str(item.get("confidence")), None,
            ):
                n_entities += 1
            for outgoing in item.get("outgoing", []) if isinstance(item.get("outgoing"), list) else []:
                sha = item["sha256"]
                target_qualified = qualified_name(outgoing)
                dst_id = by_qualified_in_binary.get((sha, target_qualified)) if target_qualified else None
                if not dst_id:
                    target_short = method_name(outgoing) or outgoing.split(" ")[0]
                    candidates = by_short_in_binary.get((sha, target_short), [])
                    if len(candidates) != 1:
                        continue  # ambiguo (0 o >1 coincidencias por nombre corto): se descarta
                    dst_id = candidates[0]
                if dst_id == eid:
                    continue
                if _upsert_call_relation(
                    conn, eid, dst_id, "json:name_match_same_binary", rel_path, rel_path,
                    f"{item['original_name']} -> {outgoing} (confidence: {item.get('confidence')})",
                ):
                    n_relations += 1

    ghidra_entities, ghidra_relations = build_ghidra_function_graph(conn, ghidra_files)
    n_entities += ghidra_entities
    n_relations += ghidra_relations
    rea_entities, rea_relations = build_rea_evidence_graph(conn, rea_files)
    n_entities += rea_entities
    n_relations += rea_relations
    # una relación CALLS solo se elimina cuando ningún archivo vivo sigue respaldándola
    # (relation_sources vacío): puede provenir de varias sesiones que reanalizan el mismo
    # binario, igual que ocurre con las entidades Function y entity_sources.
    conn.execute(
        "DELETE FROM relations WHERE type = 'CALLS' AND id NOT IN "
        "(SELECT DISTINCT relation_id FROM relation_sources)"
    )
    return n_entities, n_relations


def detect_status(line: str, window_text: str) -> str:
    """Busca primero en la LÍNEA del marcador (evita atribuir un status que en realidad
    pertenece a una oración vecina dentro de la ventana) y solo si no hay nada ahí, en
    la ventana completa."""
    for text in (line, window_text):
        for token in STATUS_VOCAB:
            if re.search(token, text, re.IGNORECASE):
                return token
    return "NO_VERIFICADO"


def resolve_md_link(doc_path: str, link: str) -> str | None:
    candidate = (ROOT / doc_path).parent / link
    try:
        resolved = candidate.resolve().relative_to(ROOT.resolve())
    except ValueError:
        return None
    return str(resolved) if (ROOT / resolved).exists() else None


WINDOW = 2  # líneas alrededor del marcador de corrección: evita relaciones por proximidad de sección

# Documentos derivados (generados por export_corrections.py u otros exportadores del propio
# grafo): citan "CORRECTS"/enlaces por diseño y contaminarían el grafo con relaciones
# autorreferenciales si se escanean como si fueran hallazgos originales de investigación.
GENERATED_DOCS = {"docs/CORRECTIONS.md", "docs/OPEN-QUESTIONS.md", "docs/INDEX.md"}


def build_correction_graph(conn: sqlite3.Connection) -> int:
    n_relations = 0
    docs_by_path = {row[0] for row in conn.execute("SELECT id FROM documents")}
    docs_by_session: dict[str, list[str]] = {}
    for doc_id in docs_by_path:
        basename = Path(doc_id).name
        m = re.match(r"s(?:ession)?0*(\d+)[-._]", basename, re.IGNORECASE)
        if m:
            docs_by_session.setdefault(m.group(1), []).append(doc_id)

    doc_paths = [row[0] for row in conn.execute("SELECT id FROM documents")
                 if row[0] not in GENERATED_DOCS]
    existing = set(doc_paths) | GENERATED_DOCS  # no son huérfanos; se excluyen, no se borran
    orphan_owners = {
        row[0] for row in conn.execute(
            "SELECT DISTINCT owner_source FROM relations "
            "WHERE extraction_method LIKE 'markdown:keyword+link%'"
        )
    } - existing
    for owner in orphan_owners | GENERATED_DOCS:
        conn.execute("DELETE FROM relations WHERE owner_source = ?", (owner,))

    for doc_id in doc_paths:
        conn.execute(
            "DELETE FROM relations WHERE owner_source = ? AND extraction_method "
            "LIKE 'markdown:keyword+link%'", (doc_id,),
        )
        fpath = ROOT / doc_id
        if not fpath.exists():
            continue
        lines = fpath.read_text(encoding="utf-8", errors="replace").splitlines()

        for i, line in enumerate(lines):
            is_correction = CORRECTION_RE.search(line)
            is_supersede = SUPERSEDE_RE.search(line)
            if not is_correction and not is_supersede:
                continue
            marker = is_supersede or is_correction
            assert marker is not None  # garantizado por el `continue` anterior
            negated = is_negated(line, marker.start())
            rel_type = "SUPERSEDES" if is_supersede else "CORRECTS"
            lo, hi = max(0, i - WINDOW), min(len(lines), i + WINDOW + 1)
            window_text = "\n".join(lines[lo:hi])
            # una mención negada ('no corrige') no es una corrección: nunca se marca
            # VERIFICADO/PARCIAL aunque el texto cercano use ese vocabulario; queda como
            # candidata pendiente de revisión manual, igual que una relación ambigua.
            status = "CONFLICTO_PENDIENTE" if negated else detect_status(line, window_text)

            # same_line: el enlace/referencia está en la MISMA oración que el marcador de
            # corrección -> relación con evidencia directa. window: el enlace solo aparece
            # en una línea vecina (±2) -> candidata, nunca se marca VERIFICADO aunque el
            # texto cercano use esa palabra (proximidad no es demostración).
            same_line_targets: set[str] = set()
            window_only_targets: set[str] = set()
            for link in MD_LINK_RE.findall(line):
                resolved = resolve_md_link(doc_id, link)
                if resolved and resolved != doc_id and resolved not in GENERATED_DOCS:
                    same_line_targets.add(resolved)
            for link in MD_LINK_RE.findall(window_text):
                resolved = resolve_md_link(doc_id, link)
                if resolved and resolved != doc_id and resolved not in GENERATED_DOCS:
                    window_only_targets.add(resolved)
            window_only_targets -= same_line_targets
            for m in SESSION_REF_RE.finditer(line):  # solo la línea del marcador: el encabezado
                                                       # de sección (en la ventana) no es el objetivo
                num = m.group(1) or m.group(2)
                candidates = docs_by_session.get(num, [])
                if len(candidates) <= 2:  # ambigüedad baja; si hay más, no se puede resolver sin adivinar
                    for candidate_doc in candidates:
                        if candidate_doc != doc_id:
                            same_line_targets.add(candidate_doc)

            same_line_method = ("markdown:keyword+link_negated" if negated
                                 else "markdown:keyword+link_or_session_same_line")
            for target, method, row_status in (
                [(t, same_line_method, status) for t in same_line_targets]
                + [(t, "markdown:keyword+link_window_candidate", "CONFLICTO_PENDIENTE")
                   for t in window_only_targets]
            ):
                line_no = i + 1
                rid = relation_id(doc_id, target, rel_type, doc_id, line_no)
                conn.execute(
                    "INSERT OR REPLACE INTO relations (id, src_id, dst_id, type, status, "
                    "extraction_method, owner_source, source_path, line_start, line_end, "
                    "evidence) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                    (rid, doc_id, target, rel_type, row_status, method,
                     doc_id, doc_id, line_no, line_no, window_text[:400]),
                )
                n_relations += 1
    return n_relations


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", default=str(DEFAULT_DB))
    args = ap.parse_args()

    conn = sqlite3.connect(args.db)
    conn.executescript(GRAPH_SCHEMA)
    if conn.execute("SELECT COUNT(*) FROM documents").fetchone()[0] == 0:
        raise SystemExit("La tabla documents está vacía. Ejecuta primero index_docs.py")

    n_func_entities, n_func_relations = build_function_graph(conn)
    n_corr_relations = build_correction_graph(conn)
    conn.commit()

    total_entities = conn.execute("SELECT COUNT(*) FROM entities").fetchone()[0]
    total_relations = conn.execute("SELECT COUNT(*) FROM relations").fetchone()[0]
    conn.close()
    print(f"Funciones: {n_func_entities} entidades, {n_func_relations} relaciones CALLS.")
    print(f"Correcciones: {n_corr_relations} relaciones CORRECTS/SUPERSEDES.")
    print(f"Total grafo: {total_entities} entidades, {total_relations} relaciones. DB: {args.db}")


if __name__ == "__main__":
    main()
