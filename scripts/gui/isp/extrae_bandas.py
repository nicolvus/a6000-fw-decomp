#!/usr/bin/env python3
"""T9 — recoge la atenuación MEDIDA por bandas verticales de EFCS (`on_off_bandas`) y Silent (`silent_off_bandas`) frente al obturador mecánico, por velocidad.
Fuente: `~/Desktop/16161111/r87*/medidas.json` (fotos del usuario, no versionadas; script `e26_r85_calibrar_fotos.py`, informe `docs/capture/e26-r85-*.md`).
Cada valor es un cociente de exposición (>1 = más luz que el mecánico) en 8 bandas arriba→abajo; None = banda sin medida (saturada o sin señal).
Una velocidad medida en varias tandas se guarda por tanda (la tabla EFCS de la cámara cambió entre tandas: NO se promedia). Salida: analysis/gui/isp/obturador_bandas.json.
Uso: extrae_bandas.py [carpeta]"""
import json
import math
import sys
from pathlib import Path

D = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.home() / "Desktop/16161111"
OUT = Path(__file__).resolve().parents[3] / "analysis/gui/isp/obturador_bandas.json"
limpia = lambda v: None if v is None or (isinstance(v, float) and math.isnan(v)) else round(float(v), 3)
filas = []
for f in sorted(D.glob("r87*/medidas.json")):
    for e in json.loads(f.read_text()):
        on, si = [limpia(v) for v in e["on_off_bandas"]], [limpia(v) for v in e["silent_off_bandas"]]
        if any(v is not None for v in on) or any(v is not None for v in si):
            filas.append({"tanda": f.parent.name, "fotos": e["fotos"], "velocidad": e["velocidad"], "t_darwin_us": e["t_darwin_us"], "efcs_mec_bandas": on, "silent_mec_bandas": si,
                          "efcs_mec_global": limpia(e.get("on_off")), "silent_ms": limpia(e.get("silent_ms")), "silent_saturado": limpia(e.get("silent_saturado"))})
OUT.write_text(json.dumps({"fuente": "r87*/medidas.json (MEDIDO, fotos del usuario)", "filas": filas}, indent=1))
print(len(filas), "filas ->", OUT)
