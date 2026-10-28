#!/usr/bin/env python3
"""G01 — Inventario reproducible del subsistema de interfaz gráfica (A6000 fw3.21).

No interpreta: solo mide y clasifica artefactos del userland Linux que participan
en la GUI. La evidencia interpretada está en docs/gui/.

Uso:
    .venv/bin/python scripts/gui/inventory.py [--root RUTA] [--out RUTA.json]

Por defecto root = firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/
nflasha15_unpacked_unpacked (partición /usr de la cámara), out = analysis/gui/g01-inventory.json.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
DEFAULT_ROOT = (
    REPO
    / "firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev"
    / "nflasha15_unpacked_unpacked"
)

# Bibliotecas con evidencia de participar en la GUI (nombres del firmware, no inventados).
GUI_LIBS = [
    "libObj.so",
    "viewUnified2.so",
    "viewUnified3.so",
    "viewUnified4.so",
    "viewUnified5.so",
    "viewUnified6.so",
    "viewUnified7.so",
    "viewUnified8.so",
    "cmn_menuTableUtil.so",
    "cmnviewViewModel.so",
    "cmn_view_processDataMgr.so",
    "cmnviewMRUtil.so",
    "CmnShootingInfoLayoutMgr.so",
    "CmnViewIroiroConDataMgr.so",
    "cmnFnWrapper.so",
    "zakoMenuUtil.so",
    "libScalarDaemon.so",
    "libmintx.so",
]

# Namespaces/clases que identifican capas de la GUI (prefijos mangled).
LAYER_PATTERNS = {
    "ux::gfxeng": r"^_ZN2ux6gfxeng",
    "ux::core": r"^_ZN2ux4core",
    "ux::resmgr": r"^_ZN2ux6resmgr",
    "ux::wgtlay": r"^_ZN2ux6wgtlay",
    "ux::animeng": r"^_ZN2ux7animeng",
    "GEN_widgets": r"^_ZN3GEN",
    "ViewBase": r"^_ZN8ViewBase",
    "DefRootView": r"^_ZN11DefRootView",
    "AppWidgetBase": r"^_ZN14AppWidgetBase",
    "LayoutableWidgetBase": r"^_ZN20LayoutableWidgetBase",
    "CmnViewMenuData": r"^_ZN15CmnViewMenuData",
    "CmnMenuTableUtil": r"^_ZN16CmnMenuTableUtil",
    "HighlightManager": r"^_ZN16HighlightManager",
    "SequenceBase": r"^_ZN12SequenceBase",
    "InputService": r"^_ZN12InputService",
    "GlobalAccessor": r"^_ZN14GlobalAccessor",
    "ScalarView": r"^_ZN10ScalarView",
    "MprIf": r"^_ZN5MprIf",
    "MWF": r"^_ZN3MWF",
    "UFW": r"^_ZN3UFW",
    "stella": r"^_ZN6stella",
}

RESOURCE_MAGIC = {b"uxc": "uxc", b"uxb": "uxb", b"uxa": "uxa", b"uxx": "uxx"}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def run(cmd: list[str]) -> str:
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=600, check=False)
        return out.stdout
    except (OSError, subprocess.TimeoutExpired) as exc:  # pragma: no cover
        return f"ERROR: {exc}"


def elf_info(path: Path) -> dict:
    dyn = run(["nm", "-D", "--defined-only", str(path)])
    names = [line.split()[-1] for line in dyn.splitlines() if len(line.split()) >= 3]
    layers = Counter()
    for name in names:
        for layer, pat in LAYER_PATTERNS.items():
            if re.match(pat, name):
                layers[layer] += 1
    needed = re.findall(
        r"\(NEEDED\)\s+.*?\[(.+?)\]", run(["readelf", "-d", str(path)])
    )
    return {
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
        "dyn_defined_symbols": len(names),
        "layers": dict(sorted(layers.items())),
        "needed": needed,
    }


def gui_strings(path: Path, limit: int = 40) -> list[str]:
    """Cadenas que apuntan a dispositivos/recursos de la GUI (evidencia de rol)."""
    raw = path.read_bytes()
    pattern = re.compile(
        rb"[\x20-\x7e]{4,}"
    )
    hits = set()
    for m in pattern.finditer(raw):
        s = m.group().decode("ascii", "ignore")
        if re.search(r"/dev/fb\d|\.uxc|\.uxb|\.uxa|/usr/share/app|framebuffer|uxc|LayoutConveter|SurfaceFlinger", s):
            hits.add(s[:160])
    return sorted(hits)[:limit]


def resource_summary(appdir: Path) -> dict:
    files = sorted(p for p in appdir.iterdir() if p.is_file())
    by_prefix: dict[str, list[str]] = defaultdict(list)
    entries = []
    for p in files:
        head = p.read_bytes()[:16]
        magic = RESOURCE_MAGIC.get(head[:3], head[:4].decode("latin-1"))
        prefix = re.split(r"[._]", p.name)[0]
        by_prefix[prefix].append(p.name)
        entries.append(
            {
                "name": p.name,
                "bytes": p.stat().st_size,
                "magic": magic,
                "header_hex": head.hex(),
                "sha256": sha256(p) if p.stat().st_size < (32 << 20) else None,
            }
        )
    return {
        "files": len(files),
        "total_bytes": sum(e["bytes"] for e in entries),
        "prefixes": {k: len(v) for k, v in sorted(by_prefix.items())},
        "entries": entries,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=str(DEFAULT_ROOT))
    ap.add_argument("--out", default=str(REPO / "analysis/gui/g01-inventory.json"))
    args = ap.parse_args()

    root = Path(args.root)
    if not root.is_dir():
        print(f"no existe {root}", file=sys.stderr)
        return 2

    libdir = root / "lib"
    appdir = root / "share/app"
    report = {
        "generated_by": "scripts/gui/inventory.py",
        "root": str(root.relative_to(REPO)) if str(root).startswith(str(REPO)) else str(root),
        "libs": {},
        "resources": {},
        "startup_candidates": {},
    }

    for name in GUI_LIBS:
        p = libdir / name
        if not p.exists():
            report["libs"][name] = {"missing": True}
            continue
        info = elf_info(p)
        info["gui_strings"] = gui_strings(p)
        report["libs"][name] = info

    if appdir.is_dir():
        report["resources"] = resource_summary(appdir)

    # Scripts de arranque disponibles en la partición /usr (evidencia de quién lanza el userland).
    startup = {}
    for cand in sorted((root / "bin").glob("*.sh")):
        startup[cand.name] = cand.read_text(errors="replace")[:4000]
    report["startup_candidates"] = startup

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=1, ensure_ascii=False))
    print(f"escrito {out} ({out.stat().st_size} B)")
    for name, info in report["libs"].items():
        if info.get("missing"):
            print(f"  FALTA {name}")
        else:
            print(f"  {name:32s} {info['bytes']:>10d} B  syms={info['dyn_defined_symbols']:>5d}  {info['layers']}")
    res = report["resources"]
    if res:
        print(f"  recursos share/app: {res['files']} ficheros, {res['total_bytes']} B, prefijos={res['prefixes']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
