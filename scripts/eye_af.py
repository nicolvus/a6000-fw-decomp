#!/usr/bin/env python3
"""Eye AF en tiempo real en la Sony A6000 (lanzador).

Uso: scripts/eye_af.py --host 192.168.1.29 --check
     scripts/eye_af.py --host 192.168.1.29 --preview --focus-mode AF-C

Requiere la app Smart Remote Control abierta en la cámara. Detalle y API:
tools/eye-af/README.md y docs/capture/eye-af-tiempo-real.md.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools" / "eye-af"))

from eyeaf.__main__ import main

if __name__ == "__main__":
    raise SystemExit(main())
