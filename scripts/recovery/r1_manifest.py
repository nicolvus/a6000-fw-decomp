"""R1 — manifiesto de copia externa de los archivos críticos de la A6000.

Solo lectura sobre los archivos inventariados. El único archivo que escribe es el manifiesto
que se le pida generar. No toca la cámara, no ejecuta firmware y no modifica ningún binario.

Uso:
  python scripts/recovery/r1_manifest.py manifest [--root DIR] [--inventory FILE] [--out FILE]
  python scripts/recovery/r1_manifest.py verify MANIFEST [--root DIR] [--json]
  python scripts/recovery/r1_manifest.py paths MANIFEST [--all] [--null]

Códigos de salida:
  manifest: 0 si no falta ningún archivo requerido; 1 si falta alguno.
  verify:   0 si todos los archivos del manifiesto coinciden; 1 si falta o no coincide alguno.
  2: error de uso, inventario o manifiesto.

El manifiesto guarda rutas relativas y SHA-256. Para verificar una copia:
  python scripts/recovery/r1_manifest.py verify /media/EXT/r1/manifest.json --root /media/EXT/r1/copia
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from collections.abc import Iterable
from datetime import UTC, datetime
from pathlib import Path, PurePosixPath
from typing import Any

SCHEMA_INVENTORY = "a6000.r1.inventory.v1"
SCHEMA_MANIFEST = "a6000.r1.manifest.v1"
SCHEMA_VERIFY = "a6000.r1.verify.v1"
CHUNK = 1 << 20


class R1Error(Exception):
    """Error de inventario, manifiesto o uso."""


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        while True:
            block = fh.read(CHUNK)
            if not block:
                break
            h.update(block)
    return h.hexdigest()


def _utc_now() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds")


def _safe_rel(value: str) -> str:
    """Normaliza una ruta relativa y rechaza absolutas o escapes del árbol."""
    text = value.replace("\\", "/")
    pure = PurePosixPath(text)
    if pure.is_absolute() or any(part == ".." for part in pure.parts):
        raise R1Error(f"ruta no relativa o con '..': {value!r}")
    normal = str(pure)
    if normal in ("", "."):
        raise R1Error(f"ruta vacía: {value!r}")
    return normal


def _within(root: Path, path: Path) -> bool:
    try:
        return os.path.commonpath([str(root.resolve()), str(path.resolve())]) == str(root.resolve())
    except ValueError:
        return False


def load_inventory(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise R1Error(f"no se puede leer el inventario {path}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise R1Error(f"inventario JSON inválido {path}: {exc}") from exc
    if data.get("schema") != SCHEMA_INVENTORY:
        raise R1Error(f"esquema de inventario inesperado: {data.get('schema')!r}")
    entries = data.get("entries")
    if not isinstance(entries, list) or not entries:
        raise R1Error("el inventario no contiene 'entries'")
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            raise R1Error(f"entrada {index} del inventario no es un objeto")
        if not isinstance(entry.get("role"), str) or not entry["role"]:
            raise R1Error(f"entrada {index} sin 'role'")
        kinds = [key for key in ("path", "paths", "glob") if key in entry]
        if len(kinds) != 1:
            raise R1Error(f"entrada {entry['role']}: debe tener exactamente uno de path/paths/glob")
        if not isinstance(entry.get("required", True), bool):
            raise R1Error(f"entrada {entry['role']}: 'required' debe ser booleano")
    return data


def expand_inventory(
    inventory: dict[str, Any], root: Path, exclude: Path | None = None
) -> list[dict[str, Any]]:
    """Devuelve una lista plana {role, path, required, note} con las rutas concretas."""
    seen: set[str] = set()
    out: list[dict[str, Any]] = []
    excluded = exclude.resolve() if exclude is not None else None

    def add(role: str, value: str, required: bool, note: str | None) -> None:
        rel = _safe_rel(value)
        if rel in seen:
            return
        candidate = root / rel
        if excluded is not None and candidate.resolve() == excluded:
            return
        seen.add(rel)
        out.append({"role": role, "path": rel, "required": required, "note": note})

    for entry in inventory["entries"]:
        role = entry["role"]
        required = bool(entry.get("required", True))
        note = entry.get("note")
        if "path" in entry:
            add(role, entry["path"], required, note)
        elif "paths" in entry:
            paths = entry["paths"]
            if not isinstance(paths, list) or not paths:
                raise R1Error(f"entrada {role}: 'paths' debe ser una lista no vacía")
            for value in paths:
                if not isinstance(value, str):
                    raise R1Error(f"entrada {role}: 'paths' solo admite cadenas")
                add(role, value, required, note)
        else:
            pattern = entry["glob"]
            if not isinstance(pattern, str):
                raise R1Error(f"entrada {role}: 'glob' debe ser una cadena")
            # Path.glob no admite patrones absolutos; el patrón se valida como relativo.
            _safe_rel(pattern)
            matches = sorted(
                (p for p in root.glob(pattern) if p.is_file()),
                key=lambda p: p.as_posix().lower(),
            )
            if not matches:
                add(role, pattern, required, note)
                continue
            for match in matches:
                if not _within(root, match):
                    raise R1Error(f"el glob {pattern!r} sale de la raíz: {match}")
                add(role, match.relative_to(root).as_posix(), required, note)
    return out


def build_manifest(
    entries: Iterable[dict[str, Any]], root: Path, inventory_path: Path
) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    missing_required = 0
    missing_optional = 0
    empty_required = 0
    total_bytes = 0
    by_role: dict[str, dict[str, int]] = {}

    for entry in entries:
        role = entry["role"]
        rel = entry["path"]
        required = entry["required"]
        path = root / rel
        stats = by_role.setdefault(role, {"present": 0, "missing": 0, "bytes": 0})
        if not path.is_file():
            status = "missing"
            stats["missing"] += 1
            if required:
                missing_required += 1
            else:
                missing_optional += 1
            rows.append(
                {
                    "role": role,
                    "path": rel,
                    "required": required,
                    "status": status,
                    "note": entry.get("note"),
                }
            )
            continue

        size = path.stat().st_size
        digest = _sha256(path)
        total_bytes += size
        stats["present"] += 1
        stats["bytes"] += size
        if size == 0 and required:
            empty_required += 1
        rows.append(
            {
                "role": role,
                "path": rel,
                "required": required,
                "status": "present",
                "size": size,
                "sha256": digest,
                "empty": size == 0,
                "note": entry.get("note"),
            }
        )

    return {
        "schema": SCHEMA_MANIFEST,
        "generated_by": "scripts/recovery/r1_manifest.py",
        "created_utc": _utc_now(),
        "source_root": str(root.resolve()),
        "inventory": str(inventory_path),
        "inventory_sha256": _sha256(inventory_path),
        "summary": {
            "entries": len(rows),
            "present": sum(1 for row in rows if row["status"] == "present"),
            "missing_required": missing_required,
            "missing_optional": missing_optional,
            "empty_required": empty_required,
            "bytes": total_bytes,
            "by_role": by_role,
        },
        "entries": rows,
    }


def verify_manifest(manifest: dict[str, Any], root: Path) -> dict[str, Any]:
    if manifest.get("schema") != SCHEMA_MANIFEST:
        raise R1Error(f"esquema de manifiesto inesperado: {manifest.get('schema')!r}")
    entries = manifest.get("entries")
    if not isinstance(entries, list) or not entries:
        raise R1Error("el manifiesto no contiene 'entries'")

    rows: list[dict[str, Any]] = []
    counts = {"ok": 0, "missing": 0, "size_mismatch": 0, "hash_mismatch": 0}
    missing_required = 0
    missing_present = 0

    for entry in entries:
        if not isinstance(entry, dict):
            raise R1Error("entrada de manifiesto inválida")
        role = entry.get("role", "")
        rel = entry.get("path")
        required = bool(entry.get("required", True))
        if not isinstance(rel, str):
            raise R1Error("entrada de manifiesto sin 'path'")
        rel = _safe_rel(rel)
        path = root / rel
        expected_size = entry.get("size")
        expected_hash = entry.get("sha256")

        if entry.get("status") == "missing" or not path.is_file():
            status = "missing"
            counts["missing"] += 1
            # Un archivo que existía al generar el manifiesto debe estar en la copia,
            # sea requerido o opcional. Un opcional ya ausente en el origen no se exige.
            if entry.get("status") == "present":
                missing_present += 1
            if required:
                missing_required += 1
            rows.append(
                {
                    "role": role,
                    "path": rel,
                    "required": required,
                    "status": status,
                    "expected_size": expected_size,
                    "expected_sha256": expected_hash,
                }
            )
            continue

        actual_size = path.stat().st_size
        if not isinstance(expected_size, int) or actual_size != expected_size:
            status = "size_mismatch"
            counts["size_mismatch"] += 1
            rows.append(
                {
                    "role": role,
                    "path": rel,
                    "required": required,
                    "status": status,
                    "expected_size": expected_size,
                    "actual_size": actual_size,
                    "expected_sha256": expected_hash,
                }
            )
            continue

        actual_hash = _sha256(path)
        if not isinstance(expected_hash, str) or actual_hash.lower() != expected_hash.lower():
            status = "hash_mismatch"
            counts["hash_mismatch"] += 1
        else:
            status = "ok"
            counts["ok"] += 1
        rows.append(
            {
                "role": role,
                "path": rel,
                "required": required,
                "status": status,
                "expected_size": expected_size,
                "actual_size": actual_size,
                "expected_sha256": expected_hash,
                "actual_sha256": actual_hash,
            }
        )

    ok = (
        missing_required == 0
        and missing_present == 0
        and counts["size_mismatch"] == 0
        and counts["hash_mismatch"] == 0
    )
    return {
        "schema": SCHEMA_VERIFY,
        "checked_utc": _utc_now(),
        "root": str(root.resolve()),
        "manifest_source_root": manifest.get("source_root"),
        "summary": {
            "entries": len(rows),
            "ok": counts["ok"],
            "missing": counts["missing"],
            "missing_present": missing_present,
            "missing_required": missing_required,
            "size_mismatch": counts["size_mismatch"],
            "hash_mismatch": counts["hash_mismatch"],
        },
        "ok": ok,
        "entries": rows,
    }


def _print_manifest_summary(manifest: dict[str, Any], stream: Any | None = None) -> None:
    stream = sys.stdout if stream is None else stream
    summary = manifest["summary"]
    print(
        "manifest: {entries} archivos, {present} presentes, "
        "{missing_required} requeridos ausentes, {missing_optional} opcionales ausentes, "
        "{empty_required} requeridos vacíos, {bytes} bytes".format(**summary),
        file=stream,
    )
    for role, stats in sorted(summary["by_role"].items()):
        if stats["missing"]:
            print(
                f"  {role}: {stats['present']} presentes, {stats['missing']} ausentes",
                file=stream,
            )


def _print_verify_summary(result: dict[str, Any], stream: Any | None = None) -> None:
    stream = sys.stdout if stream is None else stream
    summary = result["summary"]
    verdict = "OK" if result["ok"] else "FALLO"
    print(
        f"verify: {verdict} — {summary['entries']} archivos, {summary['ok']} correctos, "
        f"{summary['missing']} ausentes ({summary['missing_present']} que estaban en el manifiesto, "
        f"{summary['missing_required']} requeridos), "
        f"{summary['size_mismatch']} tamaños distintos, {summary['hash_mismatch']} hashes distintos",
        file=stream,
    )
    for row in result["entries"]:
        if row["status"] != "ok":
            print(f"  {row['status']}: {row['path']}", file=stream)


def _write_json(payload: dict[str, Any], out: str | None) -> None:
    text = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    if out in (None, "-"):
        sys.stdout.write(text)
        return
    path = Path(out)
    try:
        path.write_text(text, encoding="utf-8")
    except OSError as exc:
        raise R1Error(f"no se puede escribir el manifiesto {path}: {exc}") from exc


def _cmd_manifest(args: argparse.Namespace) -> int:
    root = Path(args.root).resolve()
    inventory_path = Path(args.inventory).resolve()
    inventory = load_inventory(inventory_path)
    out_path = Path(args.out).resolve() if args.out not in (None, "-") else None
    entries = expand_inventory(inventory, root, exclude=out_path)
    manifest = build_manifest(entries, root, inventory_path)
    _write_json(manifest, args.out)
    _print_manifest_summary(manifest, stream=sys.stderr if args.out in (None, "-") else sys.stdout)
    return 0 if manifest["summary"]["missing_required"] == 0 and manifest["summary"]["empty_required"] == 0 else 1


def _load_manifest(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise R1Error(f"no se puede leer el manifiesto {path}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise R1Error(f"manifiesto JSON inválido {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise R1Error("el manifiesto no es un objeto JSON")
    return data


def _cmd_verify(args: argparse.Namespace) -> int:
    manifest = _load_manifest(Path(args.manifest))
    result = verify_manifest(manifest, Path(args.root).resolve())
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        _print_verify_summary(result)
    return 0 if result["ok"] else 1


def _cmd_paths(args: argparse.Namespace) -> int:
    manifest = _load_manifest(Path(args.manifest))
    entries = manifest.get("entries")
    if not isinstance(entries, list):
        raise R1Error("el manifiesto no contiene 'entries'")
    separator = "\0" if args.null else "\n"
    for entry in entries:
        if not isinstance(entry, dict) or not isinstance(entry.get("path"), str):
            continue
        if not args.all and entry.get("status") != "present":
            continue
        sys.stdout.write(_safe_rel(entry["path"]) + separator)
    return 0


def build_parser() -> argparse.ArgumentParser:
    default_root = Path(__file__).resolve().parents[2]
    default_inventory = Path(__file__).resolve().with_name("r1_inventory.json")
    parser = argparse.ArgumentParser(
        description="R1: manifiesto y verificación de la copia externa de archivos críticos."
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_manifest = sub.add_parser("manifest", help="genera el manifiesto SHA-256")
    p_manifest.add_argument("--root", default=str(default_root), help="raíz del árbol a inventariar")
    p_manifest.add_argument("--inventory", default=str(default_inventory), help="JSON de inventario")
    p_manifest.add_argument("--out", default="-", help="archivo de salida ('-' = stdout)")
    p_manifest.set_defaults(func=_cmd_manifest)

    p_verify = sub.add_parser("verify", help="verifica una copia contra el manifiesto")
    p_verify.add_argument("manifest", help="manifiesto JSON")
    p_verify.add_argument("--root", default=".", help="raíz de la copia a verificar")
    p_verify.add_argument("--json", action="store_true", help="salida JSON")
    p_verify.set_defaults(func=_cmd_verify)

    p_paths = sub.add_parser("paths", help="lista las rutas del manifiesto (para rsync/cp)")
    p_paths.add_argument("manifest", help="manifiesto JSON")
    p_paths.add_argument("--all", action="store_true", help="incluye también las ausentes")
    p_paths.add_argument("--null", action="store_true", help="separa con NUL (rsync --from0)")
    p_paths.set_defaults(func=_cmd_paths)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.func(args))
    except R1Error as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
