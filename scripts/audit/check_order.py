#!/usr/bin/env python3
"""Comprueba mecánicamente las reglas de ORDEN.md (orden del repositorio).

Uso: python scripts/audit/check_order.py [-v]
Salida 0 si todo cumple; 1 con la lista de incumplimientos.
"""
from __future__ import annotations

import re
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OBLIGATORIOS = [
    "README.md", "README.en.md", "CONTRIBUTING.md", "CONTRIBUTING.en.md",
    "ORDEN.md", "ORDER.md", "FUNCIONES.md", "LICENSE", "AGENTS.md",
]
DOCS_PORTADA = ["README.md", "README.en.md", "ORDEN.md", "ORDER.md", "CONTRIBUTING.md", "CONTRIBUTING.en.md"]


def word(slug: str) -> str:
    """Sin acentos ni mayúsculas, para comparar slug y nombre de fichero."""
    plano = unicodedata.normalize("NFKD", slug).encode("ascii", "ignore").decode()
    return plano.lower()


def chequeos() -> list[str]:
    fallos: list[str] = []

    # 1. Ficheros raíz obligatorios
    fallos += [f"falta {f}" for f in OBLIGATORIOS if not (ROOT / f).exists()]

    # 2. Wiki: cada página tiene gemela en el otro idioma con el mismo número
    wiki = sorted(p for p in (ROOT / "wiki").glob("*.md") if p.name != "_Sidebar.md")
    for p in wiki:
        en = p.name.startswith("en-")
        num = re.match(r"(\d+)-", p.name[3:] if en else p.name)
        if not num:  # Home / en-Home
            gemela = ROOT / "wiki" / (p.name.removeprefix("en-") if en else f"en-{p.name}")
            if not gemela.exists():
                fallos.append(f"wiki/{p.name} sin gemela wiki/{gemela.name}")
            continue
        hermanas = [q for q in wiki if q.name != p.name and
                    q.name.removeprefix("en-").split("-")[0] == num.group(1) and
                    q.name.startswith("en-") != en]
        if not hermanas:
            fallos.append(f"wiki/{p.name} sin gemela del número {num.group(1)} en el otro idioma")

    # 3. _Sidebar lista todas las páginas en los dos bloques
    sidebar = (ROOT / "wiki" / "_Sidebar.md").read_text(encoding="utf-8")
    for p in wiki:
        if f"/wiki/{p.stem})" not in sidebar:
            fallos.append(f"wiki/_Sidebar.md no enlaza {p.stem}")

    # 4. Sin enlaces a releases (el repositorio no tiene releases)
    for p in [ROOT / f for f in OBLIGATORIOS if f.endswith(".md")] + wiki:
        texto = p.read_text(encoding="utf-8")
        for destino in re.findall(r"\]\(([^)\s]+)\)", texto):
            if "/releases/tag/" in destino:
                fallos.append(f"{p.relative_to(ROOT)}: enlace a releases/tag (no hay releases)")

    # 5. Enlaces relativos de las portadas resuelven
    for f in DOCS_PORTADA:
        p = ROOT / f
        if not p.exists():
            continue
        for destino in re.findall(r"\]\(([^)\s]+)\)", p.read_text(encoding="utf-8")):
            if destino.startswith(("http://", "https://", "#", "mailto:")):
                continue
            if not (ROOT / destino.split("#")[0]).exists():
                fallos.append(f"{f}: enlace relativo roto -> {destino}")

    # 6. Enlaces a páginas de la wiki resuelven a un fichero de wiki/
    for p in [ROOT / f for f in OBLIGATORIOS if f.endswith(".md")] + wiki:
        for slug in re.findall(r"/wiki/([A-Za-z0-9._-]+)", p.read_text(encoding="utf-8")):
            if not (ROOT / "wiki" / f"{slug}.md").exists():
                fallos.append(f"{p.relative_to(ROOT)}: enlace a wiki/{slug} sin página")

    # 7. Portada del sitio: par ES/EN con enlace cruzado
    es, en = ROOT / "site" / "index.html", ROOT / "site" / "en" / "index.html"
    if es.exists() != en.exists():
        fallos.append("site/: la portada debe tener par ES (site/index.html) y EN (site/en/index.html)")
    elif es.exists():
        if 'href="en/"' not in es.read_text(encoding="utf-8"):
            fallos.append("site/index.html: falta el enlace a la versión inglesa (en/)")
        if 'href="../"' not in en.read_text(encoding="utf-8"):
            fallos.append("site/en/index.html: falta el enlace a la versión española (../)")

    # 8. Nombres de docs/capture y reports sin espacios ni acentos
    for sub in ("docs/capture", "reports"):
        for p in sorted((ROOT / sub).glob("*.md")):
            if not p.stem.isascii():
                fallos.append(f"{sub}/{p.name}: nombre con acentos")
            if " " in p.name:
                fallos.append(f"{sub}/{p.name}: nombre con espacios")
    return fallos


def main() -> int:
    fallos = chequeos()
    if not fallos:
        print("ORDEN: todo cumple")
        return 0
    print(f"ORDEN: {len(fallos)} incumplimiento(s)")
    for f in fallos:
        print(f"  - {f}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
