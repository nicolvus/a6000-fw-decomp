"""E25-04/R1 — pruebas del manifiesto de copia externa.

Solo usan directorios temporales; no leen firmware ni tocan la cámara. Verifican que el
manifiesto detecta archivos ausentes y copias alteradas, y que la verificación no modifica
los archivos. Informe: docs/capture/e25-04-recuperabilidad-y-decision.md
"""
from __future__ import annotations

import hashlib
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "scripts" / "recovery")]

import r1_manifest as R


def _write_inventory(path: Path, entries: list[dict]) -> Path:
    path.write_text(
        json.dumps({"schema": R.SCHEMA_INVENTORY, "entries": entries}, ensure_ascii=False),
        encoding="utf-8",
    )
    return path


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def test_manifest_and_verify_roundtrip(tmp_path, capsys):
    root = tmp_path / "src"
    (root / "sub").mkdir(parents=True)
    (root / "a.bin").write_bytes(b"alpha")
    (root / "sub" / "b.bin").write_bytes(b"beta")
    (root / "optional.txt").write_bytes(b"opt")
    inventory = _write_inventory(
        tmp_path / "inventory.json",
        [
            {"role": "a", "path": "a.bin", "required": True},
            {"role": "b", "glob": "sub/*.bin", "required": True},
            {"role": "opt", "path": "optional.txt", "required": False},
        ],
    )
    manifest_path = tmp_path / "manifest.json"

    assert R.main(["manifest", "--root", str(root), "--inventory", str(inventory), "--out", str(manifest_path)]) == 0
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["schema"] == R.SCHEMA_MANIFEST
    assert manifest["summary"]["entries"] == 3
    assert manifest["summary"]["present"] == 3
    assert manifest["summary"]["missing_required"] == 0
    by_path = {row["path"]: row for row in manifest["entries"]}
    assert by_path["a.bin"]["sha256"] == _sha(b"alpha")
    assert by_path["sub/b.bin"]["sha256"] == _sha(b"beta")
    assert by_path["optional.txt"]["required"] is False

    copy = tmp_path / "copy"
    shutil.copytree(root, copy)
    before = {p: p.stat().st_mtime_ns for p in copy.rglob("*") if p.is_file()}
    capsys.readouterr()
    assert R.main(["verify", str(manifest_path), "--root", str(copy)]) == 0
    after = {p: p.stat().st_mtime_ns for p in copy.rglob("*") if p.is_file()}
    assert before == after, "verify no debe modificar la copia"
    assert "OK" in capsys.readouterr().out


def test_verify_detects_missing_and_hash_mismatch(tmp_path, capsys):
    root = tmp_path / "src"
    root.mkdir()
    (root / "a.bin").write_bytes(b"alpha")
    (root / "b.bin").write_bytes(b"beta")
    (root / "opt.bin").write_bytes(b"opt")
    inventory = _write_inventory(
        tmp_path / "inventory.json",
        [
            {"role": "a", "path": "a.bin", "required": True},
            {"role": "b", "path": "b.bin", "required": True},
            {"role": "opt", "path": "opt.bin", "required": False},
        ],
    )
    manifest_path = tmp_path / "manifest.json"
    assert R.main(["manifest", "--root", str(root), "--inventory", str(inventory), "--out", str(manifest_path)]) == 0

    copy = tmp_path / "copy"
    shutil.copytree(root, copy)
    (copy / "b.bin").unlink()
    (copy / "a.bin").write_bytes(b"ALPHA")
    (copy / "opt.bin").unlink()  # opcional, pero presente en el manifiesto: debe exigirse en la copia
    capsys.readouterr()
    assert R.main(["verify", str(manifest_path), "--root", str(copy)]) == 1
    out = capsys.readouterr().out
    assert "FALLO" in out
    assert "missing: b.bin" in out
    assert "missing: opt.bin" in out
    assert "2 que estaban en el manifiesto" in out
    assert "size_mismatch: a.bin" in out or "hash_mismatch: a.bin" in out


def test_manifest_flags_missing_required_and_optional(tmp_path):
    root = tmp_path / "src"
    root.mkdir()
    (root / "present.bin").write_bytes(b"x")
    inventory = _write_inventory(
        tmp_path / "inventory.json",
        [
            {"role": "ok", "path": "present.bin", "required": True},
            {"role": "req", "path": "missing.bin", "required": True},
            {"role": "opt", "path": "also-missing.bin", "required": False},
        ],
    )
    manifest_path = tmp_path / "manifest.json"
    assert R.main(["manifest", "--root", str(root), "--inventory", str(inventory), "--out", str(manifest_path)]) == 1
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["summary"]["missing_required"] == 1
    assert manifest["summary"]["missing_optional"] == 1
    assert manifest["summary"]["present"] == 1

    assert R.main(["verify", str(manifest_path), "--root", str(root)]) == 1


def test_paths_skips_missing_and_supports_null(tmp_path, capsys):
    manifest = {
        "schema": R.SCHEMA_MANIFEST,
        "entries": [
            {"role": "a", "path": "a.bin", "required": True, "status": "present", "size": 1, "sha256": "00"},
            {"role": "b", "path": "b.bin", "required": False, "status": "missing"},
        ],
    }
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps(manifest), encoding="utf-8")
    assert R.main(["paths", str(path)]) == 0
    assert capsys.readouterr().out == "a.bin\n"
    assert R.main(["paths", str(path), "--all", "--null"]) == 0
    assert capsys.readouterr().out == "a.bin\0b.bin\0"


def test_inventory_rejects_escape(tmp_path):
    inventory = _write_inventory(
        tmp_path / "inventory.json",
        [{"role": "bad", "path": "../secret.bin", "required": True}],
    )
    assert R.main(["manifest", "--root", str(tmp_path), "--inventory", str(inventory), "--out", "-"]) == 2


def test_inventory_real_es_valido():
    inventory = R.load_inventory(ROOT / "scripts" / "recovery" / "r1_inventory.json")
    roles = {entry["role"] for entry in inventory["entries"]}
    assert {
        "nvram_referencia",
        "nand_logica",
        "firmware_original",
        "fdat_recuperacion_323",
        "candidato_b1a",
    } <= roles
