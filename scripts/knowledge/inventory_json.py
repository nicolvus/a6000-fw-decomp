#!/usr/bin/env python3
"""Inventariador determinista de JSON bajo analysis/ (Fase 12.4.A).

No lee cada archivo con el contexto del LLM: agrupa por FIRMA ESTRUCTURAL (forma de
claves + tipos, no contenido) y escribe un catálogo reproducible. Una firma igual no
implica equivalencia SEMÁNTICA — dos formatos pueden compartir claves por coincidencia
(p. ej. "address") y significar cosas distintas; el catálogo solo agrupa por forma,
la interpretación semántica de cada familia es manual y se documenta aparte.

Uso: python3 scripts/knowledge/inventory_json.py [--dir analysis] [--out knowledge/catalog]
"""

import argparse
import hashlib
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

from _paths import find_root

ROOT = find_root()

# claves cuya presencia sugiere evidencia técnica aprovechable para un extractor de grafo
EVIDENCE_HINTS = {
    "address", "addr", "symbol", "symbol_value", "original_name", "outgoing", "incoming",
    "callers", "callees", "xref", "xrefs", "register", "registers", "pin", "pins", "gpio",
    "queue", "queues", "message", "messages", "callback", "callbacks", "mode", "modes",
    "sensor", "sha256", "binary", "instruction_address", "vtable", "dispatcher",
}


