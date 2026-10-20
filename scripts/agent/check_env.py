#!/usr/bin/env python3
"""Comprueba si el repo y la máquina pueden ejecutar una sesión S63 (REA + tests).

Uso:
    python scripts/agent/check_env.py            # resumen legible
    python scripts/agent/check_env.py --json     # salida para agentes
    python scripts/agent/check_env.py --sha      # además verifica SHA-256 del fdat

Códigos: 0 = listo; 1 = falta algo imprescindible (bloquea); 2 = solo avisos.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FDAT = ROOT / "firmware" / "extracted" / "fw321" / "firmware.fdat"
FDAT_SHA = "603b42ec9d2dd66b91e38c15a6a23e860fb8af46a072050903506672036f0f90"
SKILLS = ("contradiction-audit", "knowledge-maintenance", "knowledge-navigation", "session-checkpoint")


def run(*cmd: str, timeout: int = 20) -> str | None:
    if not cmd or not cmd[0]:
        return None
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return (out.stdout + out.stderr).strip().splitlines()[0] if (out.stdout or out.stderr) else ""
    except (OSError, subprocess.SubprocessError):
        return None


def first_line(text: str | None) -> str | None:
    return text.splitlines()[0].strip() if text else None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--sha", action="store_true", help="verifica SHA-256 del firmware.fdat")
    args = ap.parse_args()

    checks: list[dict] = []

    def add(name: str, ok: bool, detail: str, required: bool = True):
        checks.append({"check": name, "ok": ok, "detail": detail, "required": required})

    py = sys.version_info
    add("python>=3.10", py >= (3, 10), f"{py.major}.{py.minor}.{py.micro}")
    add("repo", (ROOT / "AGENTS.md").is_file(), str(ROOT))

    missing = [s for s in SKILLS if not (ROOT / ".agents" / "skills" / s / "SKILL.md").is_file()]
    add("skills .agents", not missing, "faltan: " + ", ".join(missing) if missing else f"{len(SKILLS)} skills")
    missing = [s for s in SKILLS if not (ROOT / ".claude" / "skills" / s / "SKILL.md").is_file()]
    add("skills .claude", not missing, "faltan: " + ", ".join(missing) if missing else f"{len(SKILLS)} skills")

    add("firmware.fdat", FDAT.is_file(), f"{FDAT.stat().st_size} B" if FDAT.is_file() else str(FDAT))
    avcam = ROOT / "firmware" / "extracted" / "fw321" / "firmware.tar_unpacked" / "0700_part_image" / "dev" / "nflasha3_unpacked_unpacked" / "av-cam.bin"
    add("av-cam.bin", avcam.is_file(), f"{avcam.stat().st_size} B" if avcam.is_file() else str(avcam), required=False)

    if args.sha and FDAT.is_file():
        h = hashlib.sha256()
        with FDAT.open("rb") as fh:
            for block in iter(lambda: fh.read(1 << 20), b""):
                h.update(block)
        add("fdat sha256", h.hexdigest() == FDAT_SHA, h.hexdigest())

    git_branch = first_line(run("git", "-C", str(ROOT), "rev-parse", "--abbrev-ref", "HEAD"))
    git_head = first_line(run("git", "-C", str(ROOT), "rev-parse", "--short", "HEAD"))
    add("git", bool(git_branch), f"{git_branch} @ {git_head}" if git_branch else "no es un repo git")

    java_exe = "java.exe" if os.name == "nt" else "java"
    java = shutil.which("java") or (
        str(Path(os.environ["JAVA_HOME"]) / "bin" / java_exe) if os.environ.get("JAVA_HOME") else None
    )
    java_ver = run(java, "-version") if java and Path(java).exists() else None
    add("java 21+", bool(java_ver), java_ver or "no encontrado (exporta JAVA_HOME o pon java en PATH)", required=False)

    ghidra = os.environ.get("GHIDRA_INSTALL_DIR")
    ghidra_ok = bool(ghidra) and (Path(ghidra) / "Ghidra").is_dir()
    add("ghidra 12.1.x", ghidra_ok, ghidra or "define GHIDRA_INSTALL_DIR", required=False)

    node = shutil.which("node")
    add("node", bool(node), run(node, "-v") or "no encontrado", required=False)
    rea = shutil.which("rea") or str(ROOT / "tools" / "rea" / "node_modules" / ".bin" / "rea")
    add("rea cli", Path(rea).exists() or bool(shutil.which("rea")), rea, required=False)

    db = ROOT / ".knowledge-cache" / "knowledge.sqlite"
    add("knowledge db", db.is_file(), f"{db.stat().st_size} B" if db.is_file() else "ejecuta scripts/knowledge/index_docs.py")

    missing_mods = [m for m in ("pytest", "capstone", "unicorn") if not _has_module(m)]
    add("python test deps", not missing_mods, "faltan: " + ", ".join(missing_mods) if missing_mods else "pytest/capstone/unicorn", required=False)

    blocking = [c for c in checks if not c["ok"] and c["required"]]
    warnings = [c for c in checks if not c["ok"] and not c["required"]]

    if args.json:
        print(json.dumps({"root": str(ROOT), "ready": not blocking, "blocking": blocking, "warnings": warnings, "checks": checks}, indent=2, ensure_ascii=False))
    else:
        for c in checks:
            mark = "OK  " if c["ok"] else ("FALLA" if c["required"] else "AVISO")
            print(f"[{mark}] {c['check']}: {c['detail']}")
        print()
        print("LISTO para S63" if not blocking else f"BLOQUEADO: {len(blocking)} requisito(s)")
    return 0 if not blocking else 1


def _has_module(name: str) -> bool:
    import importlib.util

    return importlib.util.find_spec(name) is not None


if __name__ == "__main__":
    raise SystemExit(main())
