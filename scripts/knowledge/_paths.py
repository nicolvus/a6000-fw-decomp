"""Resuelve la raíz del proyecto, con esta prioridad:

1. Variable de entorno SONY_A6000_KB_ROOT (override explícito), validada.
2. Marcador CLAUDE.md ascendiendo desde `start` (o Path.cwd()).
3. Marcador CLAUDE.md ascendiendo desde la ubicación de instalación de este propio
   script (scripts/knowledge/_paths.py): corrige el bug reproducido de la auditoría
   ("ejecutar el indexador desde /tmp produjo cero documentos") cuando se invoca el
   script por ruta absoluta desde un directorio ajeno al proyecto.
4. `start` (o Path.cwd()) sin resolver: último recurso para fixtures de test que
   simulan un proyecto propio SIN CLAUDE.md real (deben crear uno si quieren
   comportarse como el proyecto real; ver tests/knowledge/*).

La validación de SONY_A6000_KB_ROOT exige el marcador CLAUDE.md en esa ruta exacta
(evita apuntar por error a un directorio sin relación con ningún proyecto)."""

import os
from pathlib import Path

_MARKER = "CLAUDE.md"
_SELF = Path(__file__).resolve()


def _search_ancestors(start: Path) -> Path | None:
    for candidate in (start, *start.parents):
        if (candidate / _MARKER).exists():
            return candidate
    return None


def find_root(start: Path | None = None) -> Path:
    env = os.environ.get("SONY_A6000_KB_ROOT")
    if env:
        candidate = Path(env).resolve()
        if not (candidate / _MARKER).exists():
            raise SystemExit(f"SONY_A6000_KB_ROOT={candidate} no contiene {_MARKER}")
        return candidate

    here = (start or Path.cwd()).resolve()
    return _search_ancestors(here) or _search_ancestors(_SELF.parent) or here