def sha256_of(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _scalar_type(v: Any) -> str:
    if v is None:
        return "null"
    if isinstance(v, bool):
        return "bool"
    if isinstance(v, int):
        return "int"
    if isinstance(v, float):
        return "float"
    if isinstance(v, str):
        return "str"
    if isinstance(v, list):
        return "list"
    if isinstance(v, dict):
        return "dict"
    return type(v).__name__


def _dict_key_types(d: dict) -> dict[str, str]:
    return {k: _scalar_type(v) for k, v in d.items()}


def classify(data: Any, sample_cap: int = 50) -> dict:
    """Devuelve {shape, keys, key_types, homogeneous, item_count} describiendo la FORMA
    estructural de `data`, sin interpretar su significado."""
    if isinstance(data, dict):
        if not data:
            return {"shape": "empty_dict", "keys": [], "key_types": {}, "item_count": 0}
        return {
            "shape": "dict",
            "keys": sorted(data.keys()),
            "key_types": _dict_key_types(data),
            "item_count": 1,
        }
    if isinstance(data, list):
        if not data:
            return {"shape": "empty_list", "keys": [], "key_types": {}, "item_count": 0}
        sample = data[:sample_cap]
        if all(isinstance(x, dict) for x in sample):
            key_sets = [frozenset(x.keys()) for x in sample]
            union: set = set()
            for ks in key_sets:
                union |= ks
            homogeneous = len(set(key_sets)) == 1
            key_types: dict[str, set[str]] = defaultdict(set)
            for item in sample:
                for k, v in item.items():
                    key_types[k].add(_scalar_type(v))
            return {
                "shape": "list_of_dict" if homogeneous else "list_of_dict_variant",
                "keys": sorted(union),
                "key_types": {k: sorted(v) for k, v in key_types.items()},
                "item_count": len(data),
            }
        scalar_types = sorted({_scalar_type(x) for x in sample})
        return {
            "shape": "list_of_scalar",
            "keys": [],
            "key_types": {"_items": scalar_types},
            "item_count": len(data),
        }
    return {"shape": f"scalar_{_scalar_type(data)}", "keys": [], "key_types": {}, "item_count": 1}


def signature_of(info: dict) -> str:
    """Clave de agrupación: forma + claves ordenadas. Dos archivos con la MISMA firma
    quedan en la misma familia; firmas distintas aunque compartan algunas claves no."""
    return f"{info['shape']}::{','.join(info['keys'])}"


def has_evidence_hint(keys: list[str]) -> bool:
    return bool(EVIDENCE_HINTS & {k.lower() for k in keys})


def scan(base: Path) -> tuple[list[dict[str, Any]], dict]:
    files: list[dict[str, Any]] = []
    families: dict[str, dict] = {}
    for path in sorted(base.rglob("*.json")):
        rel = str(path.relative_to(ROOT))
        try:
            raw = path.read_bytes()
        except OSError as exc:
            files.append({"path": rel, "error": f"no_leible: {exc}"})
            continue
        size = len(raw)
        digest = hashlib.sha256(raw).hexdigest()
        try:
            data = json.loads(raw.decode("utf-8", errors="strict"))
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            files.append({"path": rel, "size": size, "sha256": digest,
                          "error": f"json_invalido: {exc}"})
            continue
        info = classify(data)
        sig = signature_of(info)
        files.append({
            "path": rel, "size": size, "sha256": digest, "shape": info["shape"],
            "item_count": info["item_count"], "signature": sig,
        })
        fam = families.setdefault(sig, {
            "signature": sig, "shape": info["shape"], "keys": info["keys"],
            "key_types": info["key_types"], "count": 0, "total_size": 0,
            "sample_paths": [], "has_evidence_hint": has_evidence_hint(info["keys"]),
        })
        fam["count"] += 1
        fam["total_size"] += size
        if len(fam["sample_paths"]) < 3:
            fam["sample_paths"].append(rel)
    return files, families


def write_catalog(files: list[dict[str, Any]], families: dict, out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "json_inventory.json").write_text(
        json.dumps({"files": files, "families": families}, ensure_ascii=False, indent=1),
        encoding="utf-8",
    )

    invalid = [f for f in files if "error" in f]
    empty = [f for f in files if f.get("shape", "").startswith("empty")]
    by_count = sorted(families.values(), key=lambda f: -f["count"])

    lines = [
        "# Catálogo de formatos JSON bajo analysis/ (generado, no editar a mano)",
        "",
        f"Total archivos: {len(files)}. Familias (firmas estructurales) distintas: {len(families)}.",
        f"Inválidos/no legibles: {len(invalid)}. Vacíos: {len(empty)}.",
        "",
        ("Una firma agrupa por FORMA (claves+tipos), no por significado: dos familias con "
         "claves parecidas pueden representar cosas distintas; revisar `sample_paths` antes "
         "de asumir equivalencia semántica."),
        "",
        "## Familias por tamaño (archivos), con pista de evidencia técnica aprovechable",
        "",
        "| # archivos | tamaño total | con pista evidencia | forma | claves | ejemplo |",
        "|---|---|---|---|---|---|",
    ]
    for fam in by_count:
        keys_preview = ", ".join(fam["keys"][:12]) + (" …" if len(fam["keys"]) > 12 else "")
        lines.append(
            f"| {fam['count']} | {fam['total_size']} | "
            f"{'SÍ' if fam['has_evidence_hint'] else 'no'} | {fam['shape']} | "
            f"{keys_preview or '(sin claves)'} | `{fam['sample_paths'][0] if fam['sample_paths'] else '-'}` |"
        )

    if invalid:
        lines += ["", "## Archivos inválidos o no legibles", ""]
        for f in invalid[:50]:
            lines.append(f"- `{f['path']}`: {f['error']}")
        if len(invalid) > 50:
            lines.append(f"- … y {len(invalid) - 50} más (ver json_inventory.json)")

    (out_dir / "JSON-CATALOG.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default="analysis")
    ap.add_argument("--out", default="knowledge/catalog")
    args = ap.parse_args()

    base = ROOT / args.dir
    if not base.exists():
        raise SystemExit(f"No existe {base}")
    files, families = scan(base)
    write_catalog(files, families, ROOT / args.out)
    print(f"{len(files)} archivos, {len(families)} familias. "
          f"Catálogo: {args.out}/JSON-CATALOG.md y {args.out}/json_inventory.json")


if __name__ == "__main__":
    main()
